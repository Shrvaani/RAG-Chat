"""Intelligent document chunking service with metadata preservation."""

from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import settings
import re


class ChunkingService:
    """Intelligent document chunking with metadata preservation."""
    
    def __init__(self):
        """Initialize chunking service with configurable parameters."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ": ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )
    
    def chunk_document(self, content: str, metadata: Dict) -> List[Dict]:
        """
        Split document into chunks with metadata.
        
        Args:
            content: Document text content
            metadata: Document metadata
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # Extract page information if present (from PDF)
        page_pattern = r'\[Page (\d+)\]\n'
        sections = re.split(page_pattern, content)
        
        if len(sections) > 1:
            # PDF with page markers
            chunks = self._chunk_with_pages(sections, metadata)
        else:
            # Plain text without page markers
            chunks = self._chunk_plain_text(content, metadata)
        
        return chunks
    
    def _chunk_with_pages(self, sections: List[str], metadata: Dict) -> List[Dict]:
        """
        Chunk PDF content preserving page numbers.
        
        Args:
            sections: List of page sections from regex split
            metadata: Document metadata
            
        Returns:
            List of chunks with page number metadata
        """
        chunks = []
        chunk_index = 0
        
        # sections format: ['', '1', 'page 1 text', '2', 'page 2 text', ...]
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                page_num = int(sections[i])
                page_text = sections[i + 1].strip()
                
                # Skip empty pages
                if not page_text or page_text == "[No text content]":
                    continue
                
                # Split page text into chunks
                page_chunks = self.text_splitter.split_text(page_text)
                
                for chunk_text in page_chunks:
                    # Skip very small chunks (likely noise)
                    if len(chunk_text.strip()) < 10:
                        continue
                    
                    chunks.append({
                        'chunk_id': f"{metadata['doc_id']}_chunk_{chunk_index}",
                        'content': chunk_text.strip(),
                        'metadata': {
                            'doc_id': metadata['doc_id'],
                            'filename': metadata['filename'],
                            'file_type': metadata['file_type'],
                            'chunk_index': chunk_index,
                            'page_number': page_num,
                            'total_chunks': None,  # Will update later
                            'upload_timestamp': metadata['upload_timestamp']
                        }
                    })
                    chunk_index += 1
        
        # Update total chunks count
        total = len(chunks)
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = total
        
        return chunks
    
    def _chunk_plain_text(self, content: str, metadata: Dict) -> List[Dict]:
        """
        Chunk plain text files.
        
        Args:
            content: Text content
            metadata: Document metadata
            
        Returns:
            List of chunks without page numbers
        """
        chunks = []
        text_chunks = self.text_splitter.split_text(content)
        
        for idx, chunk_text in enumerate(text_chunks):
            # Skip very small chunks
            if len(chunk_text.strip()) < 10:
                continue
            
            chunks.append({
                'chunk_id': f"{metadata['doc_id']}_chunk_{idx}",
                'content': chunk_text.strip(),
                'metadata': {
                    'doc_id': metadata['doc_id'],
                    'filename': metadata['filename'],
                    'file_type': metadata['file_type'],
                    'chunk_index': idx,
                    'page_number': None,
                    'total_chunks': len(text_chunks),
                    'upload_timestamp': metadata['upload_timestamp']
                }
            })
        
        return chunks
    
    def get_chunk_stats(self, chunks: List[Dict]) -> Dict:
        """
        Get statistics about chunks.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'avg_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0
            }
        
        chunk_sizes = [len(chunk['content']) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(chunk_sizes) // len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes)
        }
    
    def merge_small_chunks(self, chunks: List[Dict], min_size: int = 100) -> List[Dict]:
        """
        Merge chunks that are too small.
        
        Args:
            chunks: List of chunks
            min_size: Minimum chunk size in characters
            
        Returns:
            List of chunks with small ones merged
        """
        if not chunks:
            return []
        
        merged = []
        buffer = ""
        buffer_metadata = None
        
        for chunk in chunks:
            content = chunk['content']
            
            if len(content) < min_size:
                # Accumulate small chunks
                if buffer:
                    buffer += " " + content
                else:
                    buffer = content
                    buffer_metadata = chunk['metadata'].copy()
            else:
                # Flush buffer if exists
                if buffer:
                    merged.append({
                        'chunk_id': f"{buffer_metadata['doc_id']}_chunk_{len(merged)}",
                        'content': buffer,
                        'metadata': buffer_metadata
                    })
                    buffer = ""
                    buffer_metadata = None
                
                # Add current chunk
                merged.append(chunk)
        
        # Flush remaining buffer
        if buffer and buffer_metadata:
            merged.append({
                'chunk_id': f"{buffer_metadata['doc_id']}_chunk_{len(merged)}",
                'content': buffer,
                'metadata': buffer_metadata
            })
        
        # Update chunk indices and total
        for idx, chunk in enumerate(merged):
            chunk['metadata']['chunk_index'] = idx
            chunk['metadata']['total_chunks'] = len(merged)
        
        return merged
