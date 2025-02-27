import numpy as np
import hou
from PIL import Image

def preprocess_image_for_clip(grid_node, target_size=None):
    
    # TODO delete
    grid_node : hou.SopNode = hou.pwd()

    #Node reference paths
    node_path = "/obj/geo1/image_encode"
    rows_parameter_name = "input_shape13"
    columns_parameter_name = "input_shape14"

    #If target size is not specified, retrive from ONNX node
    if target_size is None:
        onnx_node : hou.SopNode = hou.node(node_path)
        row_parameter : hou.Parm = onnx_node.parm(rows_parameter_name)
        columns_parameter : hou.Parm = onnx_node.parm(columns_parameter_name)
        if row_parameter and columns_parameter:
            height = row_parameter.eval()
            width = columns_parameter.eval()
            target_size = (height,width)
    
    #Default to 336x336 if size isn't determined
    if target_size is None:
        target_size = (336,336)

    height,width = target_size

    # Get the grid geometry
    geo : hou.Geometry = grid_node.geometry()

    #Get color attribute of grid
    color_attrib = geo.findPointAttrib("Cd")

    #Create image array with target dimensions
    image_np = np.zeros((height,width,3), dtype=np.float32)

    points = geo.points()
    point : hou.Point

    for point in points:
        pos = point.position()
        