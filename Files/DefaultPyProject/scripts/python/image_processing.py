import numpy as np
import hou
import json
import os

def load_preprocessor_config(json_path):
    # Read preprocessing configuration from json
    if os.path.exists(json_path):
        with open(json_path,'r') as f:
            config = json.load(f)
    else:
        # Display file not found message
        config = None
        raise hou.NodeError("Cannot find the JSON file: preprocessor.json")
    return config


def preprocess_image_for_clip(grid_node, preprocessor_json = None):
    
    # TODO delete
    grid_node : hou.SopNode = hou.pwd()

    if preprocessor_json is None:
        # Default CLIP settings
        config = {
            "stages": [
                {"type": "resize", "size": 336},
                {"type": "center_crop", "size": [336, 336]},
                {"type": "normalize", "mean": [0.48145467, 0.45782751, 0.40821072], 
                                        "std": [0.26862955, 0.26130259, 0.27577711]}
            ]
        }
    elif isinstance(preprocessor_json, str):
        config = load_preprocessor_config(preprocessor_json)
    else:
        config = preprocessor_json

    # Initialize parameters to extract from config
    image_size, mean, std = None

    # Extract parameters from config
    for stage in config.get("stages",[]):
        if stage.get("type") == "center_crop":
            image_size = stage.get("size")
        elif stage.get("type") == "normalize":
            mean = stage.get("mean")
            std = stage.get("std")

    # Handle missing values after parsing config
    if image_size or mean or std is None:
        raise hou.NodeError("Config values missing")
    
    height, width = image_size

    # Get the grid geometry
    geo : hou.Geometry = grid_node.geometry()

    # Get color attribute of grid
    color_attrib = geo.findPointAttrib("Cd")

    # Create image array with target dimensions
    image_np = np.zeros((height,width,3), dtype=np.float32)

    points = geo.points()
    point : hou.Point

    # Convert color data format
    for point in points:
        pos = point.position()
        i = int((1.0 - pos[1]) * (height-1))    # Y coordinate
        j = int(pos[0] * (width-1))             # X coordinate
        
        # Get color value
        if 0<= i < height and 0 <= j < width:
            color = point.attribValue(color_attrib)
            image_np[i,j,0] = color[0]  # R
            image_np[i,j,1] = color[1]  # G
            image_np[i,j,2] = color[2]  # B

    # Apply normilization
    if np.max(image_np) > 1.0:
        image_np = image_np/255.0
        
    mean_np = np.array(mean)
    std_np = np.array(std)
    image_np = (image_np - mean_np) / std_np

    # Reorder RGB format
    image_np = np.transpose(image_np,(2,0,1))
    image_np = np.expand_dims(image_np, axis=0)

    return image_np