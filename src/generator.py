import os
import sys

# neccessary on windows so that generator can find generator_js when called from spark.py
# for whatever reason
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from generator_js import generate_js

def generate(transformed, lang):
    if lang == "js":
        return generate_js(transformed)
