import os
import argparse
from dotenv import load_dotenv
from pathlib import Path
from Ollama_chatbot.constants.prompt import SYSTEM_PAPER_EVALUATION_PROMPT
from Ollama_chatbot.components.text_extraction import extract_text_from_pdf
from Ollama_chatbot.components.session import Session


def parse_args():
    parser = argparse.ArgumentParser(description="Path to your pdf location to test it against LLM")
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to you pdf file"
    )

    return parser.parse_args()

def main():
    load_dotenv()
    args = parse_args()
    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        raise FileNotFoundError("File not found on {pdf_path}")
        sys.exit(1)
    
    print("Extracting Text...")

    extracted = extract_text_from_pdf(str(pdf_path))
    full_text = extracted['full_text']

    print("Running LLM session")

    session = Session(system_prompt = SYSTEM_PAPER_EVALUATION_PROMPT)
    session.query = full_text
    result = session.run()

    print("\n LLM Output: \n")
    print(result)

if __name__ == "__main__":
    main()
