import os
import argparse
from dotenv import load_dotenv
from pathlib import Path
from Ollama_chatbot.constants.prompt import SYSTEM_PAPER_EVALUATION_PROMPT_V3
from Ollama_chatbot.validators.llm_output_validation import validate_llm_output, is_recommended
from Ollama_chatbot.components.session import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from itertools import islice

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate text files using LLM")
    parser.add_argument("--folder", type=str, required=True, help="Path to folder containing .txt files")
    parser.add_argument("--output-dir", type=str, required=True, help="Path to save results")
    return parser.parse_args()

# def process_text_file(txt_path: Path, output_dir: Path):
#     """Process a single text file."""
#     try:
#         print(f"Processing: {txt_path.name}")
        
#         # Read text file
#         with open(txt_path, 'r', encoding='utf-8') as f:
#             full_text = f.read()
        
#         # Run LLM
#         session = Session(system_prompt=SYSTEM_PAPER_EVALUATION_PROMPT_V3)
#         session.query = full_text
#         result = session.run()
#         validated_result = validate_llm_output(result)
        
#         # Check recommendation
#         recommendation = is_recommended(validated_result)
        
#         # Save result
#         output_file = output_dir / f"{txt_path.stem}_result.txt"
#         with open(output_file, 'w', encoding='utf-8') as f:
#             f.write(f"Source: {txt_path.name}\n")
#             f.write(f"Recommendation: {'✅ RECOMMENDED' if recommendation else '❌ NOT RECOMMENDED'}\n")
#             f.write("="*80 + "\n\n")
#             f.write(result)
        
#         print(f"✅ Saved: {output_file.name}")
        
#     except Exception as e:
#         print(f"❌ Error processing {txt_path.name}: {e}")

def process_text_file(txt_path: Path, output_dir: Path):
    """Process a single text file - no exception handling here"""
    print(f"Processing: {txt_path.name}")
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    session = Session(system_prompt=SYSTEM_PAPER_EVALUATION_PROMPT_V3)
    session.query = full_text
    result = session.run()
    validated_result = validate_llm_output(result)
    recommendation = is_recommended(validated_result)
    
    output_file = output_dir / f"{txt_path.stem}_result.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Source: {txt_path.name}\n")
        f.write(f"Recommendation: {'✅ RECOMMENDED' if recommendation else '❌ NOT RECOMMENDED'}\n")
        f.write("="*80 + "\n\n")
        f.write(result)
    
    print(f"✅ Saved: {output_file.name}")


def chunk_list(lst, chunk_size):
    """Split list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def main():
    load_dotenv()
    args = parse_args()
    
    folder_path = Path(args.folder)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    txt_files = list(folder_path.glob("*.txt"))
    print(f"Found {len(txt_files)} text files\n")
    
    # ✅ Process in batches of 8 with 1 second gap
    BATCH_SIZE = 8  # Safe for Tier 1 (500 RPM)
    
    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        for batch in chunk_list(txt_files, BATCH_SIZE):
            
            futures = {
                executor.submit(process_text_file, txt_file, output_dir): txt_file
                for txt_file in batch
            }
            
            for future in as_completed(futures):
                txt_file = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Failed: {txt_file.name} → {e}")
            
            # ✅ Wait 1 second before next batch
            print(f"⏳ Batch done, waiting 1 second...")
            time.sleep(1)

if __name__ == "__main__":
    main()
