"""Embedding service using HuggingFace sentence-transformers."""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from backend.config import settings


class EmbeddingService:
    """Generate embeddings using HuggingFace sentence-transformers."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize embedding service with configured model."""
        if self._model is None:
            print(f"🔄 Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
            print(f"✅ Embedding model loaded (dimension: {settings.embedding_dimension})")
    
    @property
    def model(self) -> SentenceTransformer:
        """Get the embedding model."""
        return self._model
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return settings.embedding_dimension
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimension
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for batch of texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts and keep track of indices
        valid_texts = []
        valid_indices = []
        
        for idx, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(idx)
        
        if not valid_texts:
            # All texts are empty, return zero vectors
            return [[0.0] * self.dimension] * len(texts)
        
        # Generate embeddings for valid texts
        embeddings = self.model.encode(
            valid_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=show_progress
        )
        
        # Create result list with zero vectors for empty texts
        result = [[0.0] * self.dimension] * len(texts)
        
        # Fill in embeddings for valid texts
        for idx, embedding in zip(valid_indices, embeddings):
            result[idx] = embedding.tolist()
        
        return result
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def get_model_info(self) -> dict:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': settings.embedding_model,
            'dimension': self.dimension,
            'max_seq_length': self.model.max_seq_length,
            'device': str(self.model.device)
        }


# Example usage
if __name__ == "__main__":
    # Initialize service
    service = EmbeddingService()
    
    # Get model info
    info = service.get_model_info()
    print(f"Model: {info['model_name']}")
    print(f"Dimension: {info['dimension']}")
    print(f"Max sequence length: {info['max_seq_length']}")
    
    # Test single embedding
    text = "What is Retrieval-Augmented Generation?"
    embedding = service.embed_text(text)
    print(f"\nSingle embedding shape: {len(embedding)}")
    
    # Test batch embedding
    texts = [
        "RAG combines retrieval and generation",
        "Vector databases store embeddings",
        "Semantic search finds similar documents"
    ]
    embeddings = service.embed_batch(texts, show_progress=True)
    print(f"\nBatch embeddings: {len(embeddings)} vectors")
    
    # Test similarity
    sim = service.similarity(embeddings[0], embeddings[1])
    print(f"\nSimilarity between first two: {sim:.4f}")
