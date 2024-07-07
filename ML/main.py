import os
import certifi
import ssl
from ML.caption import get_caption_score
from ML.transcription import get_transcription_score
from ML.edit_video import extract_and_concatenate_clips
from urllib.parse import urlparse, parse_qs
import concurrent.futures
import json
from ML.video import TestCaseGenerator
import ML.utils as utils
import hashlib

# Set up custom SSL context using certifi
certifi_path = certifi.where()
ssl_context = ssl.create_default_context(cafile=certifi_path)

# Update environment variable to use certifi's certificates
os.environ['SSL_CERT_FILE'] = certifi_path

# Use the SSL context in network requests
from urllib.request import build_opener, HTTPSHandler, install_opener

opener = build_opener(HTTPSHandler(context=ssl_context))
install_opener(opener)

MAX_PROMPT = 4
VIDEO_DURATION = 60  # seconds
CLIP_DURATION = 15  # seconds

def save_dict_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def run_functions_in_parallel(video_url, user_prompts):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_caption = executor.submit(get_caption_score, video_url, user_prompts)
        future_transcription = executor.submit(get_transcription_score, video_url, user_prompts)

        caption_score_dict = future_caption.result()
        transcription_score_dict = future_transcription.result()

    return caption_score_dict, transcription_score_dict

def download_video(video_url):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        generator = TestCaseGenerator(video_url, executor)
        generator.execute()

def calculate_similarity_scores(caption_score_dict, transcription_score_dict, user_prompts):
    print("Caption Score Keys:", caption_score_dict.keys())
    print("Transcription Score Keys:", transcription_score_dict.keys())

    similarity_scores = {}
    for key in caption_score_dict:
        weighted_scores = []
        for i in range(len(caption_score_dict[key])):
            caption_score = caption_score_dict[key][i]
            transcription_score = transcription_score_dict.get(key, [0]*len(caption_score_dict[key]))[i]  # Default to 0 if key is missing
            weighted_score = 0.7 * caption_score + 0.3 * transcription_score
            weighted_scores.append(weighted_score)
        similarity_scores[key] = weighted_scores

    print("Similarity Scores:", similarity_scores)
    return similarity_scores

def get_top_timeframes(similarity_scores, user_prompts):
    video_per_prompt = MAX_PROMPT // len(user_prompts)
    sorted_scores = sorted(similarity_scores.items(), key=lambda item: max(item[1]), reverse=True)
    
    top_timeframes = []
    for i, prompt in enumerate(user_prompts):
        count = video_per_prompt if len(user_prompts) > 1 else MAX_PROMPT
        prompt_top_timeframes = []
        for timeframe, scores in sorted_scores:
            if count == 0:
                break
            if timeframe not in prompt_top_timeframes:
                prompt_top_timeframes.append(timeframe)
                count -= 1
        top_timeframes.extend(prompt_top_timeframes)
        sorted_scores = sorted_scores[len(prompt_top_timeframes):]

    return sorted(top_timeframes, key=lambda x: int(x.split(":")[1]) * 60 + int(x.split(":")[2]))

def generate_timeframes_for_editing(top_timeframes):
    final_timeframes = []
    for timeframe in top_timeframes:
        h, m, s = map(int, timeframe.split(":"))
        start_seconds = max(h * 3600 + m * 60 + s - 5, 0)
        end_seconds = h * 3600 + m * 60 + s + 5
        final_timeframes.append(f"{start_seconds // 3600:02}:{(start_seconds % 3600) // 60:02}:{start_seconds % 60:02} - {end_seconds // 3600:02}:{(end_seconds % 3600) // 60:02}:{end_seconds % 60:02}")
    return final_timeframes

def extract_youtube_id(url):
    parsed_url = urlparse(url)
    
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def get_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def main(video_url, user_prompts):
    download_path = './download'
    os.makedirs(download_path, exist_ok=True)

    video_id = get_sha256(video_url)
    video_path = video_url


    if not utils.is_embedding_cached(video_url): 
        # this just pre process the video url
        pass
        download_video(video_url)
        

    print(f"Video path for processing: {video_path}")

    caption_score_dict, transcription_score_dict = run_functions_in_parallel(video_url, user_prompts)
    similarity_scores = calculate_similarity_scores(caption_score_dict, transcription_score_dict, user_prompts)
    top_timeframes = get_top_timeframes(similarity_scores, user_prompts)
    final_timeframes = generate_timeframes_for_editing(top_timeframes)

    output_path = os.path.join(".", "output", f"{video_id}_output_video.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Timeframes for extraction: {final_timeframes}")
    extract_and_concatenate_clips(video_path, final_timeframes, output_path)
    print(f"Video saved at {output_path}")
    return output_path

if __name__ == "__main__":
    import time
    start_time = time.time()
    video_url = "./test-3.mp4" # change link
    user_prompts = ["corner kick"] # Up to 4 prompts
    main(video_url, user_prompts)
    print(time.time() - start_time)





