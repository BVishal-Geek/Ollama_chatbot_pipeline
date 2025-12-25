# Ollama_chatbot

## Motivation & Purpose

The primary goal of this project is to build an **offline, privacy-preserving LLM pipeline** that can **systematically evaluate biomedical research papers** for their suitability in **machine-learning modeling**.

In many biomedical research workflows, a large number of papers must be manually screened to determine whether they:
- Contain clearly defined cohorts
- Provide usable datasets
- Define outcomes and responder/non-responder criteria
- Are structured enough to support downstream modeling

This manual review process is:
- Time-consuming
- Subjective
- Difficult to scale
- Error-prone when dealing with hundreds of papers

This project addresses that problem by using a **hosted Large Language Model (LLM)** to perform **deterministic, criteria-based screening** of full-text research papers.

---

## 🎯 What This Pipeline Is Designed To Do

Given a full-text research paper (PDF), the pipeline:

1. Extracts all readable text from the document  
2. Applies a **fixed, rule-driven evaluation prompt**  
3. Checks for the presence of required modeling-ready signals, such as:
   - Dataset availability
   - Sample size reporting
   - Intervention definitions
   - Explicit responder / non-responder criteria
4. Produces a **strict, machine-readable JSON output**
5. Determines whether the paper should be **recommended** for downstream ML modeling

The focus is **structured evaluation**, not open-ended summarization or chat.

## Project Structure (Overview)
OLLAMA_CHATBOT/
├── data/                       # Input PDFs (example papers)
│   └── PMID_37313409.pdf
├── src/
│   └── Ollama_chatbot/
│       ├── components/         # Core building blocks
│       │   ├── text_extraction.py
│       │   └── session.py
│       ├── config/             # Runtime / YAML configs
│       ├── constants/          # Prompts, schemas, static configs
│       ├── pipeline/           # Pipeline orchestration (future)
│       ├── utils/              # Helper utilities
│       ├── init.py
│       └── main.py             # CLI entry point
├── tests/                      # Unit tests (pytest)
├── config/                     # Top-level configuration files
├── templates/                  # HTML / UI templates (future)
├── requirements.txt
├── setup.py
└── README.md


## Running the Project

The project is executed via **`main.py`**, which accepts a **PDF file path** as a command-line argument.

### 1️. Install the project (once)

From the project root:

```bash
pip install -e .
```

### 2. Run
```bash
python main.py --pdf "Location to the pdf"
