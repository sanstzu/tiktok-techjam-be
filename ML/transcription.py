from openai import OpenAI
from key import OPENAI_API_KEY
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from image_similarity import get_similarity_score
from moviepy.editor import VideoFileClip
from datetime import timedelta
import os
import json
import subprocess
from urllib.parse import urlparse, parse_qs

client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="srt"
    )
    return transcription

def process_transcription(transcription):
    blocks = transcription.split('\n\n')
    processed_dict = {}
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_range = lines[1]
            text = lines[2]
            start_time = time_range.split(' --> ')[0]
            # Convert the time format from "00:00:00,000" to "0:00:00"
            formatted_start_time = start_time[:-4]
            processed_dict[formatted_start_time] = text
    return processed_dict

def format_transcription_dict(transcription_dict, interval=5):
    def time_to_seconds(time_str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

    def seconds_to_time(seconds):
        return str(timedelta(seconds=seconds))

    formatted_transcription_dict = {}

    trans_times = sorted(transcription_dict.keys(), key=lambda t: time_to_seconds(t))
    trans_times_in_seconds = [time_to_seconds(t) for t in trans_times]

    current_interval_start = 0
    combined_transcription = []

    for trans_time, trans_text in zip(trans_times_in_seconds, trans_times):
        while trans_time >= current_interval_start + interval:
            interval_key = seconds_to_time(current_interval_start)
            formatted_transcription_dict[interval_key] = " ".join(combined_transcription).strip() if combined_transcription else "No caption"
            current_interval_start += interval
            combined_transcription = []

        combined_transcription.append(transcription_dict[trans_text])

    # Add remaining transcriptions for the last interval
    interval_key = seconds_to_time(current_interval_start)
    formatted_transcription_dict[interval_key] = " ".join(combined_transcription).strip() if combined_transcription else "No caption"

    return formatted_transcription_dict

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='mp3')

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

def get_transcription_dict(url):
    video_id = extract_youtube_id(url)
    audio_path = os.path.join(".", "download", f"{video_id}.mp3")
    video_path = os.path.join(".", "download", f"{video_id}.mp4")
    
    if not os.path.exists(audio_path):
        extract_audio(video_path, audio_path)
    
    transcription = process_transcription(transcribe(audio_path))
    transcription_dict = format_transcription_dict(transcription)
    return transcription_dict



