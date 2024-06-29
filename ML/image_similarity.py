# coding: utf-8
import openai
from openai import OpenAI
import os
import base64
import requests
from key import OPENAI_API_KEY
import math
import numpy as np

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

# Get url name
from video import extract_youtube_id
def get_similarity_score(url, prompt):
    url = extract_youtube_id(url)

    # Get all the image paths
    directory = './frames/' + url  # When you run video.py, all the frames located inside frames folder
    image_paths = list_files(directory)
    directory
    # Get System Prompt
    f = open("prompt.txt", "r")
    prompt_text = f.read()

    # Get User Input
    user_input = prompt
    results = []

    # Iterate through each image path
    for image_path in image_paths:
        # Getting the base64 string
        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": [{"type": "text", "text": user_input}, {"type": "image_url","image_url": {"url": f"data:image/jpg;base64,{base64_image}", "detail": "low"}}]}
                # user_input text can be removed
            ],
            "max_tokens": 4096
        }

        # Make the API request
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Append the result to the list
        results.append(response.json())

    # Iterate through all the results
    for i in range(len(image_paths)):
        try:
            print(i, ": ", results[i]['choices'][0]['message']['content'])
        except KeyError:
            print(i, ": missing")

    embedding_model = 'text-embedding-3-small'
    def get_embedding(text, model=embedding_model):
        return client.embeddings.create(input = [text], model=model).data[0].embedding

    embedded_frame = {}
    for i in range(len(results)):
        embedded_frame[i] = get_embedding(results[i]['choices'][0]['message']['content'], model=embedding_model)
        embedded_frame[i] = np.array(embedded_frame[i]).reshape(1,-1)

    embedded_query = get_embedding(user_input, model=embedding_model)
    embedded_query = np.array(embedded_query).reshape(1,-1)
    from sklearn.metrics.pairwise import cosine_similarity

    similarity_result = []
    for i in range(len(image_paths)):
        similarity_result.append(cosine_similarity(embedded_frame[i], embedded_query))

    return similarity_result