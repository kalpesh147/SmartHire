# agents/jd_builder.py

import requests

# Ollama API endpoint (make sure your model is running locally)
OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_jd(title, skills, responsibilities, education):
    """
    Generate a job description using Ollama's LLM based on the provided inputs.
    """
    # Create the prompt
    prompt = f"""
    Write a professional job description for the role of '{title}'.
    
    The description should include the following sections:
    
    1. **Job Title**: {title}
    2. **Key Responsibilities**: {responsibilities}
    3. **Required Skills**: {skills}
    4. **Educational Requirements**: {education}
    5. **About the Company**: Add a generic paragraph if not specified.

    Make it structured and HR-friendly.
    """

    # Payload for the Ollama API
    payload = {
        "model": "llama3",  # or any other model you've pulled locally
        "prompt": prompt.strip(),
        "stream": False
    }

    # Make the request to Ollama
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response from model.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to generate job description: {str(e)}")
