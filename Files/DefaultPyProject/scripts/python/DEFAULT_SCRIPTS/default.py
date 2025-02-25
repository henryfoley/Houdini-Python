import hou

# Default Script
node : hou.SopNode = hou.pwd()
geo : hou.Geometry = node.geometry()

# Add code to modify contents of geo.
# Use drop down menu to select examples.

def foo():
    print("File Working")