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

        # Create Point
        #point : hou.Point = geo.createPoint()

        # Set the position of the point
        #point.setPosition((0, 0, 0)) # X, Y, Z coordinates

        # Reformat attributes
        target_length = 77
        padding_length = max(0, target_length - len(ids))
        padded_input_ids = np.pad(ids, (0, padding_length), 'constant', constant_values=0)
        padded_attention_mask = np.pad(mask, (0, padding_length), 'constant', constant_values=0)

        # Reshape to include batch dimension
        padded_input_ids = padded_input_ids.reshape(1, -1)
        padded_attention_mask = padded_attention_mask.reshape(1,-1)

        # Flatten arrays to 1D for storage
        flat_ids = padded_input_ids.flatten()
        flat_mask = padded_attention_mask.flatten()

        # Add input_ids and attention_mask attributes
        input_ids_attr = geo.addArrayAttrib(hou.attribType.Point, "input_ids", hou.attribData.Int, len(flat_ids))
        attention_mask_attr = geo.addArrayAttrib(hou.attribType.Point, "attention_mask", hou.attribData.Int, len(flat_mask))
        # Set the attributes of the point
        # point.setAttribValue(input_ids_attrib, ids)
        # point.setAttribValue(input_ids_attrib, [0,0,0])
        # geo.setGlobalAttribValue(input_ids_attr, padded_input_ids)
        # point.setAttribValue(attention_mask_attrib, mask)
       # geo.setGlobalAttribValue("input_ids", flat_ids)


    else: 
        raise hou.NodeError(f"Id-Mask length error. Length of Ids: {len(ids)}, Length of Masks: {len(mask)}")