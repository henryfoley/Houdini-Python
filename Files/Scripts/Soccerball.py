import hou

parentnode : hou.SopNode = hou.node('/obj/geo1')

platonic : hou.SopNode = parentnode.createNode("platonic")
polyextrude : hou.SopNode = parentnode.createNode("polyextrude::2.0")
polybevel : hou.SopNode = parentnode.createNode("polybevel::3.0")

polyextrude.setNextInput(platonic)
polybevel.setNextInput(polyextrude)

platonic.parm("type").set(5)
polyextrude.parm("dist").set(0.092)
polyextrude.parm("splittype").set("elements")
polybevel.parm("offset").set(0.023)

polyextrude.moveToGoodPosition()
polybevel.moveToGoodPosition()

polybevel.setDisplayFlag(True)
polybevel.setRenderFlag(True)