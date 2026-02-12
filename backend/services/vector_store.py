"""Pinecone vector database interface."""

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
from backend.config import settings
from backend.services.embedding_service import EmbeddingService
import time


class VectorStore:
    """Pinecone vector database interface."""
    
    def __init__(self):
        """Initialize Pinecone connection and embedding service."""
        if not settings.pinecone_api_key:
            raise ValueError(
                "Pinecone API key not configured. "
                "Please set PINECONE_API_KEY in .env file"
            )
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.embedding_service = EmbeddingService()
        
        # Ensure index exists
        self._ensure_index_exists()
        
        # Get index
        self.index = self.pc.Index(self.index_name)
        
        print(f"✅ Connected to Pinecone index: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist."""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"🔄 Creating Pinecone index: {self.index_name}")
            
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_service.dimension,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=settings.pinecone_environment
                )
            )
            
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
            print(f"✅ Index created: {self.index_name}")
        else:
            print(f"✅ Index already exists: {self.index_name}")
    
    async def add_chunks(self, chunks: List[Dict]) -> int:
        """
        Add document chunks to vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_id', 'content', 'metadata'
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        # Extract texts for embedding
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings in batch
        print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedding_service.embed_batch(texts, show_progress=True)
        
        # Prepare vectors for Pinecone
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            # Prepare metadata (Pinecone has size limits)
            metadata = {
                'doc_id': chunk['metadata']['doc_id'],
                'filename': chunk['metadata']['filename'],
                'chunk_index': chunk['metadata']['chunk_index'],
                'page_number': chunk['metadata'].get('page_number'),
                'content': chunk['content'][:1000]  # Store preview (max 1000 chars)
            }
            
            vectors.append({
                'id': chunk['chunk_id'],
                'values': embedding,
                'metadata': metadata
            })
        
        # Upsert to Pinecone in batches
        batch_size = 100
        total_upserted = 0
        
        print(f"🔄 Upserting {len(vectors)} vectors to Pinecone...")
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            total_upserted += len(batch)
            print(f"   Upserted {total_upserted}/{len(vectors)} vectors")
        
        print(f"✅ Added {total_upserted} chunks to vector store")
        return total_upserted
    
    async def similarity_search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform dense vector similarity search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of matching chunks with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        formatted_results = []
        for match in results['matches']:
            formatted_results.append({
                'chunk_id': match['id'],
                'score': match['score'],
                'content': match['metadata'].get('content', ''),
                'metadata': {
                    'doc_id': match['metadata'].get('doc_id'),
                    'filename': match['metadata'].get('filename'),
                    'chunk_index': match['metadata'].get('chunk_index'),
                    'page_number': match['metadata'].get('page_number')
                }
            })
        
        return formatted_results
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            # Delete by metadata filter
            self.index.delete(filter={'doc_id': doc_id})
            print(f"✅ Deleted document {doc_id} from vector store")
            return True
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False
    
    async def delete_chunks(self, chunk_ids: List[str]) -> bool:
        """
        Delete specific chunks by ID.
        
        Args:
            chunk_ids: List of chunk IDs to delete
            
        Returns:
            True if successful
        """
        try:
            self.index.delete(ids=chunk_ids)
            print(f"✅ Deleted {len(chunk_ids)} chunks from vector store")
            return True
        except Exception as e:
            print(f"❌ Error deleting chunks: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with index statistics
        """
        stats = self.index.describe_index_stats()
        return {
            'total_vectors': stats.get('total_vector_count', 0),
            'dimension': stats.get('dimension', 0),
            'index_fullness': stats.get('index_fullness', 0)
        }
    
    async def search_by_document(self, doc_id: str, top_k: int = 10) -> List[Dict]:
        """
        Get all chunks for a specific document.
        
        Args:
            doc_id: Document ID
            top_k: Maximum number of chunks to return
            
        Returns:
            List of chunks from the document
        """
        # This is a workaround since Pinecone doesn't have a direct "get by filter" method
        # We'll use a dummy query with a filter
        dummy_query = "document content"
        
        return await self.similarity_search(
            query=dummy_query,
            top_k=top_k,
            filter_dict={'doc_id': doc_id}
        )
