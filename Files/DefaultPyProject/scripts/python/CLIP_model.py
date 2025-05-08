import hou
import toolutils
import tempfile
from PIL import Image


def make_flipbook(start, end, camera_node, filename = ''):
    # Init Scene
    scene : hou.SceneViewer = toolutils.sceneViewer()
    view : hou.GeometryViewport = scene.curViewport()

    # Set Camera
    view.setCamera(camera_node)

    # Create a temporary file if filename is not provided
    if filename is None:
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        filename = temp_file.name
        temp_file.close()

    # Flipbook settings
    flip_options :hou.FlipbookSettings = scene.flipbookSettings().stash()
    flip_options.frameRange((start,end))
    flip_options.output(filename)

    # Use camera resoltion if available
    if scene.curViewport().camera():
        flip_options.useResolution(True)
        flip_options.resolution((scene.curViewport().camera().evalParm('resx'), scene.curViewport().camera().evalParm('resy') ))
        flip_options.cropOutMaskOverlay(True)
  
    # Create Flipbook
    scene.flipbook(view, flip_options)
    
    return filename

node = hou.pwd()
geo : hou.Geometry = node.geometry()
geo.addAttrib(hou.attribType.Point, "class", "")
geo.addAttrib(hou.attribType.Point, "prob", 0.0)
geo.addAttrib(hou.attribType.Point, "camera", "")

# %% Zero-shot classification
def run_model(model, processor, image_filename, classes):
    image = Image.open(image_filename)
    inputs = processor(text=classes, images=image, return_tensors="pt", padding=True)

    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
    probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities
    probs = probs[0].detach().numpy()

    """for id in range(len(probs)):
        point : hou.Point = geo.createPoint()
        point.setAttribValue("class", classes[id])
        point.setAttribValue("prob", float(probs[id]))"""
    
    return probs