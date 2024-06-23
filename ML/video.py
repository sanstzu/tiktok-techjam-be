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
interval = 5

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

        output = self.__download()
        self.__split(output)

    def __download(self):
        id = extract_youtube_id(self.url)
        file_name = f"{id}.mp4"
        output_path = os.path.join(download_output, file_name)

        if os.path.exists(output_path):
            return output_path
    
        yt = YouTube(self.url)
        # print(yt.streams)

        yt_stream =  yt.streams.filter(file_extension='mp4', type="video", resolution="1080p").order_by('resolution').desc().first()
        if yt_stream == None:
            yt_stream = yt.streams.filter(file_extension='mp4', type="video").order_by('resolution').desc().first()

        yt_stream.download(download_output, filename=id)
        return output_path
    
    def __split(self, video_path):
        output_folder = os.path.join(frames_output)
        if os.path.exists(output_folder) == False:
            os.mkdir(output_folder)

        output_image = os.path.join(output_folder, "frame_%04d.jpg")
        cmd = ["ffmpeg", "-i", video_path, "-r", str(1/interval), output_image]
        os.system(" ".join(cmd))

if __name__ == "__main__":
    start = time.time()
    url = "https://www.youtube.com/watch?v=ulfJXy4QptQ"
    generator = TestCaseGenerator(url)
    generator.execute()
    end = time.time()
    print(end-start)
    
    
        
        
    