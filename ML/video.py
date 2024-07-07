import os
import re
import cv2
import datetime
import sys
import shutil
import subprocess
from pytube import YouTube
from concurrent.futures import ThreadPoolExecutor

# Constants
download_output = os.path.join(".", "download")
frames_output = os.path.join(".", "frames")
audio_output = os.path.join(".", "audio")
tmp_folder = os.path.join(".", "tmp")
interval = 5
total_frames_per_clip = 3

def extract_youtube_id(url):
    regex = r'https:\/\/(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})|https:\/\/youtu\.be\/([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1) if match.group(1) else match.group(2)
    return None

# returns hh:mm:ss.ms
def convert_time(seconds):
    return str(datetime.timedelta(seconds=seconds))

def file_list(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def run_command(cmd):
    subprocess.run(cmd)

class TestCaseGenerator:
    def __init__ (self, url, executor):
        self.url = url
        self.executor = executor

    def execute (self):
        if os.path.exists(download_output) == False:
            os.mkdir(download_output)
        
        if os.path.exists(frames_output) == False:
            os.mkdir(frames_output)

        if os.path.exists(audio_output) == False:
            os.mkdir(audio_output)

        if os.path.exists(tmp_folder) == False:
            os.mkdir(tmp_folder)

        output = self.__download()
        merged_path = self.__merge_video_audio(output[0], output[1])
        folder_path = self.__split_video(merged_path)
        self.__extract_frames(folder_path)
        self.__extract_audio(output[1])


    def __download(self):
        id = extract_youtube_id(self.url)
        file_name = f"{id}.mp4"
        audio_file_name = f"{id}.mp3"
        output_path = os.path.join(download_output, file_name)
        audio_output_path = os.path.join(download_output, audio_file_name)

        yt = YouTube(self.url)

        if not os.path.exists(output_path):
            yt_stream = yt.streams.filter(file_extension='mp4', type="video", resolution="480p").order_by('resolution').desc().first()
            if yt_stream == None:
                yt_stream = yt.streams.filter(file_extension='mp4', type="video").order_by('resolution').desc().first()
            yt_stream.download(download_output, filename=f"{id}.mp4")
    
        
        if not os.path.exists(audio_output_path):
            yt_audio_stream = yt.streams.filter(only_audio=True).first()

            yt_audio_stream.download(download_output, filename=f"{id}.mp3")
        
        
        return [output_path, audio_output_path]
    
    def __merge_video_audio(self, video_path, audio_path):
        output_folder = os.path.join(tmp_folder, "merged")
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

        output_video = os.path.join(tmp_folder, "merged", f"{extract_youtube_id(self.url)}.mp4")

        #  ffmpeg -i "$video" -i "$audio_file" -c:v copy -c:a aac -strict experimental "./tmp/combined/${id}.mp4"
        cmd = [
            "ffmpeg", 
            "-y", 
            "-i", video_path, 
            "-i", audio_path, 
            "-c:v", "copy", 
            "-c:a", "aac", 
            "-strict", "experimental", 
            output_video
        ]

        subprocess.run(cmd)

        return output_video
    
    def __split_video(self, video_path):
        output_folder = os.path.join(tmp_folder, "clips", extract_youtube_id(self.url))
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

         # Split the video into 5-second clips
        # ffmpeg -i "$input_file" -c copy -map 0 -segment_time 5 -f segment -reset_timestamps 1 "./tmp/clips/${id}/%03d.mp4"
        cmd = [
            "ffmpeg", 
            "-y", 
            "-i", video_path, 
            "-preset", "ultrafast", 
            '-force_key_frames', f"expr:gte(t,n_forced*{interval})", 
            "-c:v", "libx264", 
            "-c:a", "aac", 
            "-map", "0", 
            "-segment_time", str(interval), 
            "-f", "segment", 
            "-reset_timestamps", "1", 
            os.path.join(output_folder, "%03d.mp4")
        ]

        subprocess.run(cmd)

        return output_folder
    
    def __extract_frames(self, clips_path):
        # Extract the first frame
        # ffmpeg -i "$clip" -vf "select=eq(n\,0)" -vsync vfr -q:v 2 "./frames/${id}/$(basename "$clip" .mp4).jpg"
        output_folder = os.path.join(frames_output, extract_youtube_id(self.url))
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

        clips = file_list(clips_path)

        def get_frame(clip_path, frame_no, output_path):
            cmd = [
                "ffmpeg", 
                "-y", 
                "-i", clip_path, 
                "-vf", f"select=eq(n\,{frame_no})", 
                "-vsync", "vfr", 
                "-q:v", "2", 
                output_path
            ]

            if self.executor != None:
                self.executor.submit(run_command, cmd)
            else:
                subprocess.run(cmd)


        def get_frames(clip):
            frames_cmd = [
                "ffprobe",
                "-v", "error",
                "-count_frames",
                "-select_streams", "v:0",
                "-show_entries", "stream=nb_read_frames",
                "-of", "default=nokey=1:noprint_wrappers=1",
                os.path.join(clips_path, clip)
            ]

            no_of_frames = int(subprocess.run(frames_cmd, capture_output=True, text=True).stdout.strip())
            clip_name = os.path.splitext(os.path.basename(clip))[0]

            for i in range(total_frames_per_clip):
                current_frame = i * (no_of_frames // total_frames_per_clip)
                output_path = os.path.join(output_folder, f"{clip_name}_{i}.jpg")
                get_frame(os.path.join(clips_path, clip), current_frame, output_path)

        for clip in clips:
            get_frames(clip)
            

    def __extract_audio(self, audio_path):
        # Extract the audio
        # ffmpeg -i "$clip" -q:a 0 -map a "./audio/${id}/$(basename "$clip" .mp4).mp3"
        output_folder = os.path.join(audio_output)
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

        shutil.copyfile(audio_path, os.path.join(output_folder, f"{extract_youtube_id(self.url)}.mp3"))

if __name__ == "__main__":
    # calculate start time
    start_time = datetime.datetime.now()

    url = "https://youtube.com/watch?v=eLJ5MoSPjVE"
    with ThreadPoolExecutor() as executor:
        generator = TestCaseGenerator(url, executor)
        generator.execute()

    # calculate end time
    end_time = datetime.datetime.now()

    print(f"Time taken: {end_time - start_time}")