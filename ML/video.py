from pytube import YouTube
import os
import re
import cv2
import datetime
import sys
import time

# Constants
download_output = os.path.join(".", "download")
frames_output = os.path.join(".", "frames")
audio_output = os.path.join(".", "audio")
interval = 15
image_per_interval = 3

def extract_youtube_id(url):
    regex = r'https:\/\/(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})|https:\/\/youtu\.be\/([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1) if match.group(1) else match.group(2)
    return None

# returns hh:mm:ss.ms
def convert_time(seconds):
    return str(datetime.timedelta(seconds=seconds))


class TestCaseGenerator:
    def __init__ (self, url):
        self.url = url

    def execute (self):
        if os.path.exists(download_output) == False:
            os.mkdir(download_output)
        
        if os.path.exists(frames_output) == False:
            os.mkdir(frames_output)
        
        if os.path.exists(audio_output) == False:
            os.mkdir(audio_output)

        output = self.__download()
        # self.__split_video(output[0])
        self.__split_audio(output[1])

    def __download(self):
        id = extract_youtube_id(self.url)
        file_name = f"{id}.mp4"
        audio_file_name = f"{id}.mp3"
        output_path = os.path.join(download_output, file_name)
        audio_output_path = os.path.join(download_output, audio_file_name)

        if os.path.exists(output_path):
            return output_path
    
        yt = YouTube(self.url)
        # print(yt.streams)

        yt_stream =  yt.streams.filter(file_extension='mp4', type="video", resolution="480p").order_by('resolution').desc().first()
        if yt_stream == None:
            yt_stream = yt.streams.filter(file_extension='mp4', type="video").order_by('resolution').desc().first()

        yt_stream.download(download_output, filename=file_name)
        print("Finished downloading after: ", time.time() - start)

        yt_audio_stream = yt.streams.filter(only_audio=True).first()
        yt_audio_stream.download(download_output, filename=audio_file_name)
        print("Finished downloading audio after: ", time.time() - start)

        print(audio_file_name, file_name)
        return [output_path, audio_output_path]
    
    def __split_video(self, video_path):
        output_folder = os.path.join(frames_output, extract_youtube_id(self.url))
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

        output_image = os.path.join(output_folder, "frame_%04d.jpeg")
        cmd = ["ffmpeg", "-i", video_path, "-r", str(image_per_interval/interval), output_image]
        os.system(" ".join(cmd))
    
    def __split_audio(self, video_path):
        output_folder = os.path.join(audio_output, extract_youtube_id(self.url))
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

        output_audio = os.path.join(output_folder, "audio_%04d.mp3")
        cmd = ["ffmpeg", "-i", video_path, "-f", "segment", "-segment_time", str(interval), "-q:a", "0", "-map" , "a", output_audio]
        os.system(" ".join(cmd))

if __name__ == "__main__":
    start = time.time()
    url = "https://www.youtube.com/watch?v=L8ECu0f9_kA"
    generator = TestCaseGenerator(url)
    generator.execute()
    end = time.time()
    print(end-start)
    
### Note ###
# 1 Hour Video:
#   - 1080p:
#       download time: 120s
#       split time: 440s
#   - 720p:
#       download time: 75s
#       split time: 140s
#   - 480p:
#       download time: 36s
#       split time: 70s
        
        
    