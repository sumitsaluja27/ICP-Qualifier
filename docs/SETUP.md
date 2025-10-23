
# Setup Guide

Complete installation and configuration guide for ICP Qualifier.

---

## Table of Contents

1. [System Requirements](#system-requirements)

2. [Installing Python Dependencies](#installing-python-dependencies)

3. [Installing Ollama and Models](#installing-ollama-and-models)

4. [Google Search API Setup (Optional)](#google-search-api-setup-optional)

5. [Configuration Deep Dive](#configuration-deep-dive)

6. [Preparing Your Knowledge Base](#preparing-your-knowledge-base)

7. [First Run Checklist](#first-run-checklist)

8. [Troubleshooting Installation](#troubleshooting-installation)

---

## System Requirements

### Minimum

- **OS:** Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)

- **CPU:** 4 cores

- **RAM:** 8GB

- **Storage:** 10GB free space

- **Python:** 3.9 or higher

### Recommended

- **CPU:** 8+ cores

- **RAM:** 16GB

- **Storage:** 20GB free space (for models and vector databases)

- **Network:** Stable internet connection (for web scraping)

---

## Installing Python Dependencies

### Step 1: Verify Python Version

```bash

python --version

# Should show Python 3.9.x or higher

```

If Python is outdated, download from [python.org](https://www.python.org/downloads/)

### Step 2: Create Virtual Environment

**Why?** Isolates dependencies from your system Python.

```bash

# Navigate to project directory

cd ICP-Qualifier

# Create virtual environment

python -m venv venv

# Activate it

# On macOS/Linux:

source venv/bin/activate

# On Windows:

venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)

which python  # macOS/Linux

where python  # Windows

```

### Step 3: Upgrade pip

```bash

pip install --upgrade pip

```

### Step 4: Install Core Dependencies

```bash

pip install -r requirements.txt

```

**This installs:**

- LangChain and RAG components

- Web scraping tools (crawl4ai, playwright)

- Vector database (ChromaDB)

- DuckDuckGo search

- Configuration tools (PyYAML, python-dotenv)

**Installation time:** 5-10 minutes depending on internet speed

### Step 5: Install Playwright Browsers

```bash

playwright install

```

**This downloads:** Chromium browser for web scraping

**Size:** ~300MB

### Step 6: Install Google Search (Optional)

**Only if you plan to use Google Custom Search API:**

```bash

pip install -r requirements-google.txt

```

---

## Installing Ollama and Models

### Step 1: Install Ollama

**macOS:**

```bash

brew install ollama

```

**Linux:**

```bash

curl -fsSL https://ollama.ai/install.sh | sh

```

**Windows:**

Download installer from [ollama.ai](https://ollama.ai/download)

### Step 2: Start Ollama Service

```bash

ollama serve

```

**Leave this running in a separate terminal window.**

### Step 3: Pull Required Models

**In a new terminal:**

```bash

# Fast model for structured tasks (required)

ollama pull llama3

# Creative model for scoring (required)

ollama pull deepseek-llm:7b

```

**Download sizes:**

- llama3: ~4.7GB

- deepseek-llm:7b: ~4.1GB

**Total:** ~9GB

**Download time:** 10-30 minutes depending on internet speed

### Step 4: Verify Models

```bash

ollama list

```

**Expected output:**

```

NAME                    ID              SIZE    MODIFIED

llama3:latest           a6990ed6be41    4.7 GB  2 hours ago

deepseek-llm:7b         f6627e9d8c83    4.1 GB  2 hours ago

```

### Step 5: Test Models

```bash

# Test llama3

ollama run llama3 "Say hello"

# Test deepseek

ollama run deepseek-llm:7b "Say hello"

```

Both should respond quickly. If not, restart Ollama service.

---

## Google Search API Setup (Optional)

**Skip this section if using free DuckDuckGo search.**

### Why Use Google Search?

**Pros:**

- Higher quality results

- More reliable (less rate limiting)

- Better for production use

**Cons:**

- Requires API key (paid, but cheap)

- $5 per 1000 queries (~100 queries free per day)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Click "Create Project"

3. Name it "ICP-Qualifier" (or your choice)

4. Click "Create"

### Step 2: Enable Custom Search API

1. In Cloud Console, go to "APIs & Services" → "Library"

2. Search for "Custom Search API"

3. Click "Enable"

### Step 3: Create API Key

1. Go to "APIs & Services" → "Credentials"

2. Click "Create Credentials" → "API Key"

3. Copy the API key (starts with `AIza...`)

4. **Restrict the key (recommended):**

   - Click "Edit API key"

   - Under "API restrictions", select "Restrict key"

   - Choose "Custom Search API"

   - Save

### Step 4: Create Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)

2. Click "Add"

3. Configuration:

   - **Name:** ICP Qualifier Search

   - **What to search:** Search the entire web

   - **Search settings:** Turn on "Search the entire web"

4. Click "Create"

5. Copy the "Search engine ID" (looks like `a1b2c3d4e5f6...`)

### Step 5: Add Credentials to .env

Edit `.env` file:

```bash

GOOGLE_API_KEY=AIzaSyC8x9Q...  # Your API key

GOOGLE_CSE_ID=a1b2c3d4e5f6...   # Your search engine ID

```

### Step 6: Update config.yaml

```yaml

search:

  provider: "google"  # Change from "ddgs" to "google"

```

### Step 7: Test

```bash

python -m src.dashcam_company_finder USA --limit 1

```

Should see: `"🔍 Performing Google Custom Search for: ..."`

---

## Configuration Deep Dive

### config.yaml Structure

The configuration file has 7 main sections:

#### 1. Search Settings

```yaml

search:

  provider: "ddgs"  # or "google"

```

**When to use Google:**

- Production environments

- Need reliability over cost

- High volume (1000+ searches per day)

**When to use DuckDuckGo:**

- Development/testing

- Low budget

- Low volume (<100 searches per day)

#### 2. Discovery Settings

```yaml

discovery:

  sources:

    USA: [...]

    Europe: [...]

```

**How to customize:**

- Add industry-specific directories

- Remove sources that give poor results

- Add LinkedIn Sales Navigator if you have access

**Positive Keywords:**

```yaml

positive_keywords:

  - "your core product"

  - "alternative names"

  - "industry jargon"

```

**Tips:**

- Use 10-30 keywords

- Mix broad and specific terms

- Include acronyms (e.g., "DMS", "ADAS")

**Heuristic Keywords:**

```yaml

heuristic_keywords:

  - "must-have term 1"

  - "must-have term 2"

```

**Purpose:** Quick filter before expensive LLM analysis

**Best practice:** 5-15 essential terms that MUST appear on target company websites

#### 3. Scoring Settings

```yaml

scoring:

  relevance_threshold: 7

  exemplar_companies: [...]

```

**Relevance Threshold:**

- **5-6:** Cast wide net (many false positives)

- **7:** Balanced (recommended)

- **8-9:** Very strict (might miss good prospects)

**Exemplar Companies:**

- List 5-10 companies that represent your ideal customer

- Mix of direct competitors and adjacent players

- LLM compares candidates against these

#### 4. Revenue Settings

```yaml

revenue:

  minimum_threshold_millions: 15

  fallback_enabled: true

```

**Threshold Guidelines:**

- **<5M:** Small businesses, startups

- **5-50M:** Mid-market

- **50M+:** Enterprise

**Fallback Logic:**

- If `true`, estimates revenue from website text when premium sources fail

- Less accurate but better than no data

- Useful for private companies not in financial databases

#### 5. LLM Settings

```yaml

llm:

  fast_model: "llama3:latest"

  creative_model: "deepseek-llm:7b"

```

**Model Roles:**

- **Fast:** JSON parsing, verification, extraction

- **Creative:** Scoring, reasoning, analysis

**Alternative Models:**

```yaml

# If you have more powerful hardware:

fast_model: "llama3:70b"

creative_model: "mixtral:8x7b"

# If you want to use cloud APIs (requires code changes):

# fast_model: "gpt-4o-mini"

# creative_model: "claude-3-sonnet"

```

#### 6. Processing Settings

```yaml

processing:

  max_parallel_searches: 15

  max_parallel_processing: 10

  max_parallel_enrichment: 10

```

**Tuning Guidelines:**

| Your System | Searches | Processing | Enrichment |

|-------------|----------|------------|------------|

| 4 cores, 8GB RAM | 5 | 3 | 3 |

| 8 cores, 16GB RAM | 15 | 10 | 10 |

| 16 cores, 32GB RAM | 30 | 20 | 20 |

**Symptoms of too high:**

- System becomes unresponsive

- Many timeout errors

- RAM usage near 100%

**Symptoms of too low:**

- System feels idle

- Long processing times

- Low CPU usage

#### 7. RAG Settings

```yaml

rag:

  chunk_size: 1000

  chunk_overlap: 200

  retrieval_top_k: 5

```

**Chunk Size:**

- **500-800:** Better for specific facts

- **1000-1500:** Better for context (recommended)

- **2000+:** Risks losing detail

**Chunk Overlap:**

- Prevents splitting related information

- 20% of chunk_size is a good rule

- Higher = better context, but more storage

**Retrieval Top K:**

- How many chunks to retrieve per query

- **3-5:** Fast, focused (recommended)

- **10+:** Slower, more comprehensive

---

## Preparing Your Knowledge Base

### What Goes in Data/ Folder?

**Good documents:**

- Product specifications

- Service descriptions

- Technical whitepapers

- Case studies

- Target customer profiles

- Competitive analysis

**Avoid:**

- Marketing fluff without substance

- Very short documents (<500 words)

- Non-text files (images, videos)

- Confidential information you don't want in vector DB

### Supported Formats

- **PDF** (recommended) - `PyPDFLoader` handles these

- **TXT** - Plain text files work great

- **DOCX** - Requires adding DocxLoader (not included by default)

- **Markdown** - Works if saved as .txt

### Document Preparation Tips

**1. Clean your PDFs:**

- Remove password protection

- Ensure text is selectable (not scanned images)

- Split very large files (>100 pages) into sections

**2. Structure your text files:**

```

Company Name

Product Overview

=============

[Product description...]

Target Customers

===============

[Customer profiles...]

```

**3. Name files descriptively:**

```

✅ Good:

- product_capabilities_2024.pdf

- target_customer_profiles.txt

- technical_specifications.pdf

❌ Bad:

- document.pdf

- file1.txt

- untitled.pdf

```

### How Much Data Do You Need?

**Minimum:**

- 1 document describing your product/service (1000+ words)

**Recommended:**

- 3-5 documents covering:

  - What you sell

  - Who you sell to

  - Technical capabilities

  - Success stories

**Maximum:**

- No hard limit, but diminishing returns after 50 documents

- Vector DB size grows linearly with document count

### Testing Your Knowledge Base

After adding documents, test the RAG system:

```bash

python -m src.dashcam_company_finder USA --test-profiles

```

**Good output:**

```json

[

  "Fleet management solution providers in the USA",

  "Long-haul trucking companies with 50+ vehicles",

  "Last-mile delivery services using commercial vans"

]

```

**Bad output (needs better documents):**

```json

[

  "Companies in USA",

  "Businesses that need technology",

  "Organizations with vehicles"

]

```

If profiles are too generic, your documents need more specific information about your ideal customers.

---

## First Run Checklist

Before running the system, verify:

- [ ] Python 3.9+ installed

- [ ] Virtual environment activated

- [ ] All dependencies installed (`pip list` shows langchain, chromadb, etc.)

- [ ] Playwright browsers installed

- [ ] Ollama service running (`ollama list` works)

- [ ] Both LLM models downloaded (llama3, deepseek-llm)

- [ ] `config.yaml` exists (copied from example)

- [ ] `.env` exists (copied from example)

- [ ] At least 1 document in `Data/` folder

- [ ] `src/__init__.py` exists (makes it a Python package)

**Test command:**

```bash

# Dry run - just test profile generation

python -m src.dashcam_company_finder USA --test-profiles

```

**Expected output:**

- "🚀 Initializing..."

- "🗂️ Setting up vector database..."

- "🧠 Generating ideal customer profiles..."

- JSON list of customer profiles

**If this works, you're ready for a real run:**

```bash

python -m src.dashcam_company_finder USA --limit 5

```

---

## Troubleshooting Installation

### "Module not found" errors

**Symptom:**

```

ModuleNotFoundError: No module named 'langchain'

```

**Solutions:**

```bash

# 1. Verify virtual environment is activated

which python  # Should show path to venv/bin/python

# 2. Reinstall dependencies

pip install -r requirements.txt

# 3. Check Python version

python --version  # Must be 3.9+

```

### Ollama connection errors

**Symptom:**

```

Failed to connect to Ollama

```

**Solutions:**

```bash

# 1. Check if Ollama is running

ollama list

# 2. If not, start it

ollama serve

# 3. Test connection

ollama run llama3 "test"

# 4. Check Ollama is on default port

# Should be http://localhost:11434

```

### Playwright installation issues

**Symptom:**

```

Executable doesn't exist at /path/to/chromium

```

**Solutions:**

```bash

# Reinstall playwright browsers

playwright install --force

# If on Linux, install system dependencies

sudo playwright install-deps

```

### Permission errors on macOS/Linux

**Symptom:**

```

Permission denied: './venv/bin/python'

```

**Solutions:**

```bash

# Make sure scripts are executable

chmod +x venv/bin/activate

# Or use full path to Python

/path/to/ICP-Qualifier/venv/bin/python -m src.dashcam_company_finder USA

```

### Out of memory errors

**Symptom:**

```

Killed (signal 9)

```

**Solutions:**

1. Reduce parallel workers in config.yaml

2. Use smaller LLM models:

```yaml

   llm:

     fast_model: "llama3:8b"  # Instead of llama3:70b

```

3. Close other applications

4. Add swap space (Linux) or increase virtual memory (Windows)

### SSL certificate errors

**Symptom:**

```

SSL: CERTIFICATE_VERIFY_FAILED

```

**Solutions:**

```bash

# macOS

/Applications/Python\ 3.x/Install\ Certificates.command

# Linux/Windows - install certifi

pip install --upgrade certifi

```

---

## Next Steps

Once installation is complete:

1. **Read [Usage Guide](USAGE.md)** - Learn advanced usage patterns

2. **Read [Architecture](ARCHITECTURE.md)** - Understand how it works

3. **Customize config.yaml** - Adapt to your industry

4. **Add your documents** - Replace sample data

5. **Run your first search** - Start finding leads!

---

**Need help?** Open an issue on GitHub with:

- Your OS and Python version

- Full error message

- What you've tried so far

