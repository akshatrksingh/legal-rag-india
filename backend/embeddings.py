"""
Embeddings Generator
Converts legal documents into vector embeddings for semantic search
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import time


class EmbeddingsGenerator:
    """Generate embeddings from legal documents using sentence-transformers"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """
        Initialize embeddings generator
        
        Args:
            model_name: HuggingFace model name for embeddings
                       Default: bge-large-en-v1.5 (1024 dimensions, high quality)
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def clean_html_text(self, html_content: str) -> str:
        """
        Extract clean text from HTML judgment content
        
        Args:
            html_content: Raw HTML string from judgment
        
        Returns:
            Clean text string
        """
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def prepare_document_text(self, doc: Dict) -> str:
        """
        Prepare document text for embedding
        Combines title, metadata, and judgment content
        
        Args:
            doc: Document dictionary from Indian Kanoon
        
        Returns:
            Prepared text string
        """
        parts = []
        
        # Add title
        if doc.get("title"):
            parts.append(f"Title: {doc['title']}")
        
        # Add court and date
        if doc.get("court"):
            parts.append(f"Court: {doc['court']}")
        if doc.get("date"):
            parts.append(f"Date: {doc['date']}")
        
        # Add case number
        if doc.get("casenumber"):
            parts.append(f"Case Number: {doc['casenumber']}")
        
        # Add bench information
        if doc.get("bench"):
            bench_str = ", ".join(doc["bench"]) if isinstance(doc["bench"], list) else doc["bench"]
            parts.append(f"Bench: {bench_str}")
        
        # Add main judgment text (cleaned)
        if doc.get("doc"):
            clean_text = self.clean_html_text(doc["doc"])
            parts.append(clean_text)
        
        return "\n".join(parts)
    
    def generate_embeddings(
        self, 
        documents: List[Dict],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> Tuple[np.ndarray, List[str], List[Dict]]:
        """
        Generate embeddings for a list of documents
        
        Args:
            documents: List of document dictionaries
            batch_size: Number of documents to process at once
            show_progress: Whether to print progress
        
        Returns:
            Tuple of (embeddings_array, doc_ids, metadata_list)
        """
        print(f"\nGenerating embeddings for {len(documents)} documents...")
        print(f"Batch size: {batch_size}")
        
        doc_ids = []
        texts = []
        metadata = []
        
        # Prepare all texts
        for i, doc in enumerate(documents):
            doc_id = doc.get("tid", f"unknown_{i}")
            text = self.prepare_document_text(doc)
            
            doc_ids.append(doc_id)
            texts.append(text)
            
            # Store metadata
            meta = {
                "doc_id": doc_id,
                "title": doc.get("title", ""),
                "court": doc.get("court", ""),
                "date": doc.get("date", ""),
                "casenumber": doc.get("casenumber", ""),
            }
            metadata.append(meta)
            
            if show_progress and (i + 1) % 20 == 0:
                print(f"  Prepared {i + 1}/{len(documents)} documents")
        
        # Generate embeddings in batches
        print("\nEncoding documents...")
        start_time = time.time()
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        elapsed = time.time() - start_time
        print(f"Encoding complete in {elapsed:.2f} seconds")
        print(f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
        
        return embeddings, doc_ids, metadata
    
    def load_documents_from_directory(self, directory: str) -> List[Dict]:
        """
        Load all JSON documents from a directory
        
        Args:
            directory: Path to directory containing JSON files
        
        Returns:
            List of document dictionaries
        """
        doc_path = Path(directory)
        json_files = list(doc_path.glob("*.json"))
        
        # Filter out summary files
        json_files = [f for f in json_files if not f.name.startswith("_")]
        
        print(f"Loading documents from {directory}")
        print(f"Found {len(json_files)} JSON files")
        
        documents = []
        for i, file_path in enumerate(json_files):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    documents.append(doc)
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
            
            if (i + 1) % 50 == 0:
                print(f"  Loaded {i + 1}/{len(json_files)} files")
        
        print(f"Successfully loaded {len(documents)} documents")
        return documents
    
    def save_embeddings(
        self,
        embeddings: np.ndarray,
        doc_ids: List[str],
        metadata: List[Dict],
        output_dir: str = "../data/processed"
    ):
        """
        Save embeddings and metadata to disk
        
        Args:
            embeddings: Numpy array of embeddings
            doc_ids: List of document IDs
            metadata: List of metadata dictionaries
            output_dir: Directory to save files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save embeddings as numpy array
        embeddings_file = output_path / "embeddings.npy"
        np.save(embeddings_file, embeddings)
        print(f"Saved embeddings to {embeddings_file}")
        
        # Save doc IDs
        doc_ids_file = output_path / "doc_ids.pkl"
        with open(doc_ids_file, "wb") as f:
            pickle.dump(doc_ids, f)
        print(f"Saved doc IDs to {doc_ids_file}")
        
        # Save metadata
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"Saved metadata to {metadata_file}")
        
        # Save config
        config = {
            "model_name": self.model_name,
            "num_documents": len(doc_ids),
            "embedding_dimension": embeddings.shape[1],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        config_file = output_path / "embeddings_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Saved config to {config_file}")
    
    def load_embeddings(
        self,
        input_dir: str = "../data/processed"
    ) -> Tuple[np.ndarray, List[str], List[Dict]]:
        """
        Load embeddings and metadata from disk
        
        Args:
            input_dir: Directory containing saved files
        
        Returns:
            Tuple of (embeddings_array, doc_ids, metadata_list)
        """
        input_path = Path(input_dir)
        
        # Load embeddings
        embeddings_file = input_path / "embeddings.npy"
        embeddings = np.load(embeddings_file)
        
        # Load doc IDs
        doc_ids_file = input_path / "doc_ids.pkl"
        with open(doc_ids_file, "rb") as f:
            doc_ids = pickle.load(f)
        
        # Load metadata
        metadata_file = input_path / "metadata.json"
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        print(f"Loaded {len(embeddings)} embeddings from {input_dir}")
        return embeddings, doc_ids, metadata


def main():
    """Test the embeddings generator"""
    print("=" * 60)
    print("Testing Embeddings Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = EmbeddingsGenerator()
    
    # Load documents
    documents = generator.load_documents_from_directory("../data/raw")
    
    if not documents:
        print("No documents found. Run mock_data.py first!")
        return
    
    # Generate embeddings
    embeddings, doc_ids, metadata = generator.generate_embeddings(
        documents,
        batch_size=32,
        show_progress=True
    )
    
    # Save to disk
    generator.save_embeddings(embeddings, doc_ids, metadata)
    
    print("\n" + "=" * 60)
    print("Embeddings generation complete!")
    print("=" * 60)
    print(f"Total documents: {len(doc_ids)}")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Files saved to: ../data/processed/")


if __name__ == "__main__":
    main()