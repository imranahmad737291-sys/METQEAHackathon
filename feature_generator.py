


# from config import setup_genai
# import google.generativeai as genai

# # Initialize Gemini model (configured globally)
# setup_genai()
# model = genai.GenerativeModel("gemini-2.0-flash")

# def generate_feature_file(requirement_text):
#     prompt = f"""
#     Generate a Cucumber Gherkin feature file from the following requirement.
#     Include positive, negative, and regression scenarios:

#     {requirement_text}
#     """
#     response = model.generate_content(prompt)
#     return response.text

# def generate_step_definitions(requirement_text, language="Python"):
#     prompt = f"""
#     Based on the following requirement, generate step definitions in {language}:

#     {requirement_text}
#     """
#     response = model.generate_content(prompt)
#     return response.text

# updated after xpath code



import re
from config import setup_genai
import google.generativeai as genai

# Initialize Gemini model (configured globally)
setup_genai()
model = genai.GenerativeModel("gemini-2.0-flash")

def clean_feature_file(text: str) -> str:
    """
    Keep only lines starting with valid Gherkin keywords or tags.
    """
    valid_keywords = [
        "Feature:", "Scenario:", "Scenario Outline:", "Background:",
        "Given", "When", "Then", "And", "But", "Examples:", "@"
    ]
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.lstrip()
        if any(stripped.startswith(kw) for kw in valid_keywords):
            cleaned.append(line)
    return "\n".join(cleaned)

def generate_feature_file(requirement_text):
    prompt = f"""
    Generate a Cucumber Gherkin feature file from the following requirement.
    Include positive, negative, and regression scenarios:

    {requirement_text}
    """
    response = model.generate_content(prompt)
    feature_content = clean_feature_file(response.text)
    return feature_content

def generate_step_definitions(requirement_text, language="Python"):
    prompt = f"""
    Based on the following requirement, generate step definitions in {language}:

    {requirement_text}
    """
    response = model.generate_content(prompt)
    return response.text


