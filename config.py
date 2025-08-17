# import google.generativeai as genai
# from dotenv import load_dotenv
# import os

# load_dotenv()  # Load variables from .env file

# def setup_genai():
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY not found in .env file")
#     genai.configure(api_key=api_key)


# import google.generativeai as genai

# def setup_genai(api_key):
#     genai.configure(api_key=api_key)

import google.generativeai as genai

def setup_genai():
    genai.configure(api_key="AIzaSyDofYpUJfHqKIVEIJ_cxrvZEC1IkgJ5ncg")



     



