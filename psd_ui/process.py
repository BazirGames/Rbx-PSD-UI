from psd_tools import PSDImage
from effects import AddEffects, Supported_affects
from instances import Instance, Frame, ImageLabel, TextLabel, CanvasGroup
from constants import default_image_holder
        
def LayerFrame(layer, parent: Instance, top: Instance):
    if layer.is_group():
        return CanvasGroup(layer)
    if layer.kind == "type":
        return TextLabel(layer, parent, top)
    if layer.kind == "psdimage" or layer.kind == "pixel" or layer.kind == "smartobject" or layer.has_clip_layers():
        return ImageLabel(layer)
    for effect in layer.effects:
        if effect.enabled and str(effect) not in Supported_affects:
            print(effect, "is not supported")
            return ImageLabel(layer)
    return Frame(layer, top)

def RecursiveFrame(top: Instance, parent: Instance, psd: PSDImage, images: dict):
    for layer in psd:    
        if layer.name == "IGNORE ME":
            continue
        
        print(layer.name, layer.kind, layer.effects)
        
        instance = parent.AddChild(LayerFrame(layer, parent, top))
        
        if len(parent.children) > 1:
            instance.properties["ZIndex"] = len(parent.children) - 1
            
        if not isinstance(instance, ImageLabel):
            if not layer.is_group() and layer.has_effects():
                AddEffects(layer, instance, top)       
            if layer.parent.is_group() and not isinstance(layer.parent, PSDImage) and layer.parent.has_effects():
                AddEffects(layer.parent, instance, top)
            if layer.is_group():
                RecursiveFrame(top, instance, layer, images)
        elif images.get(layer.name) == None and not instance.properties["Image"] == default_image_holder:
            images[layer.name] = layer
                
def ScreenGui(filename: str, psd: PSDImage, images: dict):
    screen = Instance("ScreenGui", {
        "Name": filename[:-4],
        "ResetOnSpawn": False,
        "ZIndexBehavior": "Sibling"
    })
    root = screen.AddChild(CanvasGroup(psd))
    root.AddChild(Instance("UIAspectRatioConstraint", {
        "AspectRatio": round(psd.size[0]/psd.size[1], 2)
    }))
    RecursiveFrame(screen, root, psd, images)
    return screen

def BillboardGui(filename: str, psd: PSDImage, images: dict):
    top = Instance("Folder", {
        "Name": filename[:-4]
    })
    for layer in psd:
        if layer.is_group():
            screen = top.AddChild(Instance("BillboardGui", {
                "Name": layer.name,
                "Active": True,
                "AlwaysOnTop": True,
                "LightInfluence": 1,
                "Size": [layer.size[0]/100, 0, layer.size[1]/100, 0],
                "ResetOnSpawn": False,
                "ZIndexBehavior": "Sibling"
            }))
            RecursiveFrame(screen, screen, layer, images)
            
    return top

def SurfaceGui(filename: str, psd: PSDImage, images: dict):
    top = Instance("Folder", {
        "Name": filename[:-4]
    })
    for layer in psd:
        if layer.is_group():
            screen = top.AddChild(Instance("SurfaceGui", {
                "Name": layer.name,
                "Active": True,
                "AlwaysOnTop": True,
                "LightInfluence": 1,
                "SizingMode": "PixelsPerStud",
                "ZIndexBehavior": "Sibling"
            }))
            root = screen.AddChild(CanvasGroup(psd))
            root.AddChild(Instance("UIAspectRatioConstraint", {
                "AspectRatio": round(psd.size[0]/psd.size[1], 2)
            }))
            RecursiveFrame(screen, root, layer, images)
            
    return top
             
 
def main(filename, imagedir):
    images = dict()
    psd = PSDImage.open(filename)
    """ psd.composite().save("images/" + filename[:-4] + ".png") """
    screen = ScreenGui(filename, psd, images)
    
    json = open("lua_src/ServerScriptService/Render/output.json", "w")
    json.write(screen.ToJSON())
    json.close()
    
    json = open("Tsx.text", "w")
    json.write(screen.ToTSX())
    json.close()
    
    for name, layer in images.items():
        print("Processing " + name)
        layer.composite().save(imagedir + "/" + name + ".png")
        print("successfully save " + name)
