import xml.etree.ElementTree as ET
import os
from Bio import Entrez
import time
from argparse import ArgumentParser
from datetime import datetime
from Ollama_chatbot.constants.extraction_pattern import matches_data_availability_pattern

# IMPORTANT: Replace with your email and API key
Entrez.email = "vishal.bakshi@gwu.edu"
Entrez.api_key = "91edd023f816535457674cb118a456ceda08"

date = datetime.now().strftime("%Y-%m-%d")

def extract_text_from_element(element):
    """
    Recursively extract all text from an XML element and its children.
    Preserves paragraph structure.
    """
    if element is None:
        return ""
    
    text_parts = []
    
    # Get the element's own text
    if element.text:
        text_parts.append(element.text.strip())
     
    # Get text from all children
    for child in element:
        child_text = extract_text_from_element(child)
        if child_text:
            text_parts.append(child_text)
        # Get tail text (text after the child element)
        if child.tail:
            text_parts.append(child.tail.strip())
    
    return " ".join(text_parts)


def extract_abstract(root):
    """Extract abstract text"""
    abstract_section = root.find('.//abstract')
    if abstract_section is None:
        return "Abstract not found"
    
    abstract_text = []
    # Find all sections within abstract
    for sec in abstract_section.findall('.//sec'):
        title = sec.find('title')
        if title is not None and title.text:
            abstract_text.append(f"\n{title.text}:")
        
        # Extract paragraphs
        for para in sec.findall('.//p'):
            para_text = extract_text_from_element(para)
            if para_text:
                abstract_text.append(para_text)
    
    # If no sections found, just get all paragraphs
    if not abstract_text:
        for para in abstract_section.findall('.//p'):
            para_text = extract_text_from_element(para)
            if para_text:
                abstract_text.append(para_text)
    
    return "\n".join(abstract_text)


def extract_section_by_title(root, section_titles):
    """
    Extract a section from the body by matching title(s).
    section_titles can be a string or list of strings to match.
    """
    if isinstance(section_titles, str):
        section_titles = [section_titles]
    
    # Convert all titles to lowercase for case-insensitive matching
    section_titles = [title.lower() for title in section_titles]
    
    # Find all sections in body
    body = root.find('.//body')
    if body is None:
        return f"Section not found (no body element)"
    
    for sec in body.findall('.//sec'):
        title_elem = sec.find('title')
        if title_elem is not None and title_elem.text:
            title_text = title_elem.text.strip().lower()
            
            # Check if any of the provided titles match
            if any(search_title in title_text for search_title in section_titles):
                section_text = [f"{title_elem.text}"]
                
                # Extract all paragraphs in this section
                for para in sec.findall('.//p'):
                    para_text = extract_text_from_element(para)
                    if para_text:
                        section_text.append(f"\n{para_text}")
                
                # Also check for subsections
                for subsec in sec.findall('.//sec'):
                    subtitle = subsec.find('title')
                    if subtitle is not None and subtitle.text:
                        section_text.append(f"\n\n{subtitle.text}")
                    
                    for para in subsec.findall('.//p'):
                        para_text = extract_text_from_element(para)
                        if para_text:
                            section_text.append(f"\n{para_text}")
                
                return "\n".join(section_text)
    
    return f"Section with title(s) {section_titles} not found"


def extract_data_availability(root):
    """Extract data availability statement"""
    # Try to find in notes section
    for notes in root.findall('.//*[title]'):
        title = notes.find('title')
        if title is not None and title.text:
            if matches_data_availability_pattern(title.text):
                paragraphs = []
                for para in notes.findall('.//p'):
                    para_text = extract_text_from_element(para)
                    if para_text:
                        paragraphs.append(para_text)
                return "\n".join(paragraphs) if paragraphs else "Data availability statement found but empty"
    
    return "Data availability statement not found"


def extract_associated_data(root):
    """Extract associated data/supplementary information"""
    associated_text = []
    
    # Look for supplementary material in back matter
    for supp in root.findall('.//supplementary-material'):
        # Get caption/label
        label = supp.find('label')
        caption = supp.find('caption')
        
        if label is not None and label.text:
            associated_text.append(f"\n{label.text}")
        
        if caption is not None:
            caption_text = extract_text_from_element(caption)
            if caption_text:
                associated_text.append(caption_text)
        
        # Get media info
        media = supp.find('.//media')
        if media is not None:
            href = media.get('{http://www.w3.org/1999/xlink}href')
            if href:
                associated_text.append(f"File: {href}")
    
    # Also check for sections with "supplementary" in title
    for sec in root.findall('.//sec'):
        title = sec.find('title')
        if title is not None and title.text:
            if 'supplementary' in title.text.lower() or 'associated data' in title.text.lower():
                associated_text.append(f"\n{title.text}")
                for para in sec.findall('.//p'):
                    para_text = extract_text_from_element(para)
                    if para_text:
                        associated_text.append(para_text)
    
    return "\n".join(associated_text) if associated_text else "No associated data found"


def process_xml_to_text(xml_content, pmcid):
    """
    Process XML content and return formatted text.
    Returns the extracted text as a string, or None if parsing fails.
    """
    try:
        # Parse XML from string
        root = ET.fromstring(xml_content)
        
        # Extract article title
        title_elem = root.find('.//article-title')
        article_title = extract_text_from_element(title_elem) if title_elem is not None else "Title not found"
        
        # Extract actual PMCID from XML (not the one passed in)
        pmcid_elem = root.find('.//article-id[@pub-id-type="pmcid"]')
        actual_pmcid = pmcid_elem.text if pmcid_elem is not None else pmcid
        
        # Extract PMID as well
        pmid_elem = root.find('.//article-id[@pub-id-type="pmid"]')
        pmid = pmid_elem.text if pmid_elem is not None else "Not found"
        
        # DEBUG: Print article info
        print(f"\n  DEBUG INFO:")
        print(f"  Title: {article_title[:100]}...")
        print(f"  PMCID from XML: {actual_pmcid}")
        print(f"  PMID: {pmid}")
        
        # Extract keywords to check relevance
        keywords = []
        for kwd_group in root.findall('.//kwd-group'):
            for kwd in kwd_group.findall('.//kwd'):
                if kwd.text:
                    keywords.append(kwd.text.lower())
        
        if keywords:
            print(f"  Keywords: {', '.join(keywords[:5])}")
        
        # Check if cancer-related
        cancer_terms = ['cancer', 'carcinoma', 'tumor', 'tumour', 'neoplasm', 'malignancy', 'oncology']
        title_lower = article_title.lower()
        abstract = extract_abstract(root).lower()
        
        is_cancer_related = any(term in title_lower or term in abstract for term in cancer_terms)
        print(f"  Cancer-related: {is_cancer_related}")
        
        # Build the output text
        output_lines = []
        output_lines.append("="*80)
        output_lines.append(f"ARTICLE TITLE: {article_title}")
        output_lines.append(f"PMCID: {actual_pmcid}")
        output_lines.append(f"PMID: {pmid}")
        if keywords:
            output_lines.append(f"KEYWORDS: {', '.join(keywords)}")
        output_lines.append("="*80)
        output_lines.append("")
        
        # Extract and add each section
        sections = {
            "ABSTRACT": extract_abstract(root),
            "INTRODUCTION": extract_section_by_title(root, ["introduction", "intro"]),
            "MATERIALS AND METHODS": extract_section_by_title(root, ["materials and methods", "methods", "materials & methods"]),
            "RESULTS": extract_section_by_title(root, "results"),
            "DISCUSSION": extract_section_by_title(root, "discussion"),
            "CONCLUSION": extract_section_by_title(root, ["conclusion", "conclusions"]),
            "DATA AVAILABILITY": extract_data_availability(root),
            "ASSOCIATED DATA": extract_associated_data(root)
        }
        
        for section_name, section_text in sections.items():
            output_lines.append("")
            output_lines.append("="*80)
            output_lines.append(f"{section_name}")
            output_lines.append("="*80)
            output_lines.append(section_text)
            output_lines.append("")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        print(f"  ERROR processing XML for {pmcid}: {e}")
        return None


def get_ids_by_query(query, max_results=100):
    """Search PMC database and return list of PMCIDs"""
    print(f"Searching for: '{query}' in PMC...")
    print(f"\nDEBUG: Full query being sent to PMC:")
    print(f"{query}\n")
    
    handle = Entrez.esearch(db="pmc", term=query, retmax=max_results, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    
    id_list = record.get('IdList', [])
    
    # Debug: Show translation of query
    if 'TranslationStack' in record:
        print(f"DEBUG: Query translation:")
        print(record['TranslationStack'])
        print()
    
    print(f"Found {len(id_list)} PMC results.")
    print(f"DEBUG: First 5 PMCIDs: {id_list[:5]}")
    
    return id_list


def download_and_extract_pmc(pmcid, output_dir="pmc_texts"):
    """
    Download PMC XML and immediately extract text, saving only the text file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Remove 'PMC' prefix if present for the efetch call
    pmc_id = pmcid.replace('PMC', '')
    
    print(f"Downloading and processing {pmcid}...", end=" ")
    
    try:

        # Download XML
        handle = Entrez.efetch(db="pmc", id=pmc_id, rettype="full", retmode="xml")
        xml_data = handle.read().decode('utf-8')
        handle.close()

        # Check if we got actual content
        if "<body" in xml_data or "<article" in xml_data:
            # Process XML to extract text
            extracted_text = process_xml_to_text(xml_data, pmcid)
            
            if extracted_text:
                # Save text file
                text_filename = os.path.join(output_dir, f"{pmcid}_extracted.txt")
                with open(text_filename, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                
                print(f"✓ Saved to {text_filename}")
                return True
            else:
                print(f"✗ Failed to extract text")
                return False
        else:
            print(f"✗ No full-text available")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def download_and_process_articles(query, max_results=100, output_dir="pmc_texts"):
    """
    Main function: Search PMC, download XMLs, extract text, and save only text files.
    """
    print("="*80)
    print("PMC ARTICLE DOWNLOADER AND TEXT EXTRACTOR")
    print("="*80)
    
    # Search for articles
    pmc_ids = get_ids_by_query(query, max_results=max_results)
    
    if not pmc_ids:
        print("No articles found.")
        return
    
    print(f"\nDownloading and extracting text from {len(pmc_ids)} articles...")
    print(f"Output directory: {output_dir}")
    print("="*80 + "\n")
    
    successful = 0
    failed = 0
    
    for i, pmc_id in enumerate(pmc_ids, 1):
        print(f"[{i}/{len(pmc_ids)}] ", end="")
        
        if download_and_extract_pmc(f"PMC{pmc_id}", output_dir):
            successful += 1
        else:
            failed += 1
        
        # Rate limiting
        time.sleep(0.34)  # ~3 requests per second with API key
    
    print("\n" + "="*80)
    print(f"SUMMARY")
    print("="*80)
    print(f"Total articles processed: {len(pmc_ids)}")
    print(f"Successfully extracted: {successful}")
    print(f"Failed: {failed}")
    print(f"Output directory: {output_dir}")
    print("="*80)


# Main execution
if __name__ == "__main__":

    parser = ArgumentParser(description="PMC Article Downloader and Text Extractor")
    parser.add_argument("--max_results", type=int, default=100, help="Maximum number of results to process")
    args = parser.parse_args()

    # Your search query
    query = '''("TCGA" OR "GEO" OR "SEER" OR "publicly available data" OR "open access data" OR "public dataset" OR "data repository") AND (cancer OR neoplasm OR carcinoma OR tumor OR malignancy) AND (treatment OR therapy OR drug OR chemotherapy OR radiotherapy OR immunotherapy OR "clinical trial" OR intervention OR "targeted therapy" OR pharmacotherapy)'''
    
    # Download and process articles
    # This will download XMLs, extract text, and save ONLY text files
    download_and_process_articles(
        query=query,
        max_results=args.max_results,  # Adjust as needed
        output_dir=f"../../../data/{date}"  # Output folder for text files
    )
    
    print("\n✓ All done! Text files are in the 'pmc_texts' folder.")
    print("No XML files were saved - only the extracted text files.")