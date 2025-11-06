import numpy as np
import joblib

classifier = joblib.load('emotion_model.pkl')

def analyze_emotion(image_path):
    from deepface import DeepFace
    embedding_info = DeepFace.represent(img_path=image_path, model_name='VGG-Face',enforce_detection=False)
    embedding = embedding_info[0]["embedding"]
    embedding = np.array(embedding).reshape(1, -1)
    predicted_emotion = classifier.predict(embedding)[0]
    return predicted_emotion