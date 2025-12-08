"""
Document Processor for Kenyan Government Documents
Extracts text from PDFs, cleans, and splits into chunks
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a chunk of document text with metadata"""
    
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_id: str = None
    ):
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id or self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for chunk"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        source = self.metadata.get('source', 'unknown')
        page = self.metadata.get('page', 0)
        return f"{source}_{page}_{timestamp}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'metadata': self.metadata
        }


class DocumentProcessor:
    """Process government documents into searchable chunks"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        logger.info(f"DocumentProcessor initialized (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF file, page by page
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dicts with page text and metadata
        """
        logger.info(f"Extracting text from: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        pages_data = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Processing {total_pages} pages from {os.path.basename(pdf_path)}")
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    try:
                        text = page.extract_text()
                        
                        if text.strip():
                            pages_data.append({
                                'page_number': page_num,
                                'text': text,
                                'source': os.path.basename(pdf_path),
                                'total_pages': total_pages
                            })
                            logger.debug(f"Extracted {len(text)} chars from page {page_num}")
                        else:
                            logger.warning(f"Page {page_num} is empty or couldn't be extracted")
                    
                    except Exception as e:
                        logger.error(f"Error extracting page {page_num}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise
        
        logger.info(f"Successfully extracted {len(pages_data)} pages from {os.path.basename(pdf_path)}")
        return pages_data
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove page numbers (common patterns)
        text = re.sub(r'Page \d+( of \d+)?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove headers/footers (common patterns)
        text = re.sub(r'Kenya Gazette.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Constitution of Kenya.*?\n', '', text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = text.strip()
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            metadata: Metadata for the chunks
            
        Returns:
            List of DocumentChunk objects
        """
        # Clean the text first
        text = self.clean_text(text)
        
        if not text:
            logger.warning(f"Empty text after cleaning for {metadata.get('source', 'unknown')}")
            return []
        
        # Split into sentences
        sentences = self.split_into_sentences(text)
        
        if not sentences:
            logger.warning(f"No sentences found in {metadata.get('source', 'unknown')}")
            return []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size, save current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                
                if len(chunk_text) >= self.min_chunk_size:
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = len(chunks)
                    chunk_metadata['char_count'] = len(chunk_text)
                    
                    chunks.append(DocumentChunk(
                        content=chunk_text,
                        metadata=chunk_metadata
                    ))
                
                # Keep last few sentences for overlap
                overlap_text = ' '.join(current_chunk)
                overlap_length = 0
                overlap_sentences = []
                
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = len(chunks)
                chunk_metadata['char_count'] = len(chunk_text)
                
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    metadata=chunk_metadata
                ))
        
        logger.info(f"Created {len(chunks)} chunks from {metadata.get('source', 'unknown')} page {metadata.get('page_number', '?')}")
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[DocumentChunk]:
        """
        Process entire PDF into chunks
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of DocumentChunk objects
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract text from all pages
        pages_data = self.extract_text_from_pdf(pdf_path)
        
        if not pages_data:
            logger.warning(f"No text extracted from {pdf_path}")
            return []
        
        # Process each page into chunks
        all_chunks = []
        
        for page_data in pages_data:
            metadata = {
                'source': page_data['source'],
                'page_number': page_data['page_number'],
                'total_pages': page_data['total_pages'],
                'document_type': self._detect_document_type(page_data['source']),
                'domain': self._detect_domain(page_data['source']),
                'language': self._detect_language(page_data['source'], page_data['text']),
                'processed_at': datetime.now().isoformat()
            }
            
            page_chunks = self.create_chunks(page_data['text'], metadata)
            all_chunks.extend(page_chunks)
        
        logger.info(f"Total chunks created from {os.path.basename(pdf_path)}: {len(all_chunks)}")
        return all_chunks
    
    def _detect_document_type(self, filename: str) -> str:
        """
        Detect document type from filename
        
        Args:
            filename: Name of the file
            
        Returns:
            Document type category
        """
        filename_lower = filename.lower()
        
        if 'constitution' in filename_lower:
            return 'constitution'
        elif 'business' in filename_lower or 'company' in filename_lower or 'registration' in filename_lower:
            return 'business'
        elif 'land' in filename_lower or 'property' in filename_lower:
            return 'land'
        elif 'tax' in filename_lower or 'kra' in filename_lower:
            return 'tax'
        elif 'health' in filename_lower:
            return 'health'
        elif 'employment' in filename_lower or 'labour' in filename_lower:
            return 'employment'
        elif 'county' in filename_lower:
            return 'county_government'
        elif 'citizen' in filename_lower or 'immigration' in filename_lower:
            return 'citizenship'
        else:
            return 'general'

    def _detect_domain(self, filename: str) -> str:
        """
        Decide whether a document belongs to the civic or health domain.
        """
        filename_lower = filename.lower()
        health_markers = ("health", "clinic", "hospital", "afya", "medical", "pharma")
        if any(marker in filename_lower for marker in health_markers):
            return "health"
        return "civic"
    
    def _detect_language(self, filename: str, text: str = "") -> str:
        """
        Detect the source language of a document from filename and content.
        Returns: 'english', 'swahili', or defaults to configured SOURCE_LANGUAGE
        """
        filename_lower = filename.lower()
        text_lower = text.lower()[:500] if text else ""  # Sample first 500 chars
        
        # Check filename for language indicators
        swahili_filename_markers = ("swahili", "kiswahili", "sw", "swa")
        if any(marker in filename_lower for marker in swahili_filename_markers):
            return "swahili"
        
        # Check content for common Swahili words
        swahili_words = ["na", "ya", "wa", "kwa", "ni", "katika", "hii", "hili", "haya", 
                        "serikali", "watu", "huduma", "afya", "kutoka", "kwa", "kuhusu"]
        swahili_word_count = sum(1 for word in swahili_words if word in text_lower)
        
        # If we find multiple Swahili words, likely Swahili document
        if swahili_word_count >= 3:
            return "swahili"
        
        # Default to configured source language (usually English)
        from app.config import settings
        return settings.SOURCE_LANGUAGE
    
    def process_directory(self, directory_path: str) -> List[DocumentChunk]:
        """
        Process all PDFs in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            List of all DocumentChunk objects
        """
        logger.info(f"Processing directory: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_chunks = []
        
        for pdf_path in pdf_files:
            try:
                chunks = self.process_pdf(str(pdf_path))
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        logger.info(f"Total chunks from all documents: {len(all_chunks)}")
        return all_chunks


# Utility functions for testing
def test_processor():
    """Test the document processor"""
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    
    # Test with sample text
    sample_text = """
    The Constitution of Kenya 2010. Article 43: Economic and social rights.
    Every person has the right to the highest attainable standard of health.
    Every person has the right to accessible and adequate housing.
    Every person has the right to reasonable standards of sanitation.
    Every person has the right to be free from hunger.
    Every person has the right to clean and safe water in adequate quantities.
    Every person has the right to social security.
    Every person has the right to education.
    """
    
    metadata = {
        'source': 'test_constitution.pdf',
        'page_number': 1,
        'total_pages': 100
    }
    
    chunks = processor.create_chunks(sample_text, metadata)
    
    print(f"\nTest Results:")
    print(f"Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Content: {chunk.content[:100]}...")
        print(f"Metadata: {chunk.metadata}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_processor()