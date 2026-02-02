"""
FAISS Vector Store
Semantic search over legal document embeddings
"""

import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class VectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, dimension: int = 1024):
        """
        Initialize vector store
        
        Args:
            dimension: Embedding dimension (default: 1024 for bge-large)
        """
        self.dimension = dimension
        self.index = None
        self.doc_ids = []
        self.metadata = []
    
    def build_index(
        self,
        embeddings: np.ndarray,
        doc_ids: List[str],
        metadata: List[Dict],
        index_type: str = "flat"
    ):
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: Numpy array of shape (n_docs, dimension)
            doc_ids: List of document IDs
            metadata: List of metadata dicts
            index_type: "flat" (exact) or "ivf" (approximate, faster for large datasets)
        """
        print(f"Building FAISS index with {len(embeddings)} documents...")
        
        # Validate inputs
        assert embeddings.shape[0] == len(doc_ids) == len(metadata)
        assert embeddings.shape[1] == self.dimension
        
        # Store data
        self.doc_ids = doc_ids
        self.metadata = metadata
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Build index
        if index_type == "flat":
            # Exact search (good for <100K docs)
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product = cosine after normalize
        elif index_type == "ivf":
            # Approximate search (good for >100K docs)
            nlist = min(100, len(embeddings) // 10)  # Number of clusters
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(embeddings)
        else:
            raise ValueError(f"Unknown index_type: {index_type}")
        
        # Add vectors to index
        self.index.add(embeddings)
        
        print(f"Index built successfully!")
        print(f"  Total vectors: {self.index.ntotal}")
        print(f"  Index type: {index_type}")
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1), None for no filtering
        
        Returns:
            List of dicts with doc_id, score, and metadata
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Reshape and normalize query
        query = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query)
        
        # Search
        scores, indices = self.index.search(query, k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            # Skip if below threshold
            if score_threshold is not None and score < score_threshold:
                continue
            
            # Skip invalid indices
            if idx < 0 or idx >= len(self.doc_ids):
                continue
            
            result = {
                "doc_id": self.doc_ids[idx],
                "score": float(score),
                "metadata": self.metadata[idx]
            }
            results.append(result)
        
        return results
    
    def batch_search(
        self,
        query_embeddings: np.ndarray,
        k: int = 5
    ) -> List[List[Dict]]:
        """
        Search for multiple queries at once
        
        Args:
            query_embeddings: Array of shape (n_queries, dimension)
            k: Number of results per query
        
        Returns:
            List of result lists (one per query)
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Normalize queries
        queries = query_embeddings.astype('float32')
        faiss.normalize_L2(queries)
        
        # Batch search
        scores, indices = self.index.search(queries, k)
        
        # Format results
        all_results = []
        for query_scores, query_indices in zip(scores, indices):
            query_results = []
            for score, idx in zip(query_scores, query_indices):
                if idx >= 0 and idx < len(self.doc_ids):
                    result = {
                        "doc_id": self.doc_ids[idx],
                        "score": float(score),
                        "metadata": self.metadata[idx]
                    }
                    query_results.append(result)
            all_results.append(query_results)
        
        return all_results
    
    def save(self, output_dir: str = "data/processed"):
        """
        Save index and metadata to disk
        
        Args:
            output_dir: Directory to save files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = output_path / "faiss_index.bin"
        faiss.write_index(self.index, str(index_file))
        print(f"Saved FAISS index to {index_file}")
        
        # Save doc IDs
        doc_ids_file = output_path / "doc_ids.pkl"
        with open(doc_ids_file, "wb") as f:
            pickle.dump(self.doc_ids, f)
        print(f"Saved doc IDs to {doc_ids_file}")
        
        # Save metadata
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        print(f"Saved metadata to {metadata_file}")
    
    def load(self, input_dir: str = "data/processed"):
        """
        Load index and metadata from disk
        
        Args:
            input_dir: Directory containing saved files
        """
        input_path = Path(input_dir)
        
        # Load FAISS index
        index_file = input_path / "faiss_index.bin"
        self.index = faiss.read_index(str(index_file))
        print(f"Loaded FAISS index from {index_file}")
        
        # Load doc IDs
        doc_ids_file = input_path / "doc_ids.pkl"
        with open(doc_ids_file, "rb") as f:
            self.doc_ids = pickle.load(f)
        print(f"Loaded {len(self.doc_ids)} doc IDs")
        
        # Load metadata
        metadata_file = input_path / "metadata.json"
        with open(metadata_file, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        print(f"Loaded metadata for {len(self.metadata)} documents")
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific document
        
        Args:
            doc_id: Document ID
        
        Returns:
            Metadata dict or None if not found
        """
        try:
            idx = self.doc_ids.index(doc_id)
            return self.metadata[idx]
        except ValueError:
            return None
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dict with stats
        """
        return {
            "total_documents": len(self.doc_ids),
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "is_trained": self.index.is_trained if hasattr(self.index, 'is_trained') else True
        }


def main():
    """Test the vector store"""
    from embeddings import EmbeddingsGenerator
    
    print("=" * 60)
    print("Testing Vector Store")
    print("=" * 60)
    
    # Load embeddings
    print("\n[1/4] Loading embeddings...")
    embeddings_file = "data/processed/embeddings.npy"
    doc_ids_file = "data/processed/doc_ids.pkl"
    metadata_file = "data/processed/metadata.json"
    
    embeddings = np.load(embeddings_file)
    with open(doc_ids_file, "rb") as f:
        doc_ids = pickle.load(f)
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    print(f"Loaded {len(embeddings)} embeddings")
    
    # Build index
    print("\n[2/4] Building FAISS index...")
    store = VectorStore(dimension=1024)
    store.build_index(embeddings, doc_ids, metadata, index_type="flat")
    
    # Test search
    print("\n[3/4] Testing search...")
    
    # Create a query (use first document as test)
    query_embedding = embeddings[0]
    
    print(f"Query: {metadata[0]['title']}")
    results = store.search(query_embedding, k=5)
    
    print(f"\nTop 5 results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['metadata']['title']}")
        print(f"     Score: {result['score']:.3f}")
        print(f"     Court: {result['metadata']['court']}")
        print()
    
    # Save index
    print("[4/4] Saving vector store...")
    store.save()
    
    # Test loading
    print("\nTesting load...")
    store2 = VectorStore(dimension=1024)
    store2.load()
    
    print(f"\nVector store stats:")
    stats = store2.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Vector store test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()