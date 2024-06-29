from openai import OpenAI
from key import OPENAI_API_KEY
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from image_similarity import get_similarity_score
from loudness import get_loudness_score
from video import extract_youtube_id
import os

client = OpenAI(api_key=OPENAI_API_KEY)

def list_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0, 1]

def transcribe(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )

    return transcription.text
    

def get_transcription_score(url, prompt):
    video_path = os.path.join(".", "audio", extract_youtube_id(url))
    files = list_files(video_path)

    scores = []

    for i in files:
        transcription = transcribe(i)
        score = calculate_similarity(transcription, prompt)

        scores.append(score)
    
    return scores

