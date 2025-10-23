import os
import json
import time
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM as Ollama
from langchain_community.document_loaders import PyPDFLoader
from src.config import DASHCAM_DATA_PATH, DASHCAM_VECTOR_DB_PATH, METADATA_FILE, CONFIG
from src.utils import parse_json_from_llm_response
class AdvancedDashcamRAG:
    def __init__(self):
        print("🚀 Initializing AdvancedDashcamRAG with local models...")
       
        # Load LLM configuration
        llm_config = CONFIG.get('llm', {})
        self.llm_fast = Ollama(model=llm_config.get('fast_model', 'llama3:latest'))
        self.llm_creative = Ollama(model=llm_config.get('creative_model', 'deepseek-llm:7b'))
       
        # Load embedding model
        self.embeddings = OllamaEmbeddings(model=llm_config.get('embedding_model', 'llama3'))
       
        # Load RAG configuration
        rag_config = CONFIG.get('rag', {})
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=rag_config.get('chunk_size', 1000),
            chunk_overlap=rag_config.get('chunk_overlap', 200)
        )
       
        self.vector_db = None
        self.qa_chain = None
    def setup_vector_database(self, force: bool = None):
        """
        Set up the vector database for RAG.
       
        Args:
            force: If True, rebuild database even if it exists.
                   If None, uses config setting.
        """
        if force is None:
            force = CONFIG.get('rag', {}).get('force_rebuild', False)
       
        print("🗂️ Setting up vector database...")
        if not force and DASHCAM_VECTOR_DB_PATH.exists() and METADATA_FILE.exists():
            print("✅ Vector database already exists. Loading...")
            self.vector_db = Chroma(
                persist_directory=str(DASHCAM_VECTOR_DB_PATH),
                embedding_function=self.embeddings
            )
        else:
            print("🔨 No existing database or force=True. Building new database...")
            pdf_files = list(DASHCAM_DATA_PATH.glob("*.pdf"))
            if not pdf_files:
                print("⚠️ No PDF files found in the Data directory.")
                return
           
            documents = [doc for pdf_path in pdf_files for doc in PyPDFLoader(str(pdf_path)).load()]
            print("📄 Splitting documents into chunks...")
            texts = self.text_splitter.split_documents(documents)
           
            print("💾 Creating and persisting vector database...")
            self.vector_db = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory=str(DASHCAM_VECTOR_DB_PATH)
            )
           
            metadata = {
                "last_updated": datetime.utcnow().isoformat(),
                "ingested_files": [p.name for p in pdf_files]
            }
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)
            print("✅ New vector database created and metadata saved.")
       
        self._setup_qa_chain()
    def _setup_qa_chain(self):
        """Set up the QA chain for knowledge retrieval."""
        if self.vector_db:
            print("🔗 Setting up QA chain...")
           
            # Get retrieval configuration
            rag_config = CONFIG.get('rag', {})
            retrieval_k = rag_config.get('retrieval_top_k', 5)
           
            prompt_template = '''
            You are an expert automotive and telematics hardware consultant. Use the following pieces of context to answer the question at the end.
            Provide a concise and factual answer based ONLY on the provided context.
            Context: {context}
            Question: {question}
            Answer:
            '''
            PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
           
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm_fast, # Use the fast, reliable model for this structured task
                chain_type="stuff",
                retriever=self.vector_db.as_retriever(search_kwargs={"k": retrieval_k}),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            print("✅ QA chain is ready.")
    def query_knowledge(self, question: str) -> dict:
        """
        Query the knowledge base with a question.
       
        Args:
            question: The question to ask
           
        Returns:
            Dictionary with 'answer' and 'sources' keys
        """
        if not self.qa_chain:
            print("⚠️ QA chain not set up.")
            return {"answer": "", "sources": []}
        try:
            result = self.qa_chain.invoke({"query": question})
            return {
                "answer": result.get("result", "").strip(),
                "sources": result.get("source_documents", [])
            }
        except Exception as e:
            print(f"❌ An error occurred during query: {e}")
            return {"answer": "", "sources": []}
    def get_target_company_profiles(self, territory: str) -> list[str]:
        """
        Generate ideal customer profiles for the given territory.
       
        Args:
            territory: Geographic territory (e.g., "USA", "Europe")
           
        Returns:
            List of specific company profile descriptions
        """
        for attempt in range(2):
            print(f"🧠 Generating ideal customer profiles for {territory} (Attempt {attempt + 1}/2)...")
            prompt = f'''
            Based on the provided documents about high-end dashcam technology, generate a JSON list of 5 specific company profiles in "{territory}" that would be ideal customers (B2B and B2C).
            Example for "USA": ["fleet management solution providers for long-haul trucking in the US", "American automotive electronics retailers"]
            '''
            response = self.query_knowledge(prompt)
            answer = response.get("answer", "")
            parsed_data = parse_json_from_llm_response(answer)
            profiles = []
            if isinstance(parsed_data, list):
                for item in parsed_data:
                    if isinstance(item, str):
                        profiles.append(item)
                    elif isinstance(item, dict):
                        for key in ['Company', 'profile', 'name']:
                            if key in item and isinstance(item[key], str):
                                profiles.append(item[key])
                                break
            if profiles:
                print(f" ✅ Customer profiles: {profiles}")
                return profiles
            print(" ⚠️ Attempt failed. Retrying...")
            time.sleep(2)
        print(" ❌ Customer profiles: []")
        return []
    def analyze_text(self, text: str, question: str, model_type: str = 'fast') -> str:
        """
        Analyze text using LLM to answer a specific question.
       
        Args:
            text: The text to analyze
            question: The question to answer about the text
            model_type: 'fast' for structured tasks, 'creative' for nuanced reasoning
           
        Returns:
            LLM's answer as a string
        """
        print(f"🧠 Analyzing text with LLM ({model_type} model)...")
        llm_to_use = self.llm_creative if model_type == 'creative' else self.llm_fast
        prompt = f"""Here is a block of text:
---
{text}
---
Based *only* on the text provided, answer the following question: {question}"""
        try:
            return llm_to_use.invoke(prompt).strip()
        except Exception as e:
            print(f"❌ An error occurred during text analysis: {e}")
            return ""
