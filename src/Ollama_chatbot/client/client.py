from openai import OpenAI
import os

def get_openai_client() -> OpenAI:
    api_key = os.getenv("SECRET_KEY")
    if not api_key:
        raise RuntimeError("Secret Key Not Set")
    return OpenAI(api_key = api_key)