"""Hybrid search combining dense and sparse retrieval."""

from typing import List, Dict, Optional
from rank_bm25 import BM25Okapi
from backend.services.vector_store import VectorStore
import numpy as np


class HybridSearch:
    """Hybrid search combining dense vector search and sparse BM25."""
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize hybrid search.
        
        Args:
            vector_store: Vector store instance for dense retrieval
        """
        self.vector_store = vector_store
        self.bm25_index = None
        self.bm25_corpus = []
        self.bm25_metadata = []
    
    def index_for_bm25(self, chunks: List[Dict]):
        """
        Build BM25 index for sparse retrieval.
        
        Args:
            chunks: List of chunks to index
        """
        if not chunks:
            self.bm25_index = None
            self.bm25_corpus = []
            self.bm25_metadata = []
            return
        
        print(f"🔄 Building BM25 index for {len(chunks)} chunks...")
        
        self.bm25_corpus = [chunk['content'] for chunk in chunks]
        self.bm25_metadata = chunks
        
        # Tokenize corpus (simple whitespace tokenization)
        tokenized_corpus = [doc.lower().split() for doc in self.bm25_corpus]
        self.bm25_index = BM25Okapi(tokenized_corpus)
        
        print(f"✅ BM25 index built")
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform hybrid search with score fusion.
        
        Args:
            query: Search query
            top_k: Number of results to return
            dense_weight: Weight for dense (vector) search
            sparse_weight: Weight for sparse (BM25) search
            filter_dict: Optional metadata filter for dense search
            
        Returns:
            List of results with fused scores
        """
        # Validate weights
        if abs(dense_weight + sparse_weight - 1.0) > 0.01:
            raise ValueError("dense_weight + sparse_weight must equal 1.0")
        
        # Dense retrieval (vector search)
        dense_results = await self.vector_store.similarity_search(
            query, 
            top_k=top_k * 2,  # Get more results for better fusion
            filter_dict=filter_dict
        )
        
        # Sparse retrieval (BM25)
        sparse_results = self._bm25_search(query, top_k=top_k * 2)
        
        # Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(
            dense_results,
            sparse_results,
            dense_weight,
            sparse_weight
        )
        
        return fused_results[:top_k]
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict]:
        """
        Perform BM25 sparse search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of results with BM25 scores
        """
        if self.bm25_index is None:
            print("⚠️  BM25 index not built, returning empty results")
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                chunk = self.bm25_metadata[idx]
                results.append({
                    'chunk_id': chunk.get('chunk_id', f'bm25_{idx}'),
                    'score': float(scores[idx]),
                    'content': self.bm25_corpus[idx],
                    'metadata': chunk.get('metadata', {})
                })
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        dense_weight: float,
        sparse_weight: float,
        k: int = 60
    ) -> List[Dict]:
        """
        Fuse results using Reciprocal Rank Fusion (RRF).
        
        RRF formula: score = weight / (k + rank)
        
        Args:
            dense_results: Results from dense search
            sparse_results: Results from sparse search
            dense_weight: Weight for dense results
            sparse_weight: Weight for sparse results
            k: RRF constant (default 60)
            
        Returns:
            Fused and sorted results
        """
        # Create score dictionary
        fused_scores = {}
        
        # Add dense scores
        for rank, result in enumerate(dense_results, 1):
            chunk_id = result['chunk_id']
            fused_scores[chunk_id] = {
                'score': dense_weight / (k + rank),
                'content': result['content'],
                'metadata': result['metadata'],
                'dense_rank': rank,
                'sparse_rank': None,
                'dense_score': result.get('score', 0)
            }
        
        # Add sparse scores
        for rank, result in enumerate(sparse_results, 1):
            chunk_id = result['chunk_id']
            if chunk_id in fused_scores:
                # Chunk appears in both results
                fused_scores[chunk_id]['score'] += sparse_weight / (k + rank)
                fused_scores[chunk_id]['sparse_rank'] = rank
                fused_scores[chunk_id]['sparse_score'] = result.get('score', 0)
            else:
                # Chunk only in sparse results
                fused_scores[chunk_id] = {
                    'score': sparse_weight / (k + rank),
                    'content': result['content'],
                    'metadata': result['metadata'],
                    'dense_rank': None,
                    'sparse_rank': rank,
                    'sparse_score': result.get('score', 0)
                }
        
        # Sort by fused score
        sorted_results = sorted(
            [
                {'chunk_id': cid, **data}
                for cid, data in fused_scores.items()
            ],
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_results
    
    def get_search_stats(self) -> Dict:
        """
        Get statistics about the search indices.
        
        Returns:
            Dictionary with search statistics
        """
        vector_stats = self.vector_store.get_stats()
        
        return {
            'vector_store': vector_stats,
            'bm25_corpus_size': len(self.bm25_corpus),
            'bm25_indexed': self.bm25_index is not None
        }
