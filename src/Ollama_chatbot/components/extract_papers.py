from Bio import Entrez
import time
import requests
import os

# IMPORTANT: Replace with your email and get an API key from NCBI
Entrez.email = "vishal.bakshi@gwu.edu"
Entrez.api_key = "91edd023f816535457674cb118a456ceda08"  # Get from https://www.ncbi.nlm.nih.gov/account/

def search_pubmed(query, max_results=100):
    """Search PubMed and return PMIDs"""
    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=max_results,
        sort="relevance"
    )
    results = Entrez.read(handle)
    handle.close()
    return results["IdList"]

def get_pmc_id(pmid):
    """Convert PMID to PMC ID (needed for full text)"""
    try:
        handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
        record = Entrez.read(handle)
        handle.close()
        
        if record[0]["LinkSetDb"]:
            pmc_id = record[0]["LinkSetDb"][0]["Link"][0]["Id"]
            return pmc_id
    except:
        return None

def download_pmc_pdf(pmc_id, output_dir="pdfs"):
    """Download PDF from PMC if available"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to get PDF link
    url = f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/pdf/"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            filename = os.path.join(output_dir, f"PMC{pmc_id}.pdf")
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: PMC{pmc_id}")
            return True
        else:
            print(f"✗ No PDF available for PMC{pmc_id}")
            return False
    except Exception as e:
        print(f"✗ Error downloading PMC{pmc_id}: {e}")
        return False

def main():
    # Search query - modify as needed
    query = '''("TCGA" OR "GEO" OR "SEER" OR "publicly available data" OR "open access data" OR "public dataset" OR "data repository") AND (cancer OR neoplasm OR carcinoma OR tumor OR malignancy)
("TCGA" OR "GEO" OR "publicly available data" OR "open access data" OR "public dataset" OR "data repository") AND (cancer OR neoplasm OR carcinoma OR tumor OR malignancy) AND (treatment OR therapy OR drug OR chemotherapy OR radiotherapy OR immunotherapy OR "clinical trial" OR intervention OR "targeted therapy" OR pharmacotherapy)'''  # The filter ensures open access papers
    
    print(f"Searching PubMed for: {query}")
    pmids = search_pubmed(query, max_results=2)
    print(f"Found {len(pmids)} papers")
    
    downloaded = 0
    for i, pmid in enumerate(pmids, 10):
        print(f"\n[{i}/{len(pmids)}] Processing PMID: {pmid}")
        
        # Get PMC ID
        pmc_id = get_pmc_id(pmid)
        if not pmc_id:
            print(f"  No PMC ID found for PMID {pmid}")
            continue
        
        # Download PDF
        if download_pmc_pdf(pmc_id):
            downloaded += 1
        
        # Be polite - rate limit (3 requests/sec with API key, 1/sec without)
        time.sleep(0.34)
    
    print(f"\n{'='*50}")
    print(f"Download complete! {downloaded}/{len(pmids)} PDFs downloaded")

if __name__ == "__main__":
    main()