from generator_js import generate_js

def generate(transformed, lang):
    if lang == "js":
        return generate_js(transformed)
