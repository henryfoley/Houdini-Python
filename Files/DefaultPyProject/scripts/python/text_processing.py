import numpy as np
import hou
import json
import os

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

