from config import setup_genai
from feature_generator import generate_feature_file
from script_generator import generate_script_structure
import os

def read_requirement(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def save_feature_file(content, path):
    with open(path, 'w') as f:
        f.write(content)

def create_script_structure(structure, base_path):
    for folder in structure['folder_structure']:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    for path, content in structure['files_to_create'].items():
        full_path = os.path.join(base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    setup_genai(api_key='YOUR_GEMINI_API_KEY')
    requirement = read_requirement('input/sample_requirement.txt')
    feature_content = generate_feature_file(requirement)
    save_feature_file(feature_content, 'output/features/generated.feature')
    structure = generate_script_structure(requirement)
    create_script_structure(structure, 'output/scripts')
