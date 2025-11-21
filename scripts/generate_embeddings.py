#!/usr/bin/env python3
"""
Embedding Generation Script

Generates embeddings using OpenAI API for all chunked content.
Uses text-embedding-3-small model for cost-effectiveness.
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from colorama import init, Fore, Style
from tqdm import tqdm

# Initialize colorama
init()

# Load environment variables
load_dotenv()

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EMBEDDINGS_DATA_DIR = DATA_DIR / "embeddings"

# Ensure embeddings directory exists
EMBEDDINGS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # Number of texts to embed in one batch
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(f"{Fore.RED}❌ Error: OPENAI_API_KEY not found in environment{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Please set OPENAI_API_KEY in your .env file{Style.RESET_ALL}")
    exit(1)

client = OpenAI(api_key=api_key)


def generate_embeddings_batch(texts: List[str], retry_count: int = 0) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts
    
    Args:
        texts: List of text strings to embed
        retry_count: Current retry attempt
    
    Returns:
        List[List[float]]: List of embedding vectors
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        
        # Extract embeddings from response
        embeddings = [data.embedding for data in response.data]
        return embeddings
        
    except Exception as e:
        if retry_count < MAX_RETRIES:
            print(f"\n{Fore.YELLOW}⚠️  API error, retrying in {RETRY_DELAY}s... (attempt {retry_count + 1}/{MAX_RETRIES}){Style.RESET_ALL}")
            time.sleep(RETRY_DELAY)
            return generate_embeddings_batch(texts, retry_count + 1)
        else:
            print(f"\n{Fore.RED}❌ Failed after {MAX_RETRIES} retries: {e}{Style.RESET_ALL}")
            raise


def process_chunks() -> tuple[int, float]:
    """
    Process all chunks and generate embeddings
    
    Returns:
        tuple: (total_chunks_processed, total_cost_estimate)
    """
    print(f"{Fore.CYAN}🤖 Starting embedding generation...{Style.RESET_ALL}\n")
    
    # Load chunks
    chunks_file = PROCESSED_DATA_DIR / "chunks.json"
    if not chunks_file.exists():
        print(f"{Fore.RED}❌ Error: chunks.json not found{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please run chunk_content.py first{Style.RESET_ALL}")
        exit(1)
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"{Fore.BLUE}📁 Loaded {len(chunks)} chunks{Style.RESET_ALL}")
    print(f"{Fore.BLUE}📦 Batch size: {BATCH_SIZE}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}🤖 Model: {EMBEDDING_MODEL}{Style.RESET_ALL}\n")
    
    # Process in batches
    embeddings_data = []
    total_tokens = 0
    
    # Create progress bar
    with tqdm(total=len(chunks), desc="Generating embeddings", unit="chunk") as pbar:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            texts = [chunk["content"] for chunk in batch]
            
            try:
                # Generate embeddings for batch
                embeddings = generate_embeddings_batch(texts)
                
                # Combine chunks with their embeddings
                for chunk, embedding in zip(batch, embeddings):
                    embeddings_data.append({
                        "chunk_id": chunk["chunk_id"],
                        "embedding": embedding,
                        "content": chunk["content"],
                        "token_count": chunk["token_count"],
                        "metadata": chunk["metadata"]
                    })
                    total_tokens += chunk["token_count"]
                
                pbar.update(len(batch))
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"\n{Fore.RED}❌ Error processing batch {i // BATCH_SIZE + 1}: {e}{Style.RESET_ALL}")
                raise
    
    # Save embeddings
    output_file = EMBEDDINGS_DATA_DIR / "embeddings.json"
    print(f"\n{Fore.CYAN}💾 Saving embeddings...{Style.RESET_ALL}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, indent=2)
    
    # Calculate cost estimate
    # text-embedding-3-small: $0.020 per 1M tokens
    cost_estimate = (total_tokens / 1_000_000) * 0.020
    
    print(f"\n{Fore.CYAN}📊 Summary:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Chunks processed: {len(embeddings_data)}{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Total tokens: {total_tokens:,}{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Estimated cost: ${cost_estimate:.4f}{Style.RESET_ALL}")
    print(f"   {Fore.BLUE}📁 Output: {output_file}{Style.RESET_ALL}\n")
    
    # Create index file
    index = {
        "total_embeddings": len(embeddings_data),
        "total_tokens": total_tokens,
        "model": EMBEDDING_MODEL,
        "dimensions": len(embeddings_data[0]["embedding"]) if embeddings_data else 0,
        "estimated_cost_usd": cost_estimate,
        "created_at": time.time()
    }
    
    index_path = EMBEDDINGS_DATA_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    return len(embeddings_data), cost_estimate


def verify_embeddings():
    """Verify embeddings were generated correctly"""
    embeddings_file = EMBEDDINGS_DATA_DIR / "embeddings.json"
    
    if not embeddings_file.exists():
        print(f"{Fore.RED}❌ Embeddings file not found{Style.RESET_ALL}")
        return False
    
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        embeddings = json.load(f)
    
    if not embeddings:
        print(f"{Fore.RED}❌ No embeddings found{Style.RESET_ALL}")
        return False
    
    # Check first embedding
    first = embeddings[0]
    required_fields = ["chunk_id", "embedding", "content", "metadata"]
    
    for field in required_fields:
        if field not in first:
            print(f"{Fore.RED}❌ Missing field: {field}{Style.RESET_ALL}")
            return False
    
    # Check embedding dimensions
    embedding_dim = len(first["embedding"])
    expected_dim = 1536  # text-embedding-3-small produces 1536-dimensional vectors
    
    if embedding_dim != expected_dim:
        print(f"{Fore.YELLOW}⚠️  Warning: Unexpected embedding dimension: {embedding_dim} (expected {expected_dim}){Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}✅ Embeddings verification passed{Style.RESET_ALL}")
    print(f"   Embeddings: {len(embeddings)}")
    print(f"   Dimensions: {embedding_dim}")
    
    return True


def main():
    """Main execution"""
    try:
        chunks_processed, cost = process_chunks()
        
        print(f"{Fore.CYAN}🔍 Verifying embeddings...{Style.RESET_ALL}\n")
        if verify_embeddings():
            print(f"\n{Fore.GREEN}✨ Embedding generation complete!{Style.RESET_ALL}\n")
            return 0
        else:
            print(f"\n{Fore.RED}❌ Embedding verification failed{Style.RESET_ALL}\n")
            return 1
            
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
        return 1


if __name__ == "__main__":
    exit(main())