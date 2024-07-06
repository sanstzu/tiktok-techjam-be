import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from image_similarity import get_similarity_score, get_embedding
from transcription import get_transcription_dict
from edit_video import extract_and_concatenate_clips
import os

MAX_PROMPT = 4
VIDEO_DURATION = 60  # seconds
CLIP_DURATION = 15  # seconds

def calculate_similarity_scores(caption_dict, transcription_dict, user_prompts, embedding_model='text-embedding-ada-002'):
    similarity_scores = {}
    
    for timeframe, text in caption_dict.items():
        embed1 = get_embedding(text, embedding_model)
        scores = []
        for prompt in user_prompts:
            embed2 = get_embedding(prompt, embedding_model)
            score = cosine_similarity(np.array(embed1).reshape(1, -1), np.array(embed2).reshape(1, -1)).item()
            scores.append(score)
        similarity_scores[timeframe] = scores

    for timeframe, text in transcription_dict.items():
        embed1 = get_embedding(text, embedding_model)
        scores = []
        for prompt in user_prompts:
            embed2 = get_embedding(prompt, embedding_model)
            score = cosine_similarity(np.array(embed1).reshape(1, -1), np.array(embed2).reshape(1, -1)).item()
            scores.append(score)
        if timeframe in similarity_scores:
            similarity_scores[timeframe] = [max(x, y) for x, y in zip(similarity_scores[timeframe], scores)]
        else:
            similarity_scores[timeframe] = scores

    return similarity_scores

def get_top_timeframes(similarity_scores, user_prompts):
    video_per_prompt = MAX_PROMPT // len(user_prompts)
    sorted_scores = sorted(similarity_scores.items(), key=lambda item: max(item[1]), reverse=True)
    
    top_timeframes = []
    for i, prompt in enumerate(user_prompts):
        count = video_per_prompt if len(user_prompts) > 1 else MAX_PROMPT
        prompt_top_timeframes = []
        for timeframe, scores in sorted_scores:
            if count == 0:
                break
            if timeframe not in prompt_top_timeframes:
                prompt_top_timeframes.append(timeframe)
                count -= 1
        top_timeframes.extend(prompt_top_timeframes)
        sorted_scores = sorted_scores[len(prompt_top_timeframes):]

    return sorted(top_timeframes, key=lambda x: int(x.split(":")[1]) * 60 + int(x.split(":")[2]))

def generate_timeframes_for_editing(top_timeframes):
    final_timeframes = []
    for timeframe in top_timeframes:
        h, m, s = map(int, timeframe.split(":"))
        start_seconds = h * 3600 + m * 60 + s - 5
        end_seconds = h * 3600 + m * 60 + s + 5
        final_timeframes.append(f"{start_seconds // 3600:02}:{(start_seconds % 3600) // 60:02}:{start_seconds % 60:02} - {end_seconds // 3600:02}:{(end_seconds % 3600) // 60:02}:{end_seconds % 60:02}")
    return final_timeframes

def main(video_url, user_prompts):
    caption_dict = get_similarity_score(video_url, user_prompts)
    transcription_dict = get_transcription_dict(video_url)

    similarity_scores = calculate_similarity_scores(caption_dict, transcription_dict, user_prompts)
    top_timeframes = get_top_timeframes(similarity_scores, user_prompts)
    final_timeframes = generate_timeframes_for_editing(top_timeframes)

    video_path = os.path.join(".", "download", f"{extract_youtube_id(video_url)}.mp4")
    output_path = os.path.join(".", "output", f"{extract_youtube_id(video_url)}_output_video.mp4")
    
    extract_and_concatenate_clips(video_path, final_timeframes, output_path)
    print(f"Video saved at {output_path}")

if __name__ == "__main__":
    video_url = "https://youtu.be/fYDMpMlC1Rg?si=Hin4odGiJIiOPgvM"
    user_prompts = ["france shot", "great score", "amazing defense"]
    main(video_url, user_prompts)


