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


def preprocess_image(grid_node, preprocessor_json = None):
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
        raise hou.NodeWarning("Using default CLIP settings")
    elif isinstance(preprocessor_json, str):
        config = load_preprocessor_config(preprocessor_json)
    else:
        config = preprocessor_json

    # Initialize parameters to extract from config
    image_size = None 
    mean = None 
    std = None

    # Extract parameters from config
    for stage in config.get("stages",[]):
        if stage.get("type") == "center_crop":
            image_size = stage.get("size")
        elif stage.get("type") == "normalize":
            mean = stage.get("mean")
            std = stage.get("std")

    # Convert mean and std to numpy array
    mean_np = np.array(mean)
    std_np = np.array(std)

    # Handle missing values after parsing config
    if None in (image_size, mean, std):
        raise hou.NodeError(f"Config values missing. Image Size: {image_size}, mean: {mean}, std: {std}")
    
    # Get the grid geometry
    geo : hou.Geometry = grid_node.geometry()
    
    # Add tensor attribute
    tensor_attrib = geo.addAttrib(hou.attribType.Point, "tensor_data", (0.0, 0.0, 0.0))

    # Get color attribute of grid
    color_attrib = geo.findPointAttrib("Cd")

    # Apply mean and std to each point
    points = geo.points()
    point : hou.Point

    for point in points:
        color = point.attribValue(color_attrib)
        color = np.array(color)
        color = (color - mean_np) / std_np

        point.setAttribValue(tensor_attrib, (
                    float(color[0]),
                    float(color[1]),
                    float(color[2])
                ))


"""def preprocess_image_for_clip(grid_node, preprocessor_json = None):
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
        raise hou.NodeWarning("Using default CLIP settings")
    elif isinstance(preprocessor_json, str):
        config = load_preprocessor_config(preprocessor_json)
    else:
        config = preprocessor_json

    # Initialize parameters to extract from config
    image_size = None 
    mean = None 
    std = None

    # Extract parameters from config
    for stage in config.get("stages",[]):
        if stage.get("type") == "center_crop":
            image_size = stage.get("size")
        elif stage.get("type") == "normalize":
            mean = stage.get("mean")
            std = stage.get("std")

    # Handle missing values after parsing config
    if None in (image_size, mean, std):
        raise hou.NodeError(f"Config values missing. Image Size: {image_size}, mean: {mean}, std: {std}")
    
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

    # Apply normilization if not in 0-1 color range
    if np.max(image_np) > 1.0:
        image_np = image_np/255.0

    mean_np = np.array(mean)
    std_np = np.array(std)
    image_np = (image_np - mean_np) / std_np

    # Reorder RGB format
    image_np = np.transpose(image_np,(2,0,1))
    image_np = np.expand_dims(image_np, axis=0)
  
    return image_np

def tensor_to_point_attributes(image_np, target_geo : hou.Geometry, attribute_name="tensor_data"):
    # Remove batch dimension and transpose back to [height, width, channels]
    tensor_data = np.transpose(image_np[0], (1, 2, 0))
    
    # Get dimensions
    height, width, channels = tensor_data.shape
    
    # Create float attribute if it doesn't exist
    tensor_attrib = target_geo.findPointAttrib(attribute_name)
    if tensor_attrib is None:
        tensor_attrib = target_geo.addAttrib(hou.attribType.Point, attribute_name, (0.0, 0.0, 0.0))
    
    # Get all points
    points = target_geo.points()
    point : hou.Point
    
    # Set attribute values for each point based on position
    for point in points:
        pos = point.position()
        i = int((1.0 - pos[1]) * (height-1))    # Y coordinate
        j = int(pos[0] * (width-1))             # X coordinate
        
        if 0 <= i < height and 0 <= j < width:
            # Get tensor values at this position (all channels)
            tensor_value = tensor_data[i, j, :]
            
            # Set attribute (first 3 channels if there are more)
            if channels >= 3:
                point.setAttribValue(tensor_attrib, (
                    float(tensor_value[0]),
                    float(tensor_value[1]),
                    float(tensor_value[2])
                ))
            else:
                # Handle case with fewer channels
                values = [float(tensor_value[c]) for c in range(min(3, channels))]
                while len(values) < 3:
                    values.append(0.0)  # Pad with zeros if needed
                point.setAttribValue(tensor_attrib, tuple(values))"""