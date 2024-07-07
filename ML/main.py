import os
import sys
import certifi
import ssl
import yt_dlp as youtube_dl
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from caption import get_caption_score
from transcription import get_transcription_score
from edit_video import extract_and_concatenate_clips
from urllib.parse import urlparse, parse_qs
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import json
from video import TestCaseGenerator

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
    with ThreadPoolExecutor() as executor:
        generator = TestCaseGenerator(video_url, executor)
        generator.execute()

# def download_video(video_url, download_path):
#     ydl_opts = {
#         'format': 'best',
#         'outtmpl': os.path.join(download_path, '%(id)s.%(ext)s'),
#     }
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         info_dict = ydl.extract_info(video_url, download=True)
#         video_id = info_dict.get("id", None)
#         file_path = os.path.join(download_path, f"{video_id}.mp4")
#         print(f"Video downloaded to {file_path}")
#         return file_path

def calculate_similarity_scores(caption_score_dict, transcription_score_dict, user_prompts):
    similarity_scores = {}
    for key in caption_score_dict:
        weighted_scores = []
        for i in range(len(caption_score_dict[key])):
            weighted_score = 0.7 * caption_score_dict[key][i] + 0.3 * transcription_score_dict[key][i]
            weighted_scores.append(weighted_score)
        similarity_scores[key] = weighted_scores

    print(similarity_scores)

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

def main(video_url, user_prompts):
    download_path = './download'
    os.makedirs(download_path, exist_ok=True)
    # download_video(video_url)
    video_path = "./download/" + "eLJ5MoSPjVE.mp4"

    print(f"Video path for processing: {video_path}")

    caption_score_dict, transcription_score_dict = run_functions_in_parallel(video_url, user_prompts)
    similarity_scores = calculate_similarity_scores(caption_score_dict, transcription_score_dict, user_prompts)
    top_timeframes = get_top_timeframes(similarity_scores, user_prompts)
    final_timeframes = generate_timeframes_for_editing(top_timeframes)

    output_path = os.path.join(".", "output", f"{extract_youtube_id(video_url)}_output_video.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Timeframes for extraction: {final_timeframes}")
    extract_and_concatenate_clips(video_path, final_timeframes, output_path)
    print(f"Video saved at {output_path}")

if __name__ == "__main__":
    import time
    start_time = time.time()
    video_url = "https://youtu.be/eLJ5MoSPjVE?feature=shared" # change link
    user_prompts = ["header goal", "freekick goal", "ronaldo celebration", "sliding tackle"] # Up to 4 prompts
    main(video_url, user_prompts)
    print(time.time() - start_time)



