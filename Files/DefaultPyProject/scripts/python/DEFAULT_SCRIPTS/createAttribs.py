import hou

def main():
    node : hou.SopNode = hou.pwd()
    geo : hou.Geometry = node.geometry()

    # Point Attributes
    geo.addAttrib(hou.attribType.Point, "pointAttribFloat", 0.0)
    geo.addAttrib(hou.attribType.Point, "pointAttribInt", 0)
    geo.addAttrib(hou.attribType.Point, "pointAttribString", "")
    for point in geo.points():
        point.setAttribValue("pointAttribString", "piece" + str(point.number()))

    # Prim Attributes
    geo.addAttrib(hou.attribType.Prim, "primAttribFloat", 0.0)
    geo.addAttrib(hou.attribType.Prim, "primAttribInt", 0)
    geo.addAttrib(hou.attribType.Prim, "primAttribStr", "")
    for prim in geo.prims():
        prim.setAttribValue("primAttribStr", "piece" + str(prim.number()))

    # Vertex Attributes
    geo.addAttrib(hou.attribType.Vertex, "vertexAttribFloat", 0.0)
    geo.addAttrib(hou.attribType.Vertex, "vertexAttribInt", 0)
    geo.addAttrib(hou.attribType.Vertex, "vertexAttribStr", "")
    length = "0-" + str(len(geo.prims())-1)
    for vert in geo.globVertices(length):
        vert.setAttribValue("vertexAttribStr", "piece" + str(vert.number()))
    
    # Detail Attributes
    geo.addAttrib(hou.attribType.Global, "globalAttribFloat", 0.0)
    geo.addAttrib(hou.attribType.Global, "globalAttribInt", 0)
    geo.addAttrib(hou.attribType.Global, "globalAttribStr", "")
    geo.setGlobalAttribValue("globalAttribStr", "value")