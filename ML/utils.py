import hashlib
import os
import json

CAPTION_FILE_DIR = os.path.join(".", "cache", "captions")
TRANSCRIPTION_FILE_DIR = os.path.join(".", "cache", "transcriptions")

def get_embedding_file_path(video_path):
    sha256 = hashlib.sha256()

    with open(video_path, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha256.update(data)
    
    caption_embedding_file_path = os.path.join(CAPTION_FILE_DIR, f"{sha256.hexdigest()}.json")
    transcription_embedding_file_path = os.path.join(TRANSCRIPTION_FILE_DIR, f"{sha256.hexdigest()}.json")

    return caption_embedding_file_path, transcription_embedding_file_path
    # return [caption, transcription]

def get_dict_from_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def save_dict_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def is_embedding_cached(video_path):
    caption_embedding_file_path, transcription_embedding_file_path = get_embedding_file_path(video_path)
    return os.path.exists(caption_embedding_file_path) and os.path.exists(transcription_embedding_file_path)

