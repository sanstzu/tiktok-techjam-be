from pydub import AudioSegment
import numpy as np
import os
import math
import moviepy.editor as mp
import time
from video import extract_youtube_id
# Explicitly set the path for ffmpeg and ffprobe
os.environ['PATH'] += os.pathsep + '/usr/local/bin'

def get_loudest_timeframes(audio_path, frame_duration_ms=5000):
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Calculate the number of frames
    num_frames = math.ceil(len(audio) / frame_duration_ms)
    
    # Calculate the average amplitude for each frame
    frames = []
    for i in range(num_frames):
        start_time = i * frame_duration_ms
        end_time = start_time + frame_duration_ms
        frame = audio[start_time:end_time]
        amplitude = np.abs(np.array(frame.get_array_of_samples())).mean()
        frames.append(amplitude)  # Convert to seconds
    
    # Sort frames by amplitude in descending order
    return amplitude


def get_loudness_score(url):
    audio_path = os.path.join(".", "audio", extract_youtube_id(url))

    loudness_score = get_loudest_timeframes(audio_path)
    return loudness_score