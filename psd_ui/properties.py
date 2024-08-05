import re
import psd_tools
from psd_tools import PSDImage
from util import findEffect

use_scale = True

def udim(arr):
    return [round(value, 2) for value in arr]

def udim2(arr):
    return [round(value, 2) for value in arr]

def color3(arr):
    return ", ".join(map(str, arr))

def rem(value, mode: str = "pixel"):
    return f'rem({value}, "{mode}")'

def colorSequence(sequences):
    ColorSequenceKeypoints = []
    for sequence in sequences:
        ColorSequenceKeypoints.append([sequence[0], color3(sequence[1])])
    return ColorSequenceKeypoints

def readAffectTransparency(layer):
   return 1-(layer.opacity / 100)

def readTransparency(layer):
   return 1-(layer.opacity / 255)

def hex_color(color_values):
    return '#{0:02X}{1:02X}{2:02X}'.format(int(color_values[0]), int(color_values[1]), int(color_values[2]))

def add_scale_to_rich_text(text: str, remove_size: bool = False):
    def replace_size(match):
        size_value = float(match.group(1))
        if remove_size:
            return ''
        return f' size="${{math.round({rem(size_value)})}}"'
    
    def replace_thickness(match):
        size_value = float(match.group(1))
        return f' thickness="${{{rem(size_value)}}}"'

    size_pattern = r' size="(\d+)"'
    thickness_pattern = r' thickness="(\d+(\.\d+)?)"'

    modified_text = re.sub(size_pattern, replace_size, text)
    modified_text = re.sub(thickness_pattern, replace_thickness, modified_text)

    return modified_text

font_list = ["FredokaOne", "LuckiestGuy"]

def remove_extra_spaces(text):
    # Use a regular expression to replace multiple consecutive spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text

def get_size(layer, scale = 1):
    size = [0, layer.size[0] * scale, 0, layer.size[1] * scale]
    if use_scale:
        size  = [1, 0, 1, 0]
    
    if layer.parent and use_scale:
        parent_size = [0, layer.parent.size[0], 0, layer.parent.size[1]]
        size =  [(layer.size[0]*scale)/parent_size[1], 0, (layer.size[1]*scale)/parent_size[3], 0]
    
    return size

def get_position(layer, scale = 1):
    position = [0, layer.offset[0], 0, layer.offset[1]]
    if layer.parent:
        parent_size = [0, layer.parent.size[0], 0, layer.parent.size[1]]
        parent_position = [0, layer.parent.offset[0], 0, layer.parent.offset[1]]
        position = [0, position[1] - parent_position[1], 0, position[3] - parent_position[3]]
        if use_scale:
            position = [(position[1]*scale)/parent_size[1], 0, position[3]/parent_size[3], 0]
            
    return position


def get_font_sizes(layer):
    rundata = layer.engine_dict['StyleRun']['RunArray']
    font_sizes = set()
    color_values = set()
    stroke_values = set()

    for style in rundata:
        stylesheet = style['StyleSheet']['StyleSheetData']
        font_sizes.add(float(stylesheet['FontSize'] * layer.transform[0]))
        
    return font_sizes

def get_max_front_size(sizes):
    return max(0, max(sizes))
    

def rich_text_to_html(layer):
    text = layer.engine_dict['Editor']['Text'].value
    fontset = layer.resource_dict['FontSet']
    runlength = layer.engine_dict['StyleRun']['RunLengthArray']
    rundata = layer.engine_dict['StyleRun']['RunArray']
    index = 0
    html_text = []

    # Check for ColorOverlay effect
    color_overlay_effect = findEffect(layer, "coloroverlay")
    
    # Check for GradientOverlay effect
    gradient_overlay_effect = findEffect(layer, "gradientoverlay")
    
    # Check for Stroke effect
    stroke_effect = findEffect(layer, "stroke")
    stroke_thickness = 1
    
    if layer.parent.is_group() and not isinstance(layer.parent, PSDImage) and layer.parent.has_effects():
        if color_overlay_effect is None:
            color_overlay_effect = findEffect(layer.parent, "coloroverlay")
        
        if stroke_effect is None:
            stroke_effect = findEffect(layer.parent, "stroke")
                        
    for length, style in zip(runlength, rundata):
        substring = text[index:index + length]
        stylesheet = style['StyleSheet']['StyleSheetData']
        font_index = stylesheet['Font']
        font = fontset[font_index]
        font_name = font['Name']
        font_size = float(stylesheet['FontSize']) # Round font size to the nearest integer
        is_bold = stylesheet.get('FauxBold', False)  # Check if faux bold styling is applied
        color_values = stylesheet.get('FillColor', {}).get('Values', [1.0, 1.0, 1.0, 1.0])[1:]  # Default color is white and the first value is the opacity
        stroke_values = stylesheet.get('StrokeColor', {}).get('Values', [1.0, 1.0, 1.0, 1.0])  # Default color is white and the first value is the opacity
        
        # Use ColorOverlay effect color if present
        if gradient_overlay_effect:
            color_values = [1,1,1]
        elif color_overlay_effect:
            color_overlay_values = read_color(color_overlay_effect.color)
            color_values = [value / 255.0 for value in color_overlay_values]
            
        if stroke_effect:
            stroke_effect_values = read_color(stroke_effect.color)
            stroke_thickness = stroke_effect.size
            stroke_values = [readAffectTransparency(stroke_effect)] + [value / 255.0 for value in stroke_effect_values]
            
        # Find the best-matching font from the provided font list
        closest_font = closest_name(str(font_name), font_list)
                
        html_tag = f'<font face="{closest_font}" size="{round(font_size * layer.transform[0])}" color="{hex_color([value * 255.0 for value in color_values])}">{substring[:-1]}</font>'
        if is_bold:
            html_tag = f'<b>{html_tag}</b>'

        # Stroke attributes
        if stroke_values[0] < 1 and stroke_thickness > 0:
            html_tag = f'<stroke color="{hex_color([value * 255.0 for value in stroke_values[1:]])}" thickness="{stroke_thickness}"{f' transparency="{stroke_values[0]}' if stroke_values[0] > 0 else ""}>{html_tag}</stroke>'

        html_text.append(html_tag)

        index += length

    return ''.join(html_text)
    


def read_color(color):
    return [int(value) for value in list(color.values())]

def closest_name(input_name, name_list):
    closest_match = min(name_list, key=lambda name: levenshtein_distance(input_name, name))
    return closest_match

def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
        distances = new_distances

    return distances[-1]

def LerpColor(current, goal, delta):
    return [(current[0] + goal[0]) * delta,(current[1] + goal[1]) * delta,(current[2] + goal[2]) * delta]

def read_gradientColor(gradient_data):
    colors = gradient_data.get(b'Clrs', [])

    color_points = []
    midpoint_color = None
    index = 0

    for color_point in colors:
        color = read_color(color_point.get(b'Clr ', {}))  # Note the space after 'Clr'
        location = int(color_point.get(b'Lctn', psd_tools.psd.descriptor.Integer(0)).value / 4096.0 * 100 + 0.5)  # Adjusted location to represent percentage
        midpoint = color_point.get(b'Mdpn', psd_tools.psd.descriptor.Integer(0)).value  # Default opacity to 100 if not present
            
        if midpoint_color is not None:
            color_points.append([midpoint/100, midpoint_color])
            midpoint_color = None
        else:
            next_color = read_color(colors[index + 1].get(b'Clr ', {}))
            midpoint_color = LerpColor(color, next_color, midpoint/100)
            
        color_points.append([location/100, color])
        index += 1
    
    return color_points