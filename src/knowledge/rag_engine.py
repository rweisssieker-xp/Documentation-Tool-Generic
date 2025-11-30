"""
RAG Engine - Retrieval-Augmented Generation for Q&A.
Part of Feature 4: Multi-Modal Knowledge Base
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RAGResponse:
    """Response from RAG query."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    tokens_used: int
    model: str


class RAGEngine:
    """
    Retrieval-Augmented Generation engine.
    Combines semantic search with GPT for intelligent Q&A.
    """
    
    SYSTEM_PROMPT_DE = """Du bist ein hilfreicher Assistent für technische Dokumentation.
Beantworte Fragen basierend auf dem bereitgestellten Kontext.
Wenn die Antwort nicht im Kontext zu finden ist, sage das ehrlich.
Verweise auf die relevanten Quellen in deiner Antwort.
Antworte auf Deutsch."""

    SYSTEM_PROMPT_EN = """You are a helpful technical documentation assistant.
Answer questions based on the provided context.
If the answer is not in the context, say so honestly.
Reference the relevant sources in your answer.
Answer in English."""
    
    def __init__(
        self,
        semantic_search: Any,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        language: str = "de"
    ):
        """
        Initialize RAG engine.
        
        Args:
            semantic_search: SemanticSearch instance
            api_key: OpenAI API key
            model: GPT model to use
            language: Response language ('de' or 'en')
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required. Install with: pip install openai")
        
        self.search = semantic_search
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.language = language
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = self.SYSTEM_PROMPT_DE if language == "de" else self.SYSTEM_PROMPT_EN
        
        logger.info(f"RAGEngine initialized: {model}, {language}")
    
    def query(
        self,
        question: str,
        context_limit: int = 5,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> RAGResponse:
        """
        Query the knowledge base with RAG.
        
        Args:
            question: User question
            context_limit: Number of documents to retrieve
            max_tokens: Maximum response tokens
            temperature: Response creativity (0-1)
            
        Returns:
            RAGResponse with answer and sources
        """
        # Retrieve relevant context
        search_data = self.search.answer_question(question, context_limit)
        context = search_data.get("context", "")
        sources = search_data.get("sources", [])
        
        if not context:
            return RAGResponse(
                answer="Ich konnte keine relevanten Informationen in der Wissensbasis finden." if self.language == "de" 
                       else "I could not find relevant information in the knowledge base.",
                sources=[],
                confidence=0.0,
                tokens_used=0,
                model=self.model
            )
        
        # Build prompt
        user_prompt = self._build_prompt(question, context, sources)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                confidence=search_data.get("confidence", 0.5),
                tokens_used=tokens_used,
                model=self.model
            )
        
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return RAGResponse(
                answer=f"Fehler bei der Verarbeitung: {str(e)}" if self.language == "de"
                       else f"Error processing query: {str(e)}",
                sources=[],
                confidence=0.0,
                tokens_used=0,
                model=self.model
            )
    
    def generate_summary(
        self,
        doc_ids: List[str],
        max_tokens: int = 500
    ) -> str:
        """
        Generate a summary of multiple documents.
        
        Args:
            doc_ids: List of document IDs to summarize
            max_tokens: Maximum tokens for summary
            
        Returns:
            Summary text
        """
        # Retrieve documents
        contents = []
        for doc_id in doc_ids:
            doc = self.search.kb.get_document(doc_id)
            if doc:
                contents.append(f"[{doc.title}]\n{doc.content}")
        
        if not contents:
            return "Keine Dokumente gefunden." if self.language == "de" else "No documents found."
        
        combined = "\n\n---\n\n".join(contents)
        
        prompt = f"""Erstelle eine prägnante Zusammenfassung der folgenden Dokumentation:

{combined}

Zusammenfassung:""" if self.language == "de" else f"""Create a concise summary of the following documentation:

{combined}

Summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du bist ein Experte für technische Zusammenfassungen." if self.language == "de"
                                                  else "You are an expert at technical summarization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Fehler: {str(e)}" if self.language == "de" else f"Error: {str(e)}"
    
    def suggest_related(
        self,
        question: str,
        limit: int = 3
    ) -> List[str]:
        """
        Suggest related questions based on knowledge base content.
        
        Args:
            question: Original question
            limit: Number of suggestions
            
        Returns:
            List of suggested questions
        """
        # Get related documents
        results = self.search.search(question, limit=limit)
        
        if not results:
            return []
        
        # Build context from results
        context = "\n".join([f"- {r.title}: {r.content[:200]}" for r in results])
        
        prompt = f"""Basierend auf der ursprünglichen Frage und dem verfügbaren Kontext, 
schlage {limit} verwandte Fragen vor, die ein Benutzer stellen könnte.

Ursprüngliche Frage: {question}

Verfügbarer Kontext:
{context}

Gib nur die Fragen zurück, eine pro Zeile, ohne Nummerierung:""" if self.language == "de" else f"""Based on the original question and available context,
suggest {limit} related questions a user might ask.

Original question: {question}

Available context:
{context}

Return only the questions, one per line, without numbering:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            suggestions = response.choices[0].message.content.strip().split("\n")
            return [s.strip() for s in suggestions if s.strip()][:limit]
        
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []
    
    def _build_prompt(
        self,
        question: str,
        context: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """Build the user prompt for RAG."""
        source_list = "\n".join([f"- {s['title']} (Relevanz: {s['score']:.0%})" for s in sources])
        
        if self.language == "de":
            return f"""Beantworte die folgende Frage basierend auf dem Kontext.

FRAGE: {question}

VERFÜGBARE QUELLEN:
{source_list}

KONTEXT:
{context}

Beantworte die Frage präzise und verweise auf die relevanten Quellen. 
Wenn die Antwort nicht im Kontext zu finden ist, sage das."""
        else:
            return f"""Answer the following question based on the context.

QUESTION: {question}

AVAILABLE SOURCES:
{source_list}

CONTEXT:
{context}

Answer the question precisely and reference the relevant sources.
If the answer is not in the context, say so."""

