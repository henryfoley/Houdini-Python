import hou
import toolutils
import tempfile
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def make_flipbook(start, end, filename = ''):
    scene : hou.SceneViewer = toolutils.sceneViewer()
    view : hou.GeometryViewport = scene.curViewport()

    camera_path = "obj/cam1"
    camera_node : hou.GeometryViewportCamera = hou.node(camera_path)
    original_camera = view.camera()
    view.setCamera(camera_node)

    # Create a temporary file if filename is not provided
    if filename is None:
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        filename = temp_file.name
        temp_file.close()

    #Flipbook settings
    flip_options :hou.FlipbookSettings = scene.flipbookSettings().stash()
    flip_options.frameRange((start,end))
    flip_options.output(filename)

    #use camera resoltion if available
    if scene.curViewport().camera():
        flip_options.useResolution(True)
        flip_options.resolution((scene.curViewport().camera().evalParm('resx'), scene.curViewport().camera().evalParm('resy') ))
        flip_options.cropOutMaskOverlay(True)
  
    scene.flipbook(view, flip_options)

    # Restore the original camera
    if camera_path and original_camera:
        view.setCamera(original_camera)
    
    return filename

def load_image_as_variable(image_path):
    test = Image.open(image_path)
    return Image.open(image_path)

node = hou.pwd()
geo : hou.Geometry = node.geometry()
geo.addAttrib(hou.attribType.Point, "class", "")
geo.addAttrib(hou.attribType.Point, "prob", 0.0)

# %% Zero-shot classification
def run_model(image_filename):
    #image_filename = "images/hotdog.jpg"
    image = Image.open(image_filename)
    classes = ['pig', 'man', 'squid', 'hotdog']
    inputs = processor(text=classes, images=image, return_tensors="pt", padding=True)

    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
    probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities
    probs = probs[0].detach().numpy()

    for id in range(len(probs)):
        point : hou.Point = geo.createPoint()
        point.setAttribValue("class", classes[id])
        point.setAttribValue("prob", float(probs[id]))