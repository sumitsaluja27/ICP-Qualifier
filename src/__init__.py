"""
ICP Qualifier - Ideal Customer Profile Qualification System
A production-grade B2B lead generation system using RAG + LLM + web scraping
to automatically discover, score, and qualify potential customers.
"""
__version__ = "1.0.0"
__author__ = "Your Name"
from src.advanced_dashcam_rag import AdvancedDashcamRAG
from src.dashcam_company_finder import DashcamCompanyFinder
__all__ = ['AdvancedDashcamRAG', 'DashcamCompanyFinder']
