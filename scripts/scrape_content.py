#!/usr/bin/env python3
"""
System Design Content Scraper

This script collects system design content from various sources.
For Phase 1, we'll start with manual content curation from public sources.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Sample system design content
SAMPLE_CONTENT = [
    {
        "id": "load-balancing-basics",
        "title": "Load Balancing Fundamentals",
        "category": "scalability",
        "content": """Load balancing is the process of distributing network traffic across multiple servers to ensure no single server bears too much demand. By spreading the work evenly, load balancing improves application responsiveness and increases availability of applications and websites for users.

Key concepts:
- Load balancers act as a reverse proxy and distribute network or application traffic across multiple servers
- They improve application availability and responsiveness
- They prevent any one server from becoming a single point of failure

Common load balancing algorithms:
1. Round Robin: Distributes requests sequentially across servers
2. Least Connections: Sends requests to server with fewest active connections
3. IP Hash: Routes client to server based on client IP address
4. Weighted Round Robin: Assigns weight to each server based on capacity

Types of Load Balancers:
- Layer 4 (Transport Layer): Makes routing decisions based on IP and TCP/UDP port
- Layer 7 (Application Layer): Makes routing decisions based on content of the request

Health checks are crucial - load balancers regularly check server health to avoid routing to failed servers.""",
        "source": "System Design Documentation",
        "url": "https://example.com/load-balancing",
        "tags": ["load-balancing", "scalability", "infrastructure"],
        "difficulty": "beginner",
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": "caching-strategies",
        "title": "Caching Strategies and Patterns",
        "category": "performance",
        "content": """Caching is a technique to store frequently accessed data in a fast storage layer to reduce latency and database load. Effective caching strategies are essential for building high-performance systems.

Cache Patterns:

1. Cache-Aside (Lazy Loading):
   - Application checks cache first
   - If miss, load from database and populate cache
   - Good for read-heavy workloads
   - Pros: Only requested data is cached
   - Cons: Cache misses result in three trips

2. Write-Through:
   - Write to cache and database simultaneously
   - Ensures cache is always consistent
   - Pros: Data never stale, reads are fast
   - Cons: Higher write latency

3. Write-Behind (Write-Back):
   - Write to cache immediately, database later
   - Batches writes for better performance
   - Pros: Very fast writes
   - Cons: Risk of data loss if cache fails

4. Read-Through:
   - Cache sits between application and database
   - Cache loads data on miss automatically
   - Pros: Simplified application logic
   - Cons: First request always slow

Cache Eviction Policies:
- LRU (Least Recently Used): Removes least recently accessed items
- LFU (Least Frequently Used): Removes least frequently accessed items
- FIFO (First In First Out): Removes oldest items first
- TTL (Time To Live): Items expire after set time

Popular caching technologies:
- Redis: In-memory data structure store
- Memcached: High-performance distributed memory cache
- CDN: Content Delivery Network for static assets
- Browser Cache: Client-side caching""",
        "source": "System Design Best Practices",
        "url": "https://example.com/caching",
        "tags": ["caching", "performance", "redis", "memcached"],
        "difficulty": "intermediate",
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": "database-scaling",
        "title": "Database Scaling Strategies",
        "category": "databases",
        "content": """Scaling databases is one of the most critical challenges in system design. As your application grows, you need strategies to handle increased data volume and query load.

Vertical Scaling (Scale Up):
- Add more resources (CPU, RAM, Storage) to existing server
- Pros: Simple, no application changes needed
- Cons: Hardware limits, expensive, single point of failure
- Good for: Initial growth, when horizontal scaling is complex

Horizontal Scaling (Scale Out):
- Add more servers to distribute load
- Requires data distribution strategy
- More complex but more scalable

Replication:
- Master-Slave (Primary-Replica):
  - One primary handles writes
  - Multiple replicas handle reads
  - Improves read performance
  - Provides fault tolerance
  
- Master-Master (Multi-Primary):
  - Multiple nodes handle writes
  - More complex conflict resolution
  - Higher availability

Partitioning/Sharding:
- Split data across multiple databases
- Horizontal partitioning (sharding): Split rows across nodes
- Vertical partitioning: Split columns into separate tables

Sharding Strategies:
1. Range-based: Shard by range of values (e.g., user ID 1-1000, 1001-2000)
2. Hash-based: Use hash function on key to determine shard
3. Geographic: Shard by location for data locality
4. Directory-based: Lookup table maps keys to shards

Challenges with Sharding:
- Cross-shard queries become complex
- Transactions across shards are difficult
- Rebalancing data when adding/removing shards
- Hotspots if sharding key is not well-distributed

Database Types:
- SQL (Relational): ACID compliance, structured data
- NoSQL: 
  - Document (MongoDB): Flexible schema
  - Key-Value (Redis): Simple, fast
  - Column-Family (Cassandra): Write-heavy workloads
  - Graph (Neo4j): Relationship-focused data""",
        "source": "Database Scaling Guide",
        "url": "https://example.com/database-scaling",
        "tags": ["databases", "scaling", "sharding", "replication"],
        "difficulty": "advanced",
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": "api-design-rest",
        "title": "RESTful API Design Best Practices",
        "category": "api-design",
        "content": """REST (Representational State Transfer) is an architectural style for designing networked applications. Good API design is crucial for maintainability and developer experience.

REST Principles:
1. Client-Server: Separation of concerns
2. Stateless: Each request contains all necessary information
3. Cacheable: Responses explicitly indicate if they can be cached
4. Uniform Interface: Consistent interaction patterns
5. Layered System: Client doesn't know if connected to end server

HTTP Methods:
- GET: Retrieve resource (idempotent, safe)
- POST: Create new resource
- PUT: Update/replace entire resource (idempotent)
- PATCH: Partial update of resource
- DELETE: Remove resource (idempotent)

URL Design Best Practices:
- Use nouns, not verbs: /users not /getUsers
- Use plural names: /users/123 not /user/123
- Hierarchical relationships: /users/123/posts
- Filter with query parameters: /users?active=true&role=admin
- Versioning: /v1/users or /api/v1/users

Status Codes:
- 2xx Success:
  - 200 OK: Standard success
  - 201 Created: Resource created
  - 204 No Content: Success with no body
- 3xx Redirection:
  - 301 Moved Permanently
  - 302 Found (temporary redirect)
- 4xx Client Errors:
  - 400 Bad Request: Invalid data
  - 401 Unauthorized: Authentication required
  - 403 Forbidden: Authenticated but not authorized
  - 404 Not Found: Resource doesn't exist
  - 429 Too Many Requests: Rate limit exceeded
- 5xx Server Errors:
  - 500 Internal Server Error
  - 503 Service Unavailable

Response Format:
- Consistent JSON structure
- Include metadata (pagination, timestamps)
- Error responses with helpful messages
- HATEOAS: Include links to related resources

Example Response:
{
  "data": {...},
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  },
  "links": {
    "self": "/users?page=1",
    "next": "/users?page=2"
  }
}

Security:
- Always use HTTPS
- Implement authentication (JWT, OAuth)
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS configuration""",
        "source": "API Design Guidelines",
        "url": "https://example.com/api-design",
        "tags": ["api-design", "rest", "http", "web-services"],
        "difficulty": "intermediate",
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": "microservices-architecture",
        "title": "Microservices Architecture Patterns",
        "category": "architecture",
        "content": """Microservices architecture structures an application as a collection of loosely coupled, independently deployable services. Each service is responsible for a specific business capability.

Key Characteristics:
- Single Responsibility: Each service does one thing well
- Independently Deployable: Deploy without affecting other services
- Decentralized Data: Each service manages its own database
- Technology Diversity: Different services can use different tech stacks
- Communication via APIs: Services communicate over network

Benefits:
- Scalability: Scale individual services independently
- Flexibility: Use different technologies for different services
- Resilience: Failure in one service doesn't crash entire system
- Faster Development: Teams can work independently
- Easier Testing: Test services in isolation

Challenges:
- Distributed System Complexity: Network latency, partial failures
- Data Consistency: No ACID transactions across services
- Testing: Integration testing is more complex
- Deployment: More moving parts to manage
- Monitoring: Need distributed tracing and logging

Communication Patterns:

1. Synchronous (HTTP/REST):
   - Direct request-response
   - Simple but creates coupling
   - Use for: Low latency requirements

2. Asynchronous (Message Queue):
   - Services communicate via events
   - Loose coupling, better resilience
   - Use for: Background processing, event-driven workflows

API Gateway Pattern:
- Single entry point for clients
- Handles authentication, routing, rate limiting
- Aggregates multiple service calls
- Examples: Kong, AWS API Gateway, NGINX

Service Discovery:
- Services register themselves
- Clients query to find service locations
- Tools: Consul, Eureka, etcd

Circuit Breaker Pattern:
- Prevents cascading failures
- Stops calling failing service
- Returns default response or error
- Tools: Hystrix, Resilience4j

Data Management:
- Database per Service: Each service owns its data
- Saga Pattern: Manage distributed transactions
- Event Sourcing: Store all changes as events
- CQRS: Separate read and write models

Deployment:
- Containers (Docker) for consistency
- Orchestration (Kubernetes) for management
- CI/CD pipelines for automation
- Blue-Green or Canary deployments""",
        "source": "Microservices Patterns",
        "url": "https://example.com/microservices",
        "tags": ["microservices", "architecture", "distributed-systems"],
        "difficulty": "advanced",
        "timestamp": datetime.now().isoformat()
    }
]


def save_content() -> tuple[int, int]:
    """
    Save content to files
    
    Returns:
        tuple: (success_count, error_count)
    """
    print(f"{Fore.CYAN}📝 Starting content collection...{Style.RESET_ALL}\n")
    
    success_count = 0
    error_count = 0

    for item in SAMPLE_CONTENT:
        try:
            filename = f"{item['id']}.json"
            filepath = RAW_DATA_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=2, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✅ Saved: {filename}{Style.RESET_ALL}")
            success_count += 1
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving {item['id']}: {e}{Style.RESET_ALL}")
            error_count += 1

    print(f"\n{Fore.CYAN}📊 Summary:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}✅ Successfully saved: {success_count} files{Style.RESET_ALL}")
    print(f"   {Fore.RED}❌ Errors: {error_count} files{Style.RESET_ALL}")
    print(f"   {Fore.BLUE}📁 Location: {RAW_DATA_DIR}{Style.RESET_ALL}\n")

    # Create index file
    index = {
        "total": len(SAMPLE_CONTENT),
        "categories": list(set(c["category"] for c in SAMPLE_CONTENT)),
        "files": [c["id"] for c in SAMPLE_CONTENT],
        "lastUpdated": datetime.now().isoformat()
    }

    index_path = RAW_DATA_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"{Fore.GREEN}✅ Created index file{Style.RESET_ALL}\n")
    
    return success_count, error_count


def main():
    """Main execution"""
    print(f"{Fore.CYAN}🚀 System Design Content Scraper{Style.RESET_ALL}\n")
    success, errors = save_content()
    print(f"{Fore.CYAN}✨ Content collection complete!{Style.RESET_ALL}\n")
    
    # Exit with error code if there were errors
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    exit(main())