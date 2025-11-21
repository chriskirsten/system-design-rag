
#!/usr/bin/env python3
"""
Pinecone Upload Script

Uploads embeddings to Pinecone vector database.
Creates index if needed and uploads vectors with metadata.
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Tuple
from pinecone import Pinecone, ServerlessSpec
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
EMBEDDINGS_DATA_DIR = DATA_DIR / "embeddings"

# Configuration
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "system-design-rag")
DIMENSION = 1536  # text-embedding-3-small dimension
METRIC = "cosine"  # cosine similarity
BATCH_SIZE = 100  # Vectors per batch

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    print(f"{Fore.RED}❌ Error: PINECONE_API_KEY not found in environment{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Please set PINECONE_API_KEY in your .env file{Style.RESET_ALL}")
    exit(1)

pc = Pinecone(api_key=api_key)


def create_index_if_needed() -> bool:
    """
    Create Pinecone index if it doesn't exist
    
    Returns:
        bool: True if index was created, False if it already existed
    """
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if INDEX_NAME in existing_indexes:
        print(f"{Fore.BLUE}📊 Index '{INDEX_NAME}' already exists{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.CYAN}🔨 Creating index '{INDEX_NAME}'...{Style.RESET_ALL}")
    
    # Create serverless index (free tier)
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    
    # Wait for index to be ready
    print(f"{Fore.YELLOW}⏳ Waiting for index to be ready...{Style.RESET_ALL}")
    while not pc.describe_index(INDEX_NAME).status['ready']:
        time.sleep(1)
    
    print(f"{Fore.GREEN}✅ Index created successfully{Style.RESET_ALL}\n")
    return True


def prepare_vectors(embeddings_data: List[Dict]) -> List[Tuple]:
    """
    Prepare vectors for upload to Pinecone
    
    Args:
        embeddings_data: List of embedding dictionaries
    
    Returns:
        List[Tuple]: List of (id, vector, metadata) tuples
    """
    vectors = []
    
    for item in embeddings_data:
        vector_id = item["chunk_id"]
        vector = item["embedding"]
        
        # Prepare metadata (Pinecone has limits on metadata size)
        metadata = {
            "content": item["content"][:1000],  # Limit content length
            "title": item["metadata"]["title"],
            "category": item["metadata"]["category"],
            "document_id": item["metadata"]["document_id"],
            "chunk_index": item["metadata"]["chunk_index"],
            "total_chunks": item["metadata"]["total_chunks"],
            "token_count": item["token_count"],
            "source": item["metadata"].get("source", ""),
            "difficulty": item["metadata"].get("difficulty", ""),
            "tags": ",".join(item["metadata"].get("tags", []))[:500]  # Join tags, limit length
        }
        
        vectors.append((vector_id, vector, metadata))
    
    return vectors


def upload_vectors(vectors: List[Tuple]) -> int:
    """
    Upload vectors to Pinecone in batches
    
    Args:
        vectors: List of (id, vector, metadata) tuples
    
    Returns:
        int: Number of vectors uploaded
    """
    print(f"{Fore.CYAN}📤 Uploading vectors to Pinecone...{Style.RESET_ALL}\n")
    
    # Get index
    index = pc.Index(INDEX_NAME)
    
    # Upload in batches
    total_uploaded = 0
    
    with tqdm(total=len(vectors), desc="Uploading vectors", unit="vector") as pbar:
        for i in range(0, len(vectors), BATCH_SIZE):
            batch = vectors[i:i + BATCH_SIZE]
            
            try:
                # Upsert batch
                index.upsert(vectors=batch)
                total_uploaded += len(batch)
                pbar.update(len(batch))
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"\n{Fore.RED}❌ Error uploading batch {i // BATCH_SIZE + 1}: {e}{Style.RESET_ALL}")
                raise
    
    return total_uploaded


def verify_upload() -> Dict:
    """
    Verify vectors were uploaded correctly
    
    Returns:
        Dict: Index statistics
    """
    print(f"\n{Fore.CYAN}🔍 Verifying upload...{Style.RESET_ALL}\n")
    
    index = pc.Index(INDEX_NAME)
    
    # Wait for index to update
    time.sleep(2)
    
    # Get index stats
    stats = index.describe_index_stats()
    
    return stats


def test_search():
    """Test a simple search query"""
    print(f"{Fore.CYAN}🧪 Testing search functionality...{Style.RESET_ALL}\n")
    
    index = pc.Index(INDEX_NAME)
    
    # Load one embedding to use as test query
    embeddings_file = EMBEDDINGS_DATA_DIR / "embeddings.json"
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        embeddings = json.load(f)
    
    if not embeddings:
        print(f"{Fore.YELLOW}⚠️  No embeddings to test with{Style.RESET_ALL}")
        return
    
    # Use first embedding as test query
    test_vector = embeddings[0]["embedding"]
    
    # Query index
    results = index.query(
        vector=test_vector,
        top_k=3,
        include_metadata=True
    )
    
    print(f"{Fore.GREEN}✅ Search test successful{Style.RESET_ALL}")
    print(f"   Found {len(results['matches'])} matches")
    
    if results['matches']:
        print(f"\n{Fore.BLUE}Top match:{Style.RESET_ALL}")
        top_match = results['matches'][0]
        print(f"   ID: {top_match['id']}")
        print(f"   Score: {top_match['score']:.4f}")
        print(f"   Title: {top_match['metadata'].get('title', 'N/A')}")


def main():
    """Main execution"""
    try:
        # Load embeddings
        embeddings_file = EMBEDDINGS_DATA_DIR / "embeddings.json"
        if not embeddings_file.exists():
            print(f"{Fore.RED}❌ Error: embeddings.json not found{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please run generate_embeddings.py first{Style.RESET_ALL}")
            return 1
        
        print(f"{Fore.CYAN}📂 Loading embeddings...{Style.RESET_ALL}\n")
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            embeddings_data = json.load(f)
        
        print(f"{Fore.BLUE}Loaded {len(embeddings_data)} embeddings{Style.RESET_ALL}\n")
        
        # Create index if needed
        create_index_if_needed()
        
        # Prepare vectors
        print(f"{Fore.CYAN}🔧 Preparing vectors...{Style.RESET_ALL}\n")
        vectors = prepare_vectors(embeddings_data)
        print(f"{Fore.GREEN}✅ Prepared {len(vectors)} vectors{Style.RESET_ALL}\n")
        
        # Upload vectors
        uploaded = upload_vectors(vectors)
        
        # Verify upload
        stats = verify_upload()
        
        print(f"{Fore.CYAN}📊 Index Statistics:{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}Total vectors: {stats.get('total_vector_count', 0)}{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}Dimension: {stats.get('dimension', 0)}{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}Index fullness: {stats.get('index_fullness', 0):.2%}{Style.RESET_ALL}\n")
        
        # Test search
        test_search()
        
        print(f"\n{Fore.GREEN}✨ Upload complete!{Style.RESET_ALL}\n")
        print(f"{Fore.BLUE}Index name: {INDEX_NAME}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Vectors uploaded: {uploaded}{Style.RESET_ALL}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())