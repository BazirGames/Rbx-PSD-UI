from psd_tools import PSDImage

def findEffect(layer: PSDImage, name: str):
    generator = layer.effects.find(name)
    for effect in generator:
        if effect.enabled:
            return effect