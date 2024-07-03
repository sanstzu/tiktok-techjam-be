# coding: utf-8
import openai
from openai import OpenAI
import os
import concurrent.futures
import base64
import requests
from key import OPENAI_API_KEY
import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialize client
api_key=OPENAI_API_KEY
client = OpenAI(api_key=api_key)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def list_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def get_sys_prompt(file_path):
    f = open("prompt.txt", "r")
    prompt_text = f.read()
    return prompt_text

def make_api_request(image_paths, api_key, prompt_text, user_input):
    # Encode all images in the list
    base64_images = [encode_image(image_path) for image_path in image_paths]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Prepare the images for the payload
    images_payload = [{"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{img}", "detail": "low"}} for img in base64_images]

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": [
                {"type": "text", "text": user_input},
                *images_payload
            ]}
        ],
        "max_tokens": 4096
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def process_images_in_parallel(image_paths, api_key, prompt_text, user_input, num_threads=10, frames_per_request=3):
    results = []

    # Split image_paths into chunks of frames_per_request
    image_chunks = [image_paths[i:i + frames_per_request] for i in range(0, len(image_paths), frames_per_request)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_image_chunk = {executor.submit(make_api_request, chunk, api_key, prompt_text, user_input): chunk for chunk in image_chunks}
        for future in concurrent.futures.as_completed(future_to_image_chunk):
            image_chunk = future_to_image_chunk[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'{image_chunk} generated an exception: {exc}')

    return results

def get_embedding(text, model):
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def process_embeddings_in_parallel(results, model, num_threads=10):
    def embed_result(result):
        return get_embedding(result['choices'][0]['message']['content'], model=model)
    
    embedded_frame = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_index = {executor.submit(embed_result, result): i for i, result in enumerate(results)}
        for future in concurrent.futures.as_completed(future_to_index):
            i = future_to_index[future]
            try:
                embedding = future.result()
                embedded_frame[i] = np.array(embedding).reshape(1, -1)
            except Exception as exc:
                print(f'Embedding for result {i} generated an exception: {exc}')

    return embedded_frame



# Get url name
from video import extract_youtube_id
def get_similarity_score(url, prompt):
    url = extract_youtube_id(url)

    # Get all the image paths
    directory = './frames/' + url  # When you run video.py, all the frames located inside frames folder
    image_paths = list_files(directory)
    directory

    # Get User Input
    user_input = prompt
    prompt_text = get_sys_prompt('prompt.txt')
    results = []

    # Captioning
    results = process_images_in_parallel(image_paths, api_key, prompt_text, user_input, num_threads=20, frames_per_request=3)

    # Embedding
    embedding_model = 'text-embedding-3-small'
    embedded_frame = process_embeddings_in_parallel(results, model=embedding_model, num_threads=30)
    embedded_query = get_embedding(user_input, model=embedding_model)
    embedded_query = np.array(embedded_query).reshape(1, -1)

    # similarity_result = []
    # for i in range(len(image_paths)):
    #     similarity_result.append(cosine_similarity(embedded_frame[i], embedded_query))
    # return similarity_result

    similarity_result = {}
    for i in range(len(results)):
        try:
            similarity_result[i] = cosine_similarity(embedded_frame[i], embedded_query)
        except KeyError:
            similarity_result[i] = 0
            
    ranked_frame_dict = dict(sorted(similarity_result.items(), key=lambda x:x[1], reverse=True))
    
    return ranked_frame_dict