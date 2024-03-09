import base64
import io
import sys

import cv2
from langchain.globals import set_debug
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.llms.ollama import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from text_to_speech import TextToSpeech
from video_analysis import VideoAnalysis

store = {}
text_to_speech = TextToSpeech()

set_debug(True)


def convert_image_to_b64(image):
    success, encoded_image = cv2.imencode('.png', image)
    buffered = io.BytesIO(encoded_image)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def add_session_message(session_id: str, message) -> None:
    session_history = get_session_history(session_id)
    session_history.add_message(message)


def process(image_grid):
    llm_cabin = Ollama(model="mistral-cabin-assistant")
    llm_json_directive = Ollama(model="direction-assistant-extractor")
    llm_llava = Ollama(model="llava-picture-descriptor")

    image_b64 = convert_image_to_b64(image_grid)

    # prompt1 = ChatPromptTemplate.from_messages(
    #     [
    #         MessagesPlaceholder(variable_name="history"),
    #         ("system", "{input}"),
    #     ]
    # )
    llava_n_ctx = llm_llava.bind(images=[image_b64])
    output_parser = StrOutputParser()

    # chain1 = prompt1 | llava_n_ctx | llm_cabin | output_parser
    chain1 = llava_n_ctx | llm_cabin | output_parser
    

    # chain1_w_msg_hist = RunnableWithMessageHistory(
    #     chain1,
    #     get_session_history,
    #     input_messages_key="input",
    #     history_messages_key="history",
    # )
    # response1 = chain1_w_msg_hist.invoke({"input": "Describe the image."},
    #                                      config={"configurable": {"session_id": "test"}})
    response1 = chain1.invoke("Describe the image.")

    prompt2 = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="history"),
            ("system", "{input}"),
        ]
    )
    chain2 = prompt2 | llm_json_directive | output_parser

    chain2_w_msg_hist = RunnableWithMessageHistory(
        chain2,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    response2 = chain2_w_msg_hist.invoke({"input": response1},
                                         config={"configurable": {"session_id": "test"}})

    summary = text_to_speech.summarize(response2)
    text_to_speech.synthesize(summary)

    add_session_message('test', response1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception(f"Wrong arguments. Aborting.")

    va = VideoAnalysis(video_path=sys.argv[1])
    #va = VideoAnalysis(test_img_path='test_stuff/grid_test.jpg')
    va.add_observer(process)
    va.run_forever()
