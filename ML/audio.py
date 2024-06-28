# Get url name
from video import extract_youtube_id
import moviepy.editor as mp

url = extract_youtube_id("https://www.youtube.com/watch?v=ulfJXy4QptQ")

video_path = './download/' + url + '.mp4'
audio_path = "./audio/" + url + '.mp3'

clip = mp.VideoFileClip(video_path)
clip.audio.write_audiofile(audio_path)
