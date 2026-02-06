# import os
# import argparse
# from dotenv import load_dotenv
# from pathlib import Path
# from Ollama_chatbot.constants.prompt import SYSTEM_PAPER_EVALUATION_PROMPT_V3
# from Ollama_chatbot.components.text_extraction import extract_text_from_pdf
# from Ollama_chatbot.validators.llm_output_validation import validate_llm_output, is_recommended
# from Ollama_chatbot.components.session import Session

# def parse_args():
#     parser = argparse.ArgumentParser(description="Path to your pdf location to test it against LLM")
#     parser.add_argument(
#         "--pdf",
#         type=str,
#         required=False,
#         help="Path to you pdf file"
#     )

#     parser.add_argument(
#         "--folder",
#         type=str,
#         required=False,
#         help="Path to folder containing multiple pdfs"
#     )

#     return parser.parse_args()

# def main():
#     load_dotenv()
#     args = parse_args()
#     pdf_path = Path(args.pdf)

#     if not pdf_path.exists():
#         raise FileNotFoundError("File not found on {pdf_path}")
#         sys.exit(1)
    
#     print("Extracting Text...")

#     extracted = extract_text_from_pdf(str(pdf_path))
#     full_text = extracted['full_text']

#     print("Running LLM session")

#     session = Session(system_prompt = SYSTEM_PAPER_EVALUATION_PROMPT_V3)
#     session.query = full_text
#     result = session.run()
#     validated_result = validate_llm_output(result)

#     print("\n LLM Output: \n")
#     print(validated_result)

#     print("\n Recommedation: \n")
#     if is_recommended(validated_result):
#         print("✅ Paper IS RECOMMENDED")
#     else:
#         print("❌ Paper IS NOT RECOMMENDED")

# if __name__ == "__main__":
#     main()

import os
import argparse
from dotenv import load_dotenv
from pathlib import Path
from Ollama_chatbot.constants.prompt import SYSTEM_PAPER_EVALUATION_PROMPT_V3
from Ollama_chatbot.validators.llm_output_validation import validate_llm_output, is_recommended
from Ollama_chatbot.components.session import Session

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate text files using LLM")
    parser.add_argument("--folder", type=str, required=True, help="Path to folder containing .txt files")
    parser.add_argument("--output-dir", type=str, required=True, help="Path to save results")
    return parser.parse_args()

def process_text_file(txt_path: Path, output_dir: Path):
    """Process a single text file."""
    try:
        print(f"Processing: {txt_path.name}")
        
        # Read text file
        with open(txt_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        # Run LLM
        session = Session(system_prompt=SYSTEM_PAPER_EVALUATION_PROMPT_V3)
        session.query = full_text
        result = session.run()
        validated_result = validate_llm_output(result)
        
        # Check recommendation
        recommendation = is_recommended(validated_result)
        
        # Save result
        output_file = output_dir / f"{txt_path.stem}_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Source: {txt_path.name}\n")
            f.write(f"Recommendation: {'✅ RECOMMENDED' if recommendation else '❌ NOT RECOMMENDED'}\n")
            f.write("="*80 + "\n\n")
            f.write(result)
        
        print(f"✅ Saved: {output_file.name}")
        
    except Exception as e:
        print(f"❌ Error processing {txt_path.name}: {e}")

def main():
    load_dotenv()
    args = parse_args()
    
    folder_path = Path(args.folder)
    output_dir = Path(args.output_dir)
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all .txt files
    txt_files = list(folder_path.glob("*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in {folder_path}")
        return
    
    print(f"Found {len(txt_files)} text files\n")
    
    # Process each file
    for txt_file in txt_files:
        process_text_file(txt_file, output_dir)
    
    print(f"\n✅ Done! Results saved to {output_dir}")

if __name__ == "__main__":
    main()
