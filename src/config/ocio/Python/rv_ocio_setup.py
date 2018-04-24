import rv
import os
import PyOpenColorIO as OCIO
from ingestor.ExpressionEvaluator import ExpressionEvaluator

# Convenience functions to set the values in the specific nodes
def setInt(node, prop, value):
    """Set an int property."""
    property = '{node}.{prop}'.format(node=node, prop=prop)
    rv.commands.setIntProperty(property, [value], True)


def getInt(node, prop):
    """Get an int property."""
    property = '{node}.{prop}'.format(node=node, prop=prop)
    return rv.commands.getIntProperty(property, 0, 1)[0]


def setFloat(node, prop, value):
    """Set a float property."""
    property = '{node}.{prop}'.format(node=node, prop=prop)
    rv.commands.setFloatProperty(property, [float(value)], True)


def getFloat(node, prop):
    """Get a float property."""
    property = '{node}.{prop}'.format(node=node, prop=prop)
    return rv.commands.getFloatProperty(property, 0, 1)[0]


def getString(node, prop):
    """Get a string property."""
    property = '{node}.{prop}'.format(node=node, prop=prop)
    return rv.commands.getStringProperty(property, 0, 1)[0]


def setString(node, prop, value):
    """Set a string property."""
    property = '{node}.{prop}'.format(node=node, prop=prop)
    rv.commands.setStringProperty(property, [value], True)


def setComponent(node, prop, value):
    """Set a component property."""
    for k, v in value.items():
        component = '{node}.{prop}.{key}'.format(node=node, prop=prop, key=k)
        if not rv.commands.propertyExists(component):
            rv.commands.newProperty(component, rv.commands.StringType, 1)
        keyProperty = '{prop}.{key}'.format(prop=prop, key=k)
        setString(node, keyProperty, v)


def groupMemberOfType(node, memberType):
    """Get a group member of specific type."""
    for n in rv.commands.nodesInGroup(node):
        if rv.commands.nodeType(n) == memberType:
            return n
    return None


def ocio_config_from_media(*args, **kwargs):
    """
    Override the original 'ocio_config_from_media' from the 'ocio_source_setup' plugin.

    This functions sets the open color io config file. It resolves the path base on the loaded file.
    """
    media = rv.commands.sources()[0][0]
    config_file = ExpressionEvaluator.run('rfindpath', 'config/OCIO/config.ocio', media)
    return OCIO.Config.CreateFromFile(config_file)


def ocio_node_from_media(config, node, default, media=None, attributes=None):
    """
    Override the original 'ocio_node_from_media' from the 'ocio_source_setup' plugin.

    This function sets the usage of the views and color spaces in RV.
    RVDisplayPipelineGroup - Viewer setup
    RVLinearizePipelineGroup - Color space setup
    RVLookPipelineGroup - Look setup
    """
    result = [{"nodeType": d, "context": {}, "properties": {}} for d in default]

    nodeType = rv.commands.nodeType(node)

    if (nodeType == "RVDisplayPipelineGroup"):
        # The display is always the color viewer, the color space in the ocio will set the final color space
        media = rv.commands.sources()[0][0]
        sg, _, projectName = getDataFromMedia(media)
        sgProject = sg.find_one(
            'Project',
            [['name', 'is', projectName]],
            ['sg_rvcolorspaceviewer']
        )

        viewer = str(sgProject['sg_rvcolorspaceviewer'])

        display = config.getDefaultDisplay()
        result = [
            {
                "nodeType": "OCIODisplay",
                "context": {},
                "properties": {
                    "ocio.function": "display",
                    "ocio_display.view": viewer,
                    "ocio_display.display": display
                }
            }
        ]

    elif (nodeType == "RVLinearizePipelineGroup"):
        if not media:
            return result
        sg, _, projectName = getDataFromMedia(media)
        # This is not the right way to do it, but in the future we will have the ids instead of the names
        sgProject = sg.find_one(
            'Project',
            [['name', 'is', projectName]],
            ['sg_showcolorspacestudio', 'sg_showcolorspaceclient']
        )

        # Color space in
        colorSpaceStudio = str(sgProject['sg_showcolorspacestudio'])
        # Color space out
        colorSpaceClient = str(sgProject['sg_showcolorspaceclient'])

        result = [
            {
                "nodeType": "OCIOFile",
                "context": {},
                "properties": {
                    "ocio.function": "color",
                    "ocio.inColorSpace": colorSpaceStudio,
                    "ocio_color.outColorSpace": colorSpaceClient
                }
            }
        ]

    elif (nodeType == "RVLookPipelineGroup"):
        # We don't need to set the looks for so we can bypass this method (leave it to know it's a possiblity)
        pass

    return result


def getDataFromMedia(media):
    """
    Get the shotgun session, shotname and project name base on the loaded file.
    """
    from ushotgun import Session
    sg = Session.get()
    shotName = os.path.basename(media).split('_')[0]
    projectName = shotName.split('-')[0]

    return (sg, shotName, projectName)
