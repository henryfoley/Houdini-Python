import hou
import numpy as np
from transformers import AutoTokenizer

text = "You should've done this"

def tokenize(text, use_fast=True):
    tokenizer = AutoTokenizer.from_pretrained('openai/clip-vit-large-patch14-336', use_fast=use_fast)
    tokens = tokenizer(text)
    return tokens

def create_point_inputs(tokens):
    if tokens is None:
        raise hou.NodeError("Tokens are Missing")
    
    ids = tokens['input_ids']
    mask = tokens['attention_mask']

    if ids is None or mask is None:
        raise hou.NodeError(f"Id or Mask value error. Id Value:{ids}, Mask Value: {mask}")
    
    # Create points with attributes
    if len(ids) == len(mask):
        
        # Get the current node
        node = hou.pwd()
        geo : hou.Geometry = node.geometry()

        # Reformat attributes
        target_length = 77
        padding_length = max(0, target_length - len(ids))
        padded_input_ids = np.pad(ids, (0, padding_length), 'constant', constant_values=0)
        padded_attention_mask = np.pad(mask, (0, padding_length), 'constant', constant_values=0)

        # Reshape to include batch dimension
        padded_input_ids = padded_input_ids.reshape(1, -1)
        padded_attention_mask = padded_attention_mask.reshape(1,-1)

        # Add input_ids and attention_mask attributes
        for i in range(padded_input_ids.shape[1]):
            point : hou.Point = geo.createPoint()
            
            # Create integer attributes for each token and mask value
            if not geo.findPointAttrib("input_ids"):
                geo.addAttrib(hou.attribType.Point, "input_ids", 0)
            point.setAttribValue("input_ids", int(padded_input_ids[0, i]))
            
            if not geo.findPointAttrib("attention_mask"):
                geo.addAttrib(hou.attribType.Point, "attention_mask", 0)
            point.setAttribValue("attention_mask", int(padded_attention_mask[0, i]))
        


    else: 
        raise hou.NodeError(f"Id-Mask length error. Length of Ids: {len(ids)}, Length of Masks: {len(mask)}")