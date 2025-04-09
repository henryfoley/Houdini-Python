import hou
import json
import os
import torch
import tokenizer as tk

# Load model directly
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification

processor = AutoProcessor.from_pretrained("openai/clip-vit-large-patch14-336")
model = AutoModelForZeroShotImageClassification.from_pretrained("openai/clip-vit-large-patch14-336")

def load_tokenizer_config(json_path):
    # Read tokenizer configuration from json
    if os.path.exists(json_path):
        with open(json_path,'r') as f:
            tokens = json.load(f)
    else:
        # Display file not found message
        tokens = None
        raise hou.NodeError("Cannot find the JSON file: tokenizer.json")
    return tokens

text = "a photo of a cat"
tokens = tk.tokenize(text)


with torch.no_grad():
    text_features = model.encode_text(text)
print(text_features)