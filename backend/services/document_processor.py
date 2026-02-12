"""Document processing service for handling file uploads and text extraction."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber
from backend.config import settings


class DocumentProcessor:
    """Handle document upload and text extraction."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf'}
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_upload(self, file_content: bytes, filename: str) -> Dict:
        """
        Process uploaded file and extract text.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dictionary with metadata and extracted content
            
        Raises:
            ValueError: If file type is not supported
        """
        # Validate file type
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {file_ext}. "
                f"Supported types: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Save file
        safe_filename = self._sanitize_filename(filename)
        file_path = self.upload_dir / f"{doc_id}_{safe_filename}"
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Extract text
        text_content = self._extract_text(file_path, file_ext)
        
        # Create metadata
        metadata = {
            'doc_id': doc_id,
            'filename': filename,
            'file_path': str(file_path),
            'file_type': file_ext,
            'upload_timestamp': timestamp,
            'file_size': len(file_content),
            'char_count': len(text_content),
            'word_count': len(text_content.split())
        }
        
        return {
            'metadata': metadata,
            'content': text_content
        }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        # Remove path components and keep only the filename
        filename = os.path.basename(filename)
        # Replace spaces and special characters
        filename = filename.replace(' ', '_')
        return filename
    
    def _extract_text(self, file_path: Path, file_ext: str) -> str:
        """
        Extract text based on file type.
        
        Args:
            file_path: Path to the file
            file_ext: File extension
            
        Returns:
            Extracted text content
        """
        if file_ext in {'.txt', '.md'}:
            return self._extract_text_file(file_path)
        elif file_ext == '.pdf':
            return self._extract_pdf(file_path)
        else:
            raise ValueError(f"Unsupported extension: {file_ext}")
    
    def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from .txt or .md files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _extract_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF using pdfplumber.
        
        pdfplumber is more reliable than PyPDF2 for text extraction
        and handles complex layouts better.
        """
        text_parts = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        # Add page marker for citation purposes
                        text_parts.append(f"[Page {page_num}]\n{text}")
                    else:
                        # If no text found, add placeholder
                        text_parts.append(f"[Page {page_num}]\n[No text content]")
        except Exception as e:
            # Fallback to PyPDF2 if pdfplumber fails
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            return self._extract_pdf_pypdf2(file_path)
        
        return "\n\n".join(text_parts)
    
    def _extract_pdf_pypdf2(self, file_path: Path) -> str:
        """Fallback PDF extraction using PyPDF2."""
        text_parts = []
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_parts.append(f"[Page {page_num}]\n{text}")
        
        return "\n\n".join(text_parts)
    
    def delete_document(self, file_path: str) -> bool:
        """
        Delete document file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(file_path).unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_document_info(self, file_path: str) -> Optional[Dict]:
        """
        Get information about a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document information or None if file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        return {
            'filename': path.name,
            'file_size': path.stat().st_size,
            'file_type': path.suffix,
            'exists': True
        }
