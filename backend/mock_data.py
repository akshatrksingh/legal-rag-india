"""
Mock data generator for testing when Indian Kanoon API is unavailable
Creates realistic fake judgment data for development
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta


# Sample legal terms and phrases for realistic content
LEGAL_TERMS = [
    "contract", "tort", "negligence", "liability", "damages", "breach",
    "plaintiff", "defendant", "appellant", "respondent", "petition",
    "writ", "mandamus", "certiorari", "habeas corpus", "prima facie",
    "res judicata", "stare decisis", "obiter dicta", "ratio decidendi"
]

CASE_TYPES = [
    "Civil Appeal", "Criminal Appeal", "Special Leave Petition", 
    "Writ Petition", "Transfer Petition", "Review Petition"
]

COURTS = [
    "Supreme Court of India",
    "Delhi High Court",
    "Bombay High Court",
    "Calcutta High Court",
    "Madras High Court"
]

JUDGES = [
    "Justice A.K. Sikri", "Justice S.A. Bobde", "Justice N.V. Ramana",
    "Justice D.Y. Chandrachud", "Justice Rohinton Nariman",
    "Justice Indu Malhotra", "Justice Hemant Gupta"
]


def generate_mock_judgment(doc_id: int) -> dict:
    """Generate a realistic mock judgment document"""
    
    # Random date within last 10 years
    days_ago = random.randint(1, 3650)
    judgment_date = datetime.now() - timedelta(days=days_ago)
    
    # Generate case details
    case_number = f"{random.randint(100, 9999)}/20{judgment_date.year % 100}"
    court = random.choice(COURTS)
    case_type = random.choice(CASE_TYPES)
    
    # Generate parties
    petitioner = f"Party {chr(65 + random.randint(0, 25))}"
    respondent = f"Party {chr(65 + random.randint(0, 25))}"
    
    # Generate bench
    num_judges = random.randint(1, 3)
    bench = random.sample(JUDGES, num_judges)
    
    # Generate judgment text (simplified)
    judgment_text = f"""
    <div class="judgment">
        <div class="docsource">{court}</div>
        <div class="docdate">{judgment_date.strftime('%d %B %Y')}</div>
        <div class="docnumber">{case_type} No. {case_number}</div>
        
        <h2>{petitioner} vs {respondent}</h2>
        
        <div class="bench">
            <p><strong>Bench:</strong> {', '.join(bench)}</p>
        </div>
        
        <div class="judgment_text">
            <p>This is a case concerning {random.choice(LEGAL_TERMS)} law. 
            The {petitioner} filed a {case_type} against {respondent} alleging 
            {random.choice(LEGAL_TERMS)} and seeking relief.</p>
            
            <p>Upon consideration of the facts and circumstances, and after 
            hearing the learned counsel for both parties, we find that the 
            principles of {random.choice(LEGAL_TERMS)} are applicable in this case.</p>
            
            <p>In light of the established precedents and the legal principles 
            governing {random.choice(LEGAL_TERMS)}, we hold that the appellant's 
            claim is maintainable. The doctrine of {random.choice(LEGAL_TERMS)} 
            supports this interpretation.</p>
            
            <p><strong>ORDER:</strong> The appeal is allowed. The judgment of the 
            lower court is set aside. Parties to bear their own costs.</p>
        </div>
    </div>
    """
    
    # Create document structure matching Indian Kanoon API response
    doc = {
        "tid": str(1000000 + doc_id),
        "title": f"{petitioner} vs {respondent}",
        "doc": judgment_text,
        "court": court,
        "date": judgment_date.strftime("%d/%m/%Y"),
        "casenumber": case_number,
        "bench": bench,
        "author": bench[0] if bench else None,
        "citeList": [],  # Citations this case makes
        "citedbyList": [],  # Cases that cite this one
        "search_metadata": {
            "title": f"{petitioner} vs {respondent}",
            "headline": f"Case concerning {random.choice(LEGAL_TERMS)} law...",
            "docsource": court,
            "docsize": len(judgment_text)
        }
    }
    
    return doc


def generate_mock_dataset(num_docs: int = 100, output_dir: str = "../data/raw"):
    """Generate a dataset of mock judgments for testing"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {num_docs} mock judgments...")
    
    documents = []
    for i in range(num_docs):
        doc = generate_mock_judgment(i)
        documents.append(doc)
        
        # Save individual document
        doc_file = output_path / f"{doc['tid']}.json"
        with open(doc_file, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        
        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/{num_docs} documents...")
    
    # Save summary
    summary = {
        "source": "mock_data_generator",
        "total_documents": len(documents),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "This is synthetic data for development/testing"
    }
    
    summary_file = output_path / "_download_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Generated {num_docs} mock judgments!")
    print(f"Saved to: {output_path}")
    
    return documents


if __name__ == "__main__":
    # Generate 100 mock documents for testing
    generate_mock_dataset(num_docs=100)