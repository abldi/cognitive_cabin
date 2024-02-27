import base64
import io
from datetime import datetime

import cv2
from langchain_community.llms.ollama import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from video_analysis import VideoAnalysis

llm_mistral = Ollama(model="mistral")
llm_mistral_cabin = Ollama(model="mistral-cabin-assistant")
llm_llama2_cabin = Ollama(model="llama2-cabin-assistant")
llm_llava = Ollama(model="llava")


def convert_image_to_b64(image):
    success, encoded_image = cv2.imencode('.png', image)
    buffered = io.BytesIO(encoded_image)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def process(image_grid):
    image_b64 = convert_image_to_b64(image_grid)
    llava_n_ctx = llm_llava.bind(images=[image_b64])

    prompt = ChatPromptTemplate.from_template("Describe the scene in the collage.")
    output_parser = StrOutputParser()

    chain = (
            {'topic': RunnablePassthrough()}
            | prompt
            | llava_n_ctx
            | llm_mistral_cabin
            | llm_llama2_cabin
            | output_parser
    )
    rst = chain.invoke('')
    return


    try:
        image_content_array = []

        for image in image_array:
            success, encoded_image = cv2.imencode('.jpg', image)
            image_bytes = encoded_image.tobytes()
            b64encoded = base64.b64encode(image_bytes)
            image_content = b64encoded.decode('utf-8')
            image_content_array.append(image_content)

        send_time = datetime.now()
        response = llm_llava.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': 'Describe the picture.',
                'images': image_content_array
            }])
        print(f"R1 took {(datetime.now() - send_time).total_seconds()} seconds")
        print("R1:" + response['message']['content'])

        cabin_prompt = "Here is a description of the current scene, viewed from a realtime camera : "

        content2 = cabin_prompt + ' ' + response['message']['content']
        send_time = datetime.now()
        response2 = llm_mistral_cabin.chat(
            model='cabin-assistant',
            messages=[{
                'role': 'user',
                'content': content2
            }])
        print(f"\n--------------------\n"
              f"R2 took {(datetime.now() - send_time).total_seconds()} seconds")
        print("R2:" + response2['message']['content'])
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # process([cv2.imread('/home/tamaya/Screenshots/Screenshot from 2024-02-27 19-02-45.png')])
    # va = VideoAnalysis(device_index=0, window_sec=3, grid_img_nb=9)
    va = VideoAnalysis(
        video_path='/home/tamaya/Documents/cognitive_cabin/test_stuff/14.02.2024/landscape_video_sample_1.mp4',
        window_sec=15,
        grid_img_nb=4,
        width=200)
    va.add_observer(process)
    va.run_forever()
