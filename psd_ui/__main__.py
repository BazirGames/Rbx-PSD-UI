import argparse
from process import main as process

""" parser = argparse.ArgumentParser()
parser.add_argument("psd", type=str, help="The relative path to the psd file.")
args = parser.parse_args() """

print("Processing PSD...")
process("Example.psd", "images") 
""" (args.psd) """
print("PSD successfully processed.")