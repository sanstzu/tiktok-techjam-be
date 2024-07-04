from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import concatenate_videoclips, VideoFileClip
import os

output_dir = os.path.join(".", "output")
if os.path.exists(output_dir) == False:
    os.mkdir(output_dir)

tmp_dir = os.path.join(output_dir, "tmp")
if os.path.exists(tmp_dir) == False:
    os.mkdir(tmp_dir) 

def extract_and_concatenate_clips(video_path, timeframes, output_path):
    # Parse the timeframes
    clips = []
    for timeframe in timeframes:
        start_time, end_time = timeframe.split(' - ')
        start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(":")))
        end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(":")))
        
        # Extract the subclip
        temp = f"temp_{video_id}_{start_seconds}_{end_seconds}.mp4"
        temp_path = os.path.join(tmp_dir, temp)
        ffmpeg_extract_subclip(video_path, start_seconds, end_seconds, targetname=temp_path)
        clip = VideoFileClip(temp_path)
        clips.append(clip)
    
    # Concatenate the clips
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec="libx264")

# Paths and Timeframes
video_path = "./download/Gl7m0cVa37k.mp4"
video_id = os.path.splitext(os.path.basename(video_path))[0]

timeframes = ["00:00:05 - 00:00:10", "00:01:35 - 00:01:40", "00:03:15 - 00:03:20"]
output_path = os.path.join(output_dir, f"{video_id}_output_video.mp4")

extract_and_concatenate_clips(video_path, timeframes, output_path)
