# dark_pattern.py
# 1) TODO: Download 100 sample screenshots for training/testing
# 2) Define labels
LABELS = [
    "Confirmshaming",
    "Misdirection",
    "Sneaking"
]

# 3) Stub classify(img) using a lightweight ViT model from Hugging Face
from typing import Dict
from PIL import Image
import torch
from transformers import ViTImageProcessor, ViTForImageClassification
import numpy as np

# Download model weights on first run
MODEL_NAME = "nateraw/vit-base-patch16-224-in21k"

class DarkPatternClassifier:
    def __init__(self):
        self.processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
        self.model = ViTForImageClassification.from_pretrained(MODEL_NAME)
        self.model.eval()

    def classify(self, img: Image.Image) -> Dict[str, float]:
        inputs = self.processor(images=img, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        # For stub, map to our labels (simulate probabilities)
        # In real use, fine-tune model and map outputs
        # Here, just return random probabilities for demo
        np.random.seed(42)
        fake_probs = np.random.dirichlet(np.ones(len(LABELS)), size=1)[0]
        return {label: float(p) for label, p in zip(LABELS, fake_probs)}

# Singleton for reuse
_classifier = None

def classify(img: Image.Image) -> Dict[str, float]:
    global _classifier
    if _classifier is None:
        _classifier = DarkPatternClassifier()
    return _classifier.classify(img) 