from psd_tools import PSDImage
from instances import Instance
from properties import color3, colorSequence, read_color, read_gradientColor
from util import findEffect

Supported_affects = ["GradientOverlay", "ColorOverlay", "Stroke"]

def AddEffects(layer: PSDImage, instance: Instance, top: Instance):
    stroke_overlay_effect = findEffect(layer, "stroke")
    if stroke_overlay_effect:
        if layer.kind == "shape":
            instance.AddChild(Instance("UIStroke", {
				"Color": color3(read_color(stroke_overlay_effect.color)),
				"Thickness": stroke_overlay_effect.size
			}, top))
    
    color_overlay_effect = findEffect(layer, "coloroverlay")
    if color_overlay_effect:
        if layer.kind == "shape":
            instance.properties["BackgroundColor3"] = color3(read_color(color_overlay_effect.color))
    
    gradient_overlay_effect = findEffect(layer, "gradientoverlay")
    if gradient_overlay_effect:
        if layer.kind == "shape":
            instance.properties["BackgroundColor3"] = color3([255,255,255])
        instance.AddChild(Instance("UIGradient", {
            "Color": colorSequence(read_gradientColor(gradient_overlay_effect.gradient)),
            "Rotation": -1 * gradient_overlay_effect.angle
        }, top)) 