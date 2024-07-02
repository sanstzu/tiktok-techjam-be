from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from image_similarity import get_similarity_score
from loudness import get_loudness_score
from transcription import get_transcription_score

def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0, 1]

def combine_scores(caption_sim, loudness, transcription_sim):
    max_loudness = max([frame[2] for frame in loudest_timeframes])
    normalized_loudness = loudness / max_loudness
    combined_score = caption_sim * 0.5 + normalized_loudness * 0.25 + transcription_sim * 0.25
    return combined_score

def calculate_score(url, prompt):
    caption_scores = get_similarity_score(url, prompt)
    loudness_scores = get_loudness_score(url)
    transcripton_scores = get_transcription_score(url, prompt)

    scores = []

    for i in range(len(caption_scores)):
        scores.append(combine_scores(
            caption_scores[i],
            loudness_scores[i],
            transcripton_scores[i]
        ))
    
    print(scores)
