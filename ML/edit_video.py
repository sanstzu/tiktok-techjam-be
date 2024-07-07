from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import concatenate_videoclips, VideoFileClip
import os

output_dir = os.path.join(".", "output")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

tmp_dir = os.path.join(output_dir, "tmp")
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

def merge_intervals(timeframes):
    # Convert timeframes to seconds
    intervals = []
    for timeframe in timeframes:
        start_time, end_time = timeframe.split(' - ')
        start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(":")))
        end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(":")))
        intervals.append((start_seconds, end_seconds))
    
    # Sort intervals by start time
    intervals.sort()

    # Merge overlapping intervals
    merged_intervals = []
    current_start, current_end = intervals[0]
    for start, end in intervals[1:]:
        if start <= current_end:  # Overlapping intervals
            current_end = max(current_end, end)
        else:  # Non-overlapping interval, add the current interval to the list
            merged_intervals.append((current_start, current_end))
            current_start, current_end = start, end
    merged_intervals.append((current_start, current_end))  # Add the last interval

    return merged_intervals

import cv2

def concatenate_videos(new_video_path, *videos):
    if not videos:
        raise ValueError("No videos provided for concatenation")

    # Check if the video paths are valid and are strings
    video_paths = [v for v in videos if isinstance(v, (str, os.PathLike))]

    if not video_paths:
        raise ValueError("No valid video paths provided")

    # Open the first video to get the FPS and resolution
    first_video = cv2.VideoCapture(video_paths[0])
    if not first_video.isOpened():
        raise ValueError(f"Could not open the video file: {video_paths[0]}")
    
    # Get the FPS and resolution from the first video
    fps = first_video.get(cv2.CAP_PROP_FPS)
    width = int(first_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(first_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    resolution = (width, height)
    first_video.release()  # Release the first video as we are done with it

    # Create the VideoWriter object
    video_writer = cv2.VideoWriter(new_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, resolution)

    # Concatenate the videos
    for v in video_paths:
        curr_v = cv2.VideoCapture(v)
        if not curr_v.isOpened():
            print(f"Could not open the video file: {v}")
            continue

        while curr_v.isOpened():
            r, frame = curr_v.read()
            if not r:
                break
            video_writer.write(frame)

        curr_v.release()

    video_writer.release()

def extract_and_concatenate_clips(video_path, timeframes, output_path):
    merged_intervals = merge_intervals(timeframes)
    
    # Parse the timeframes
    clips = []
    clips_path = []
    for start_seconds, end_seconds in merged_intervals:
        # Extract the subclip
        temp = f"temp_{os.path.basename(video_path)}_{start_seconds}_{end_seconds}.mp4"
        temp_clip_path = os.path.join(tmp_dir, temp)
        ffmpeg_extract_subclip(video_path, start_seconds, end_seconds, targetname=temp_clip_path)
        clip = VideoFileClip(temp_clip_path)
        clips.append(clip)
        
        clips_path.append(temp_clip_path)
    
    # # Concatenate the clips
    # final_clip = concatenate_videoclips(clips)

    # # Write the final video
    # final_clip.write_videofile(output_path, codec="libx264")

    # ffmpeg_command = f"ffmpeg -i {output_path} -c:v libx264 {output_path}"
    # os.system(ffmpeg_command)
    concatenate_videos(output_path, *clips_path)

# # Example usage
# video_path = "./download/Gl7m0cVa37k.mp4"
# video_id = os.path.splitext(os.path.basename(video_path))[0]
# output_path = os.path.join(output_dir, f"{video_id}_output_video.mp4")
# timeframes = ["00:00:00 - 00:00:10", "00:00:05 - 00:00:15", "00:00:30 - 00:00:40", "00:00:35 - 00:00:45"]

# extract_and_concatenate_clips(video_path, timeframes, output_path)