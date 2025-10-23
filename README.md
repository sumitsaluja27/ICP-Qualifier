
# ICP Qualifier 🎯

**Automate your B2B lead discovery with AI-powered qualification**

ICP Qualifier is a production-grade system that finds, scores, and qualifies potential customers automatically using RAG (Retrieval-Augmented Generation), LLM analysis, and intelligent web scraping.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

![License](https://img.shields.io/badge/license-MIT-green.svg)

![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

---

## 🚀 What It Does

Turn hours of manual research into minutes of automated discovery:

1. **Understands Your Product** - Feed it documents about your capabilities

2. **Discovers Prospects** - Searches multiple B2B directories automatically  

3. **Scores Relevance** - AI rates each company's fit (0-10 scale)

4. **Verifies Revenue** - Checks if companies meet your size threshold

5. **Delivers Qualified Leads** - Outputs a clean list of ready-to-contact prospects

**Example Use Case:** Finding fleet management companies that need dashcam systems

- Input: Your product capability documents

- Output: List of 50+ qualified companies with $15M+ revenue, scored 7+/10 relevance

---

## 🎯 Real-World Results

This system currently finds companies in:

- **Video Telematics** - Dashcam and fleet camera providers

- **Driver Monitoring Systems (DMS)** - Drowsiness and distraction detection

- **ADAS** - Advanced Driver Assistance Systems

- **Automotive Electronics** - Related vehicle technology companies

Easily adaptable to any B2B industry with the right configuration.

---

## ✨ Key Features

### 🧠 Intelligent Discovery

- **RAG-Powered Understanding** - Learns your ideal customer from your documents

- **Multi-Source Search** - Queries industry directories, LinkedIn, business listings

- **Two Search Options** - Free (DuckDuckGo) or paid (Google Custom Search API)

### 🎯 Smart Qualification

- **AI Relevance Scoring** - LLM analyzes company websites for product-market fit

- **Heuristic Pre-Filtering** - Fast keyword checks before expensive AI calls

- **Exemplar Comparison** - Scores against your list of ideal customers

### 💰 Revenue Verification

- **Premium Sources** - Checks Crunchbase, Bloomberg, Yahoo Finance

- **Intelligent Fallback** - Estimates revenue from website text when premium data unavailable

- **Configurable Threshold** - Set minimum revenue requirement

### ⚡ Performance Optimized

- **Parallel Processing** - Concurrent search, scraping, and analysis

- **Pipeline Architecture** - Overlapping stages for maximum throughput

- **Rate Limit Handling** - Smart retries and backoff strategies

### 🔧 Production Ready

- **YAML Configuration** - Easy customization without code changes

- **Environment Variables** - Secure API key management

- **Modular Design** - Clean separation of concerns

- **Error Handling** - Robust retry logic and graceful failures

---

## 📋 Prerequisites

### Required

- **Python 3.9+**

- **Ollama** - For local LLM models ([Install Ollama](https://ollama.ai))

```bash

  # Install Ollama, then pull required models:

  ollama pull llama3

  ollama pull deepseek-llm:7b

```

### Optional

- **Google Custom Search API** - For higher quality search results

  - [Get API Key](https://developers.google.com/custom-search/v1/overview)

  - [Create Custom Search Engine](https://programmablesearchengine.google.com/)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash

git clone https://github.com/yourusername/ICP-Qualifier.git

cd ICP-Qualifier

```

### 2. Create Virtual Environment

```bash

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 3. Install Dependencies

```bash

# Core dependencies (required)

pip install -r requirements.txt

# Optional: Google Search API support

pip install -r requirements-google.txt

```

### 4. Install Playwright Browsers

```bash

# Required for web scraping

playwright install

```

### 5. Configure the System

**Copy configuration templates:**

```bash

cp config.example.yaml config.yaml

cp .env.example .env

```

**Edit `config.yaml`:**

- Customize keywords for your industry

- Set revenue threshold

- Adjust discovery sources

- Configure parallel processing limits

**Edit `.env` (if using Google Search):**

```bash

GOOGLE_API_KEY=your_api_key_here

GOOGLE_CSE_ID=your_search_engine_id_here

```

### 6. Add Your Knowledge Base

Place PDF documents or text files about your product/service in the `Data/` folder:

```

Data/

├── product_capabilities.pdf

├── technical_specs.pdf

└── target_customers.txt

```

**Sample data is included** - `Data/company_capabilities.txt` (fictional VisionFleet Solutions example)

---

## 🚦 Quick Start

### Basic Usage (DuckDuckGo Search)

```bash

python -m src.dashcam_company_finder USA

```

### With Google Search

```bash

# Set provider in config.yaml:

# search:

#   provider: "google"

python -m src.dashcam_company_finder USA

```

### Limit Results

```bash

# Find only 10 companies

python -m src.dashcam_company_finder USA --limit 10

```

### Test Profile Generation

```bash

# See what customer profiles the AI generates

python -m src.dashcam_company_finder USA --test-profiles

```

### Search Other Territories

```bash

python -m src.dashcam_company_finder Europe

python -m src.dashcam_company_finder Middle_East

```

---

## 📊 Output

Results are saved to `results.json`:

```json

[

  {

    "name": "FleetGuard Technologies",

    "website": "https://fleetguard.example.com",

    "estimated_revenue_in_millions": 45.5

  },

  {

    "name": "DriveVision Systems",

    "website": "https://drivevision.example.com",

    "estimated_revenue_in_millions": 28.0

  }

]

```

---

## ⚙️ Configuration Guide

### Key Settings in `config.yaml`

**Search Provider:**

```yaml

search:

  provider: "ddgs"  # or "google"

```

**Discovery Keywords** (customize for your industry):

```yaml

discovery:

  positive_keywords:

    - "your product category"

    - "your service type"

    - "industry-specific terms"

```

**Relevance Threshold** (0-10 scale):

```yaml

scoring:

  relevance_threshold: 7  # Only companies scoring 7+ are qualified

```

**Revenue Threshold:**

```yaml

revenue:

  minimum_threshold_millions: 15  # Minimum company size

  fallback_enabled: true           # Try to estimate from website if premium sources fail

```

**Performance Tuning:**

```yaml

processing:

  max_parallel_searches: 15      # More = faster but higher load

  max_parallel_processing: 10    # Adjust based on your CPU

  max_parallel_enrichment: 10    # Concurrent revenue lookups

```

**LLM Models:**

```yaml

llm:

  fast_model: "llama3:latest"        # For structured tasks

  creative_model: "deepseek-llm:7b"  # For scoring/reasoning

  embedding_model: "llama3"          # For vector search

```

---

## 🏗️ Architecture

### System Components

```

┌─────────────────────────────────────────────────────────────┐

│                   ICP Qualifier System                       │

└─────────────────────────────────────────────────────────────┘

                              │

        ┌─────────────────────┼─────────────────────┐

        │                     │                     │

   ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐

   │   RAG   │          │  Search   │        │  Scoring  │

   │ System  │          │  Engine   │        │  Engine   │

   └────┬────┘          └─────┬─────┘        └─────┬─────┘

        │                     │                     │

   [Knowledge]           [Discovery]          [Qualification]

   - Load docs           - DDGS/Google        - Relevance (0-10)

   - Vectorize           - Multi-source       - LLM analysis

   - Retrieve            - Parallel           - Exemplar compare

                                                      │

                                              ┌───────▼────────┐

                                              │   Enrichment   │

                                              │     Engine     │

                                              └───────┬────────┘

                                                      │

                                                 [Revenue Data]

                                                 - Premium sources

                                                 - Fallback logic

                                                 - Threshold filter

```

### Pipeline Flow

```

1. RAG Setup

   ↓

2. Generate Customer Profiles (LLM + RAG knowledge)

   ↓

3. Profile-by-Profile Processing:

   │

   ├─→ Web Search (parallel queries across sources)

   │   ↓

   ├─→ Company Verification (LLM: is this a real company?)

   │   ↓

   ├─→ Heuristic Filter (quick keyword check)

   │   ↓

   ├─→ Relevance Scoring (LLM: 0-10 vs exemplars)

   │   ↓

   └─→ Store relevant companies

   

4. Revenue Enrichment (parallel across all relevant companies)

   │

   ├─→ Try premium sources (Crunchbase, Bloomberg, etc.)

   │   ↓

   └─→ Fallback: Estimate from website text

   

5. Filter by threshold & Save results

```

### Why This Architecture?

**Two-Stage Pipeline:**

- **Stage 1 (Discovery):** Cast wide net, find potential matches

- **Stage 2 (Enrichment):** Deep dive on qualified prospects only

**Parallel Within, Sequential Between:**

- Process one customer profile at a time (stability)

- Parallelize operations within each profile (speed)

- Prevents overwhelming search APIs with requests

**Two-LLM Strategy:**

- **Fast Model (llama3):** Structured extraction, JSON parsing

- **Creative Model (deepseek):** Nuanced reasoning, scoring

**Heuristic Pre-Filter:**

- Saves expensive LLM calls

- Checks keywords before full website analysis

---

## 🔧 Customization for Your Industry

### Step 1: Update Keywords

Edit `config.yaml`:

```yaml

discovery:

  positive_keywords:

    - "your industry term 1"

    - "your industry term 2"

  

  heuristic_keywords:

    - "keyword1"

    - "keyword2"

```

### Step 2: Update Exemplar Companies

```yaml

scoring:

  exemplar_companies:

    - "Industry Leader 1"

    - "Industry Leader 2"

    - "Competitor A"

```

### Step 3: Update Discovery Sources

```yaml

discovery:

  sources:

    USA:

      - "industry-specific-directory.com"

      - "clutch.co"

```

### Step 4: Add Your Documents

Replace `Data/company_capabilities.txt` with your own:

- Product specifications

- Service descriptions  

- Target customer profiles

- Case studies

### Step 5: Adjust Scoring Prompt

Edit `advanced_dashcam_rag.py` → `_score_relevance()` method:

```python

question = f'''

My ideal customer is [YOUR DESCRIPTION].

Examples of perfect-fit companies: {str(self.exemplar_companies)}.

...

'''

```

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation and configuration

- **[Architecture Deep Dive](docs/ARCHITECTURE.md)** - System design decisions

- **[Usage Examples](docs/USAGE.md)** - Advanced usage patterns

---

## 🐛 Troubleshooting

### "No PDF files found in the Data directory"

- **Solution:** Add at least one PDF or TXT file to `Data/` folder

### "QA chain not set up"

- **Solution:** Vector database build failed. Check that Ollama models are installed:

```bash

  ollama list

  # Should show: llama3, deepseek-llm

```

### "Search failed after multiple retries"

- **Solution:** 

  - DDGS rate limiting - reduce `max_parallel_searches` in config

  - Or switch to Google Search API (more reliable but paid)

### "Google API error"

- **Solution:** Check your API key and CSE ID in `.env`

- Verify you've enabled Custom Search API in Google Cloud Console

### Slow Performance

- **Solution:**

  - Reduce parallel workers in config.yaml

  - Use Google Search instead of DDGS (faster)

  - Add more CPU/RAM to your system

### Too Many False Positives

- **Solution:**

  - Increase `relevance_threshold` (e.g., 8 instead of 7)

  - Refine `heuristic_keywords` to be more specific

  - Update exemplar companies to better match your ideal customer

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more search providers (Bing, Yahoo)

- [ ] Support for OpenAI/Anthropic APIs (cloud LLMs)

- [ ] Web UI for easier configuration

- [ ] Export to CRM formats (Salesforce, HubSpot)

- [ ] Add more financial data sources

- [ ] Improve revenue estimation accuracy

- [ ] Add unit tests

- [ ] Docker containerization

**To contribute:**

1. Fork the repository

2. Create a feature branch

3. Make your changes

4. Submit a pull request

---

## 📝 License

MIT License - feel free to use for commercial projects.

---

## 🙏 Acknowledgments

Built with:

- [LangChain](https://github.com/langchain-ai/langchain) - RAG framework

- [Ollama](https://ollama.ai) - Local LLM runtime

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - Advanced web scraping

- [ChromaDB](https://www.trychroma.com/) - Vector database

---

## 📧 Contact

**Questions or feedback?**

- Open an issue on GitHub

- Email: your.email@example.com

- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

## 🎯 What's Next?

**v2.0 Roadmap:**

- Google Search API integration ✅ (Done)

- Revenue fallback logic ✅ (Done)

- Multi-territory support ✅ (Done)

- Cloud LLM support (OpenAI, Anthropic)

- Web dashboard

- CRM integrations

- Automated email outreach

---

**Built with ❤️ for the B2B community**

Star ⭐ this repo if you find it useful!

