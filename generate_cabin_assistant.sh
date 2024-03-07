ollama list
ollama pull llava
ollama pull mistral
ollama rm mistral-cabin-assistant direction-assistant-extractor llava_picture_descriptor.modelfile
ollama create mistral-cabin-assistant -f mistral_cabin_assistant.modelfile
ollama create direction-assistant-extractor -f mistral_direction_assistant_extractor.modelfile
ollama create llava-picture-descriptor -f llava_picture_descriptor.modelfile 
ollama list
