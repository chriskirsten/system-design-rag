#!/usr/bin/env python3
"""
Content Chunking Script

Splits documents into optimal chunks for embeddings.
Target: 500-1000 tokens per chunk with overlap for context preservation.
"""

import json
import tiktoken
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from colorama import init, Fore, Style

# Initialize colorama
init()

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Ensure processed directory exists
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Chunking configuration
TARGET_CHUNK_SIZE = 750  # tokens (middle of 500-1000 range)
MAX_CHUNK_SIZE = 1000    # tokens
MIN_CHUNK_SIZE = 100     # tokens (minimum viable chunk)
OVERLAP_SIZE = 50        # tokens (for context preservation)

# Initialize tokenizer for OpenAI models
try:
    ENCODING = tiktoken.encoding_for_model("text-embedding-3-small")
except Exception:
    # Fallback to cl100k_base encoding (used by GPT-4 and text-embedding-3)
    ENCODING = tiktoken.get_encoding("cl100k_base")


@dataclass
class Chunk:
    """Represents a text chunk"""
    chunk_id: str
    content: str
    token_count: int
    chunk_index: int
    metadata: Dict


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken
    
    Args:
        text: Text to count tokens in
    
    Returns:
        int: Number of tokens
    """
    return len(ENCODING.encode(text))


def split_text_by_tokens(text: str, max_tokens: int, overlap: int = 0) -> List[str]:
    """
    Split text into chunks by token count
    
    Args:
        text: Text to split
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
    
    Returns:
        List[str]: List of text chunks
    """
    # Encode the entire text
    tokens = ENCODING.encode(text)
    chunks = []
    
    start = 0
    while start < len(tokens):
        # Get chunk of tokens
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        
        # Decode back to text
        chunk_text = ENCODING.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Move start position (accounting for overlap)
        start = end - overlap
        
        # Break if we've consumed all tokens
        if end >= len(tokens):
            break
    
    return chunks


def chunk_by_paragraphs(text: str, target_size: int) -> List[str]:
    """
    Split text by paragraphs, combining them to reach target size
    
    Args:
        text: Text to split
        target_size: Target token count per chunk
    
    Returns:
        List[str]: List of text chunks
    """
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for paragraph in paragraphs:
        para_tokens = count_tokens(paragraph)
        
        # If single paragraph is too large, split it
        if para_tokens > MAX_CHUNK_SIZE:
            # Save current chunk if it has content
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Split the large paragraph by sentences
            sentences = [s.strip() + '.' for s in paragraph.split('.') if s.strip()]
            temp_chunk = []
            temp_tokens = 0
            
            for sentence in sentences:
                sent_tokens = count_tokens(sentence)
                if temp_tokens + sent_tokens > MAX_CHUNK_SIZE:
                    if temp_chunk:
                        chunks.append(' '.join(temp_chunk))
                    temp_chunk = [sentence]
                    temp_tokens = sent_tokens
                else:
                    temp_chunk.append(sentence)
                    temp_tokens += sent_tokens
            
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
            
            continue
        
        # Check if adding this paragraph exceeds target
        if current_tokens + para_tokens > target_size and current_chunk:
            # Save current chunk and start new one
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_tokens = para_tokens
        else:
            current_chunk.append(paragraph)
            current_tokens += para_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks


def chunk_document(doc_data: Dict) -> List[Chunk]:
    """
    Chunk a document into optimal sizes
    
    Args:
        doc_data: Document data dictionary
    
    Returns:
        List[Chunk]: List of chunks
    """
    content = doc_data["content"]
    doc_id = doc_data["id"]
    
    # First try paragraph-based chunking
    text_chunks = chunk_by_paragraphs(content, TARGET_CHUNK_SIZE)
    
    # If chunks are still too large, split by tokens
    final_chunks = []
    for chunk_text in text_chunks:
        token_count = count_tokens(chunk_text)
        if token_count > MAX_CHUNK_SIZE:
            # Split further by tokens
            sub_chunks = split_text_by_tokens(chunk_text, TARGET_CHUNK_SIZE, OVERLAP_SIZE)
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk_text)
    
    # Create Chunk objects
    chunks = []
    for idx, chunk_text in enumerate(final_chunks):
        chunk = Chunk(
            chunk_id=f"{doc_id}_chunk_{idx}",
            content=chunk_text,
            token_count=count_tokens(chunk_text),
            chunk_index=idx,
            metadata={
                "document_id": doc_id,
                "title": doc_data["title"],
                "category": doc_data["category"],
                "source": doc_data.get("source", ""),
                "url": doc_data.get("url", ""),
                "tags": doc_data["tags"],
                "difficulty": doc_data.get("difficulty", ""),
                "chunk_index": idx,
                "total_chunks": len(final_chunks)
            }
        )
        chunks.append(chunk)
    
    return chunks


def process_all_documents() -> tuple[int, int, int]:
    """
    Process all documents in raw data directory
    
    Returns:
        tuple: (total_docs, total_chunks, total_tokens)
    """
    print(f"{Fore.CYAN}🔪 Starting content chunking...{Style.RESET_ALL}\n")
    
    if not RAW_DATA_DIR.exists():
        print(f"{Fore.RED}❌ Error: Raw data directory not found{Style.RESET_ALL}")
        exit(1)
    
    files = [f for f in RAW_DATA_DIR.glob("*.json") if f.name != "index.json"]
    
    if not files:
        print(f"{Fore.RED}❌ Error: No JSON files found{Style.RESET_ALL}")
        exit(1)
    
    print(f"{Fore.BLUE}📁 Found {len(files)} documents to process{Style.RESET_ALL}\n")
    
    total_chunks = 0
    total_tokens = 0
    all_chunks_data = []
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            # Chunk the document
            chunks = chunk_document(doc_data)
            
            # Convert chunks to dictionaries for JSON serialization
            chunks_dict = [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "token_count": chunk.token_count,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
            
            all_chunks_data.extend(chunks_dict)
            
            chunk_tokens = sum(c.token_count for c in chunks)
            total_chunks += len(chunks)
            total_tokens += chunk_tokens
            
            print(f"{Fore.GREEN}✅ {filepath.name}{Style.RESET_ALL}")
            print(f"   Chunks: {len(chunks)}, Tokens: {chunk_tokens:,}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error processing {filepath.name}: {e}{Style.RESET_ALL}")
    
    # Save all chunks to processed directory
    output_file = PROCESSED_DATA_DIR / "chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Fore.CYAN}📊 Summary:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Documents processed: {len(files)}{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Total chunks: {total_chunks}{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Total tokens: {total_tokens:,}{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Average tokens/chunk: {total_tokens // total_chunks if total_chunks > 0 else 0}{Style.RESET_ALL}")
    print(f"   {Fore.BLUE}📁 Output: {output_file}{Style.RESET_ALL}\n")
    
    # Create index file
    index = {
        "total_documents": len(files),
        "total_chunks": total_chunks,
        "total_tokens": total_tokens,
        "avg_tokens_per_chunk": total_tokens // total_chunks if total_chunks > 0 else 0,
        "processed_at": Path(output_file).stat().st_mtime
    }
    
    index_path = PROCESSED_DATA_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    return len(files), total_chunks, total_tokens


def main():
    """Main execution"""
    try:
        docs, chunks, tokens = process_all_documents()
        print(f"{Fore.GREEN}✨ Chunking complete!{Style.RESET_ALL}\n")
        return 0
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    exit(main())