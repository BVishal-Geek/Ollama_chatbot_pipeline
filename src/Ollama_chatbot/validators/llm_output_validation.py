import json
from typing import Dict
from Ollama_chatbot.constants.schema import CONDITIONAL_KEYS

class LLMOutputValidationError(Exception):
    pass

def validate_llm_output(text: str) -> Dict[str, int]:
    '''
    Validating the output of the llm to check if its JSON
    
    Input
    text: str

    Return: Dict[str, int]
    '''

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise LLMOutputValidationError("LLM output is not valid")
    
    #checking if all the keys exist
    missing = set(CONDITIONAL_KEYS) - set(data.keys())

    if missing:
        raise LLMOutputValidationError(f"Missing keys: {missing}")

    #check for extra keys
    extra_keys = set(data.keys()) - set(CONDITIONAL_KEYS)

    if extra_keys:
        raise LLMOutputValidationError(f"Unexpected keys: {extra_keys}")
    
    #check if the value is only either 0 or 1 
    for key, value in data.items():
        if value not in (0,1):
            raise LLMOutputValidationError(f"Invalid key for {key}: {value} (expected 0 or 1)")

    return data 

def is_recommended(result:Dict[str, int]) -> bool:
    return all(value == 1 for value in result.values())