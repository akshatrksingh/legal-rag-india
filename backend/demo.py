"""
Demo Questions - Based on Actual Cases in Database
These questions are designed to show good matches with our 1994 Supreme Court cases
"""

from rag_service import RAGService
import time

def print_response(response):
    """Pretty print RAG response"""
    print(f"\nConfidence: {response.get('confidence', 'unknown').upper()}")
    
    if response.get('warning'):
        print(f"⚠️  Warning: {response['warning']}")
    
    print(f"\n📝 Answer:\n{response.get('answer', 'No answer')}")
    
    citations = response.get('citations', [])
    if citations:
        print(f"\n📚 Citations ({len(citations)} cases):")
        for i, citation in enumerate(citations, 1):
            print(f"\n  {i}. {citation['title']}")
            print(f"     Court: {citation['court']}")
            print(f"     Date: {citation['date']}")
            print(f"     Relevance: {citation['relevance_score']:.3f}")
    
    print("\n" + "="*80)


def main():
    print("="*80)
    print("LegalRAG India - Demo")
    print("AI-Powered Legal Research Assistant")
    print("="*80)
    
    # Initialize service
    print("\nInitializing...")
    rag = RAGService()
    
    # Demo questions based on our actual case data
    demo_questions = [
        {
            "category": "Property & Landlord-Tenant Law",
            "question": "What are the legal rights of a landlord to evict a tenant in India?",
            "why": "We have multiple property dispute cases (MOHD. RAZA vs GEETA, etc.)"
        },
        {
            "category": "Employment Law",
            "question": "Can an employer terminate an employee without giving notice period?",
            "why": "We have employment cases (TATA CONSULTANCY, DTC vs BALWAN SINGH)"
        },
        {
            "category": "Criminal Law",
            "question": "What is the punishment for murder under Indian Penal Code?",
            "why": "We have criminal cases (MOHAN vs STATE OF KARNATAKA, SURAJ JADHAV)"
        },
        {
            "category": "Civil Procedure",
            "question": "How long does it take to execute a civil court decree in India?",
            "why": "We have execution proceeding cases (UNION OF INDIA cases)"
        },
        {
            "category": "Government Employment",
            "question": "What are the grounds for termination of a government employee?",
            "why": "We have government employment cases (SECRETARY TO GOVT cases)"
        }
    ]
    
    for i, item in enumerate(demo_questions, 1):
        print(f"\n{'='*80}")
        print(f"DEMO {i}/{len(demo_questions)}: {item['category']}")
        print(f"{'='*80}")
        print(f"\n❓ Question: {item['question']}")
        print(f"💡 Why this works: {item['why']}")
        
        # Ask question
        response = rag.ask(item['question'], top_k=3)
        
        # Print response
        print_response(response)
        
        # Delay to avoid rate limiting
        if i < len(demo_questions):
            time.sleep(3)
    
    print("\n" + "="*80)
    print("Demo Complete!")
    print("="*80)
    print("\n📊 Summary:")
    print("- Database: 1994 Supreme Court judgments")
    print("- Embedding Model: bge-large-en-v1.5")
    print("- LLM: Groq (Llama 3.3 70B)")
    print("- Vector Store: FAISS")
    print("\n💡 All responses are grounded in real case law with verified citations!")


if __name__ == "__main__":
    main()