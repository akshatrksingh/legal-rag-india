"""
Kaggle Dataset Converter
Converts Kaggle Supreme Court dataset (CSV + PDFs) to our JSON format
"""

import pandas as pd
import pdfplumber
import json
from pathlib import Path
from typing import Dict, Optional
import re


class KaggleDatasetConverter:
    """Convert Kaggle dataset to our pipeline format"""
    
    def __init__(
        self,
        csv_path: str = "../data/kaggle_raw/judgments.csv",
        pdf_dir: str = "../data/kaggle_raw/pdfs",
        output_dir: str = "../data/raw"
    ):
        self.csv_path = Path(csv_path)
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text or None if failed
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n\n".join(text_parts)
        except Exception as e:
            print(f"Error extracting PDF {pdf_path.name}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers pattern
        text = re.sub(r'\n\d+\n', '\n', text)
        
        return text.strip()
    
    def convert_row_to_json(self, row: pd.Series, doc_id: int) -> Dict:
        """
        Convert CSV row + PDF to our JSON format
        
        Args:
            row: DataFrame row with metadata
            doc_id: Unique document ID
        
        Returns:
            Document dict in our format
        """
        # Build title from petitioner vs respondent
        petitioner = str(row.get('pet', '')).strip()
        respondent = str(row.get('res', '')).strip()
        
        if petitioner and respondent:
            title = f"{petitioner} vs {respondent}"
        else:
            title = f"Case {row.get('case_no', doc_id)}"
        
        # Parse bench (list of judges)
        bench_str = str(row.get('bench', ''))
        bench = [judge.strip() for judge in bench_str.split(',') if judge.strip()]
        
        # Get judgment author
        author = str(row.get('judgement_by', '')).strip()
        
        # Convert date format
        date_str = str(row.get('judgment_dates', ''))
        
        # Extract PDF text
        pdf_filename = str(row.get('temp_link', ''))
        # PDF filename might be in temp_link or we need to find it
        pdf_name = Path(pdf_filename).name if pdf_filename else None
        
        judgment_text = ""
        if pdf_name:
            pdf_path = self.pdf_dir / pdf_name
            if pdf_path.exists():
                judgment_text = self.extract_text_from_pdf(pdf_path)
            else:
                # Try finding by diary number
                diary_no = str(row.get('diary_no', ''))
                matching_pdfs = list(self.pdf_dir.glob(f"*{diary_no}*.pdf"))
                if matching_pdfs:
                    judgment_text = self.extract_text_from_pdf(matching_pdfs[0])
        
        # Clean text
        judgment_text = self.clean_text(judgment_text)
        
        # Build document
        doc = {
            "tid": str(1000000 + doc_id),  # Start from 1000000 like mock data
            "title": title,
            "doc": judgment_text,
            "court": "Supreme Court of India",
            "date": date_str,
            "casenumber": str(row.get('case_no', '')),
            "bench": bench,
            "author": author,
            "citeList": [],
            "citedbyList": [],
            "search_metadata": {
                "title": title,
                "headline": f"Supreme Court judgment dated {date_str}",
                "docsource": "Supreme Court of India",
                "docsize": len(judgment_text),
                "petitioner": petitioner,
                "respondent": respondent,
                "diary_no": str(row.get('diary_no', ''))
            }
        }
        
        return doc
    
    def convert_dataset(
        self,
        max_docs: int = 1000,
        skip_failed: bool = True
    ):
        """
        Convert Kaggle dataset to our format
        
        Args:
            max_docs: Maximum number of documents to convert
            skip_failed: Skip documents that fail to process
        """
        print(f"Converting Kaggle dataset...")
        print(f"Reading CSV from: {self.csv_path}")
        
        # Load CSV
        df = pd.read_csv(self.csv_path)
        print(f"Found {len(df)} judgments in CSV")
        
        # Limit number of docs
        df = df.head(max_docs)
        print(f"Processing {len(df)} documents")
        
        converted = 0
        failed = 0
        
        for idx, row in df.iterrows():
            doc_id = idx
            
            try:
                # Convert to JSON
                doc = self.convert_row_to_json(row, doc_id)
                
                # Check if we got text
                if not doc["doc"] or len(doc["doc"]) < 100:
                    print(f"  [{idx+1}/{len(df)}] Skipped (no text): {doc['title'][:50]}...")
                    failed += 1
                    if not skip_failed:
                        continue
                else:
                    # Save to file
                    output_file = self.output_dir / f"{doc['tid']}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(doc, f, ensure_ascii=False, indent=2)
                    
                    converted += 1
                    if converted % 50 == 0:
                        print(f"  Converted {converted}/{len(df)} documents...")
            
            except Exception as e:
                print(f"  [{idx+1}/{len(df)}] Error: {e}")
                failed += 1
                if not skip_failed:
                    raise
        
        print(f"\nConversion complete!")
        print(f"  Successfully converted: {converted}")
        print(f"  Failed/Skipped: {failed}")
        print(f"  Output directory: {self.output_dir}")
        
        # Save summary
        summary = {
            "source": "Kaggle Supreme Court Judgments",
            "total_in_csv": len(df),
            "successfully_converted": converted,
            "failed": failed,
            "output_directory": str(self.output_dir)
        }
        
        summary_file = self.output_dir / "_conversion_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"  Summary saved to: {summary_file}")


def main():
    """Run the converter"""
    import sys
    
    # Get number of docs from command line or use default
    max_docs = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    
    print("=" * 60)
    print("Kaggle Dataset Converter")
    print("=" * 60)
    
    converter = KaggleDatasetConverter()
    converter.convert_dataset(max_docs=max_docs)
    
    print("\n" + "=" * 60)
    print("Ready for embeddings generation!")
    print("Next steps:")
    print("  1. cd backend")
    print("  2. python embeddings.py")
    print("  3. python vector_store.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
