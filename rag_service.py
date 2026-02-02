"""
RAG Service
Combines vector search with LLM generation for legal Q&A
"""

import os
from typing import List, Dict, Optional
from groq import Groq
from sentence_transformers import SentenceTransformer
from vector_store import VectorStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RAGService:
    """RAG service for legal question answering"""
    
    def __init__(
        self,
        vector_store_path: str = "data/processed",
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        llm_model: str = "llama-3.3-70b-versatile",
        similarity_threshold: float = 0.45
    ):
        """
        Initialize RAG service
        
        Args:
            vector_store_path: Path to saved vector store
            embedding_model: Model for query embeddings
            llm_model: Groq model name
            similarity_threshold: Minimum similarity score for retrieval
        """
        print("Initializing RAG service...")
        
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Load vector store
        print("Loading vector store...")
        self.vector_store = VectorStore(dimension=1024)
        self.vector_store.load(vector_store_path)
        
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.llm_model = llm_model
        
        self.similarity_threshold = similarity_threshold
        
        print("RAG service initialized successfully!")
    
    def retrieve_documents(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
        
        Returns:
            List of retrieved documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            k=top_k,
            score_threshold=self.similarity_threshold
        )
        
        return results
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            retrieved_docs: List of retrieved documents
        
        Returns:
            Formatted context string with judgment text
        """
        if not retrieved_docs:
            return "No relevant case law found."
        
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc["metadata"]
            doc_id = doc["doc_id"]
            
            # Load full document to get judgment text
            from pathlib import Path
            import json
            
            doc_path = Path(f'data/raw/{doc_id}.json')
            judgment_text = ""
            
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                        full_text = doc_data.get('doc', '')
                        # Get first 2000 chars for context (enough for key points)
                        judgment_text = full_text[:2000] + "..." if len(full_text) > 2000 else full_text
                except Exception as e:
                    judgment_text = "[Error loading judgment text]"
            
            context_parts.append(f"""
===== CASE {i} =====
Title: {meta.get('title', 'Unknown')}
Court: {meta.get('court', 'Unknown')}
Date: {meta.get('date', 'Unknown')}
Case Number: {meta.get('casenumber', 'Unknown')}
Relevance Score: {doc['score']:.3f}

Judgment Excerpt:
{judgment_text}

==================
""")
        
        return "\n".join(context_parts)
    
    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[Dict],
        include_citations: bool = True
    ) -> Dict:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User question
            retrieved_docs: Retrieved documents
            include_citations: Whether to include citations in response
        
        Returns:
            Dict with answer, confidence, and citations
        """
        # Check if we have good matches
        if not retrieved_docs:
            return {
                "answer": "I couldn't find relevant case law in my database for your question. However, I can provide general information: Please note this is general knowledge, not based on specific case precedents. For authoritative answers, consult indiankanoon.org or a legal professional.",
                "confidence": "low",
                "citations": [],
                "suggestion": "Try rephrasing your question or search on indiankanoon.org"
            }
        
        best_score = retrieved_docs[0]["score"]
        
        # Low confidence - use general knowledge with strong disclaimer
        if best_score < 0.55:
            context = self.format_context(retrieved_docs)
            
            system_prompt = """You are a legal AI assistant. You have limited matching cases for this query.
Provide a general answer based on your knowledge of Indian law, but CLEARLY state:
1. That you don't have strong case law matches
2. This is general information only
3. User should consult a lawyer or indiankanoon.org

Keep it brief and helpful."""

            user_prompt = f"""Question: {query}

Limited case matches found:
{context}

Provide a brief, general answer about this legal topic in Indian law, but clearly state this is general information and not based on strong case precedents. Recommend consulting a lawyer."""

            try:
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                answer = response.choices[0].message.content.strip()
                
                return {
                    "answer": answer,
                    "confidence": "low",
                    "citations": [self._format_citation(doc) for doc in retrieved_docs],
                    "warning": "Limited case law matches. This response uses general legal knowledge. Consult a lawyer for specific advice."
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "answer": "I found limited relevant cases and encountered an error. Please rephrase your question.",
                    "confidence": "error",
                    "citations": []
                }
        
        # Format context
        context = self.format_context(retrieved_docs)
        
        # Build prompt
        system_prompt = """You are a legal AI assistant specializing in Indian law.

ANSWER STRUCTURE (FOLLOW EXACTLY):

1. GENERAL ANSWER FIRST (2-3 sentences):
   - Start with the general legal principle about this topic in Indian law
   - Use your knowledge of Indian law to give a helpful overview
   
2. CASE-BY-CASE ANALYSIS:
   - For EACH retrieved case, explain:
     * How it relates to the question
     * What legal principle or ruling it establishes
     * Key relevant points from the judgment
   
3. CONFIDENCE ASSESSMENT:
   - State whether the cases strongly support your answer or are tangentially related

FORMAT EXAMPLE:
"Under Indian law, [general principle]...

Retrieved Case Analysis:

Case 1: [Title]
This case relates to the question because [explanation]. The court held that [key point from judgment]. This is relevant as [connection to query].

Case 2: [Title]
This judgment addresses [aspect of question]. The Supreme Court ruled [key principle]. This supports the general principle that [connection].

Overall, the retrieved cases [strongly support / partially address / tangentially relate to] the question."

CRITICAL RULES:
- Start with general answer, then discuss cases
- Analyze each case individually - explain its relevance
- Never say cases "don't answer" if they're related - explain how they relate
- Be specific about what each case says
- Ground your general answer in the case law when possible"""

        user_prompt = f"""Question: {query}

Below are relevant Supreme Court judgments with excerpts:

{context}

Instructions:
1. First, provide a general answer about this topic in Indian law (2-3 sentences)
2. Then analyze EACH case above individually:
   - Explain how it relates to the question
   - State what it says about the issue
   - Highlight key relevant points
3. End with a brief confidence statement about how well the cases address the question

Remember: Even if cases are tangentially related, explain HOW they relate. Don't dismiss them.

Answer:"""

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for factual accuracy
                max_tokens=1000,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Determine confidence based on similarity scores
            if best_score > 0.65:
                confidence = "high"
            elif best_score > 0.55:
                confidence = "medium"
            else:
                confidence = "low"
            
            return {
                "answer": answer,
                "confidence": confidence,
                "citations": [self._format_citation(doc) for doc in retrieved_docs],
                "model": self.llm_model,
                "retrieved_cases": len(retrieved_docs)
            }
        
        except Exception as e:
            return {
                "error": f"Error generating answer: {str(e)}",
                "answer": "I encountered an error while processing your question. Please try again.",
                "confidence": "error",
                "citations": []
            }
    
    def _format_citation(self, doc: Dict) -> Dict:
        """Format a document as a citation"""
        meta = doc["metadata"]
        return {
            "title": meta.get("title", "Unknown"),
            "court": meta.get("court", "Unknown"),
            "date": meta.get("date", "Unknown"),
            "case_number": meta.get("casenumber", "Unknown"),
            "relevance_score": round(doc["score"], 3),
            "doc_id": doc["doc_id"]
        }
    
    def ask(
        self,
        query: str,
        top_k: int = 5,
        include_raw_docs: bool = False
    ) -> Dict:
        """
        Main RAG pipeline: retrieve + generate
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            include_raw_docs: Include full retrieved documents in response
        
        Returns:
            Complete response with answer and metadata
        """
        print(f"\nProcessing query: {query}")
        
        # Step 1: Retrieve relevant documents
        print(f"Retrieving top {top_k} documents...")
        retrieved_docs = self.retrieve_documents(query, top_k=top_k)
        print(f"Retrieved {len(retrieved_docs)} documents")
        
        if retrieved_docs:
            print(f"Best match score: {retrieved_docs[0]['score']:.3f}")
        
        # Step 2: Generate answer
        print("Generating answer with LLM...")
        response = self.generate_answer(query, retrieved_docs)
        
        # Add query to response
        response["query"] = query
        
        # Optionally include raw docs
        if include_raw_docs:
            response["raw_documents"] = retrieved_docs
        
        print("Response generated!")
        return response


def main():
    """Test the RAG service"""
    print("=" * 60)
    print("Testing RAG Service")
    print("=" * 60)
    
    # Initialize service
    rag = RAGService()
    
    # Test queries
    test_queries = [
        "What are the grounds for eviction of a tenant?",
        "Can an employer terminate an employee without notice?",
        "What is the process for filing a consumer complaint?"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 60)
        response = rag.ask(query, top_k=3)
        
        print(f"\nQuery: {query}")
        print(f"\nConfidence: {response.get('confidence', 'unknown')}")
        print(f"\nAnswer:\n{response.get('answer', 'No answer')}")
        
        print(f"\nCitations ({len(response.get('citations', []))}):")
        for i, citation in enumerate(response.get("citations", []), 1):
            print(f"  {i}. {citation['title']}")
            print(f"     Court: {citation['court']}")
            print(f"     Date: {citation['date']}")
            print(f"     Relevance: {citation['relevance_score']}")
        
        print("\n" + "=" * 60)
        
        # Add delay to avoid rate limiting
        import time
        time.sleep(2)
    
    print("\nRAG service test complete!")


if __name__ == "__main__":
    main()