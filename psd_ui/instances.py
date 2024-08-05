import json
from properties import add_scale_to_rich_text, color3, get_font_sizes, get_max_front_size, readTransparency, rem, udim, udim2, read_color, rich_text_to_html, get_size, get_position
from psd_tools.constants import Tag
from constants import default_image_holder

class Instance:
    children: list
    
    def __init__(self, classname: str, properties, top = None):
        self.classname = classname
        self.properties = properties
        self.children = []
        self.top = top

    def AddChild(self, child):
        self.children.append(child)
        return child

    def ToDict(self):
        return {
            "ClassName": self.classname,
            "Properties": self.properties,
            "Children": [child.ToDict() for child in self.children]
        }
    def ToValue(self, key, value):
        if isinstance(value, str):
            if key == "Color":
                return f'Color3.fromRGB({value})'
            elif key == "BackgroundColor3":
                return f'Color3.fromRGB({value})'
            elif key == "Text":
                if self.top.classname is not "SurfaceGui":
                    return f"`{add_scale_to_rich_text(value, self.properties.get('TextScaled', False))}`"
            return f'\'{value}\''
        if isinstance(value, bool):
            return f'{value}'.lower()
        if isinstance(value, float):
            if key == "Thickness" and not (self.top is not None and self.top.classname == "SurfaceGui"):
                return rem(value)
            return f'{value}'
        if isinstance(value, list):
            if key == "CornerRadius":
                if value[1] > 0:
                    return f'new UDim({value[0]}, {rem(value[1])})'
                return f'new UDim({value[0]}, {value[1]})'
            elif key == "Size":
                if value[1] == 0 or value[3] == 0:
                    return f'UDim2.fromScale({value[0]}, {value[2]})'
                if value[0] == 0 or value[2] == 0:
                     return f'UDim2.fromOffset({rem(value[1])}, {rem(value[3])})'
                return f'new UDim2({value[0]}, {rem(value[1])}, {value[2]}, {rem(value[3])})'
            elif key == "Position":
                if value[1] == 0 or value[3] == 0:
                    return f'UDim2.fromScale({value[0]}, {value[2]})'
                if value[0] == 0 or value[2] == 0:
                     return f'UDim2.fromOffset({rem(value[1])}, {rem(value[3])})'
                return f'new UDim2({value[0]}, {rem(value[1])}, {value[2]}, {rem(value[3])})'
            elif key == "Color":
                return f'new ColorSequence([{", ".join([f"new ColorSequenceKeypoint({value[0]}, Color3.fromRGB({value[1]}))" for value in value])}])'
            else:
                print(f'{key} isn\'t supported yet.')
                return "undefined"
        return value
    def ToProperties(self):
        return " ".join([f'{key}={{{self.ToValue(key, value)}}}' for key, value in self.properties.items()])
    
    def ToChildren(self, indent=None):
        if indent is None:
            indent = 0
        return "".join([child.ToTSX(indent) for child in self.children])
    
    def ToTSX(self, indent=None):
        if indent is None:
            indent = 0
        key = self.properties.get("Name", None)
        if key is not None:
            del self.properties["Name"]
        classname = self.classname.lower()
        properties = self.ToProperties()
        childrens = self.ToChildren(indent + 4)
        
        if childrens == "":
            if key is None:
                return f"{' ' * indent}<{classname} {properties}/>\n"
            return f"{' ' * indent}<{classname} key=\"{key}\" {properties}/>\n"
        if key is None:
            return f"{' ' * indent}<{classname} {properties}>\n{childrens}{' ' * indent}</{classname}>\n"
        return f"{' ' * indent}<{classname} key=\"{key}\" {properties}>\n{childrens}{' ' * indent}</{classname}>\n"
  
    def ToJSON(self):
        return json.dumps(self.ToDict())

class GuiObject(Instance):
    def __init__(self, layer, classname, parent = None, top = None, scale: int = 1):
        Instance.__init__(self, classname, {
            "Name": layer.name,
            "Size": udim2(get_size(layer, scale)),
            "Position": udim2(get_position(layer, scale))
        }, top)
            
        if layer.visible == False:
            self.properties["Visible"] = False
  
class Frame(GuiObject):
    def __init__(self, layer, top = None):
        GuiObject.__init__(self, layer, "Frame")
        self.properties["BorderSizePixel"] = 0
        
        self.properties["BackgroundTransparency"] = readTransparency(layer)
        
        vector_stroke_content_data = layer.tagged_blocks.get_data(Tag.VECTOR_STROKE_CONTENT_DATA)
        if vector_stroke_content_data is not None:
            self.properties["BackgroundColor3"] = color3(read_color(vector_stroke_content_data.get(b'Clr ', {})))
        
        if layer.kind == "shape":
            shape = next(iter(layer.origination))
            if shape is not None and hasattr(shape, "radii"):
                self.AddChild(Instance("UICorner", {
                    "CornerRadius": udim([round(float(max(shape.radii.values()))/min(layer.size), 2), 0])
                }, top))
                
                
  
class ImageLabel(GuiObject):
    def __init__(self, layer):
        GuiObject.__init__(self, layer, "ImageLabel")
        
        self.properties["BackgroundTransparency"] = 1
        if layer.name.lower() == "icon":
            self.properties["Image"] = default_image_holder
        else:
            self.properties["Image"] = f'rbxgameasset://Images/{layer.name}'

class TextLabel(GuiObject):
    def __init__(self, layer, parent, top):
        font_sizes = get_font_sizes(layer)
        max_front_size = max(get_max_front_size(font_sizes),  layer.size[1])
        scale = round(max_front_size)/layer.size[1]
        
        
        GuiObject.__init__(self, layer, "TextLabel", parent, top, scale=scale)
        
        if len(font_sizes) == 1:
            self.properties["TextScaled"] = True
            self.properties["TextXAlignment"] = "Left"
        
        self.properties["BackgroundTransparency"] = 1
        self.properties["RichText"] = True
        self.properties["Text"] = rich_text_to_html(layer)

class CanvasGroup(GuiObject):
	def __init__(self, layer):
		GuiObject.__init__(self, layer, "Frame") ## CanvasGroup
  
		self.properties["BackgroundTransparency"] = 1