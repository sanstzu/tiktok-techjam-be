import openai
from openai import OpenAI
import os
import concurrent.futures
import base64
import requests
import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import timedelta
import json

# Ensure the key.py file is in the same directory
from key import OPENAI_API_KEY

# Initialize client
api_key = OPENAI_API_KEY
client = OpenAI(api_key=api_key)

def save_dict_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

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
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
    with open(abs_path, "r") as f:
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
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": [
                {"type": "text", "text": user_input},
                *images_payload
            ]}
        ],
        "max_tokens": 1600
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def process_images_in_parallel(image_paths, api_key, prompt_text, user_input, num_threads=30, frames_per_request=3):
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
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def process_embeddings_in_parallel(results, model, num_threads):
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

def seconds_to_hhmmss(seconds):
    return str(timedelta(seconds=seconds))

# Get url name
from video import extract_youtube_id
def get_caption_score(url, user_prompts):
    url = extract_youtube_id(url)

    # Get all the image paths
    directory = './frames/' + url  # When you run video.py, all the frames located inside frames folder
    image_paths = list_files(directory)

    # Get User Input
    user_inputs = user_prompts
    prompt_text = get_sys_prompt('prompt.txt')
    results = []
    captions_dict = {}

    # Captioning
    results = process_images_in_parallel(image_paths, api_key, prompt_text, user_prompts, num_threads=30, frames_per_request=3)
    for i in range(len(results)):
        try:
            caption = results[i]['choices'][0]['message']['content']
            captions_dict[seconds_to_hhmmss(i*5)] = caption
        except KeyError:
            captions_dict[seconds_to_hhmmss(i*5)] = "Missing"

    save_dict_to_json(captions_dict, './results/captions.json')

    # Embedding
    embedding_model = 'text-embedding-3-small'
    embedded_captions = process_embeddings_in_parallel(results, model=embedding_model, num_threads=len(results))
    
    embedded_queries = []
    for user_input in user_inputs:
        embedded_queries.append(np.array(get_embedding(user_input, model=embedding_model)).reshape(1, -1))

    similarity_result = {}

    for timeframe, embeddings in embedded_captions.items():
        scores = []
        for embedded_query in embedded_queries:
            score = cosine_similarity(embeddings, embedded_query).item()
            scores.append(score)
        similarity_result[timeframe] = scores
    
    return similarity_result

# for key in caption_dict:
#     weighted_scores = []
#     for i in range(len(caption_dict[key])):
#         weighted_score = 0.7 * caption_dict[key][i] + 0.3 * transcription_dict[key][i]
#         weighted_scores.append(weighted_score)
#     weighted_score_dict[key] = weighted_scores

# print(weighted_score_dict)