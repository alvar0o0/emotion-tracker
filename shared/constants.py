# shared/constants.py

# Paul Ekman's 6 basic emotions
# Format: database_value: (emoji, spanish_name, english_name)
EKMAN_EMOTIONS = {
    "anger": ("😠", "Ira", "Anger"),
    "disgust": ("🤢", "Asco", "Disgust"),
    "fear": ("😨", "Miedo", "Fear"),
    "happiness": ("😊", "Alegría", "Happiness"),
    "sadness": ("😢", "Tristeza", "Sadness"),
    "surprise": ("😲", "Sorpresa", "Surprise"),
}

def get_emotion_display_name(emotion_key: str) -> str:
    """Returns the formatted bilingual display name with emoji."""
    if emotion_key in EKMAN_EMOTIONS:
        emoji, es_name, en_name = EKMAN_EMOTIONS[emotion_key]
        return f"{emoji} {es_name} / {en_name}"
    return emotion_key

def get_valid_emotions() -> list[str]:
    """Returns a list of valid database keys for the emotions."""
    return list(EKMAN_EMOTIONS.keys())
