"""Test semantic search with case content preview"""

from rag_service import RAGService
import json
from pathlib import Path

rag = RAGService()

# Test queries
queries = [
    'property dispute between landlord and tenant',
    'employment termination without notice'
]

for q in queries:
    print('\n' + '='*80)
    print(f'QUERY: {q}')
    print('='*80)
    
    results = rag.retrieve_documents(q, top_k=3)
    
    for i, r in enumerate(results, 1):
        print(f'\n--- RESULT {i} (Score: {r["score"]:.3f}) ---')
        print(f'Title: {r["metadata"]["title"]}')
        print(f'Court: {r["metadata"]["court"]}')
        print(f'Date: {r["metadata"]["date"]}')
        
        # Load full document to show snippet
        doc_id = r["doc_id"]
        doc_path = Path(f'../data/raw/{doc_id}.json')
        
        if doc_path.exists():
            with open(doc_path, 'r') as f:
                doc_data = json.load(f)
                content = doc_data.get('doc', '')
                
                # Show first 500 chars of judgment
                print(f'\nContent Preview:')
                print(content[:500] + '...')
        
        print('\n' + '-'*80)