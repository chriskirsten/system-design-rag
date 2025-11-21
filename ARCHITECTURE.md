# System Design RAG - Architecture Documentation

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                      (React + Tailwind CSS)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS Request
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Netlify Edge Layer                          │
│                   (CDN + Static Hosting)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Invoke Function
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Netlify Serverless Functions                  │
│                         (API Layer)                              │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Query     │  │    Health    │  │   Future     │         │
│  │   Handler    │  │    Check     │  │  Functions   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────┬─────────────────────────────────────────────────────────┘
        │
        │ 1. Generate Query Embedding
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OpenAI API                               │
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   Embeddings     │              │      GPT-4       │        │
│  │ (text-embedding  │              │  (Response Gen)  │        │
│  │   -3-small)      │              │                  │        │
│  └──────────────────┘              └──────────────────┘        │
└───────┬───────────────────────────────────────┬─────────────────┘
        │                                       │
        │ 2. Search Vectors                     │ 4. Generate Response
        ▼                                       │
┌─────────────────────────────────────────────┐ │
│            Pinecone Vector DB                │ │
│                                              │ │
│  ┌────────────────────────────────────┐    │ │
│  │  Index: system-design-rag          │    │ │
│  │  Dimensions: 1536                   │    │ │
│  │  Metric: Cosine Similarity          │    │ │
│  │                                      │    │ │
│  │  Vectors + Metadata:                │    │ │
│  │  - Document chunks                  │    │ │
│  │  - Source information               │    │ │
│  │  - Categories/Tags                  │    │ │
│  └────────────────────────────────────┘    │ │
└──────────────────┬──────────────────────────┘ │
                   │                            │
                   │ 3. Return Top-k Results    │
                   └────────────────────────────┘
```

## Data Flow - Query Processing

```
Step 1: User Query
┌──────────────┐
│ User submits │
│   "What is   │
│    load      │
│  balancing?" │
└──────┬───────┘
       │
       ▼
Step 2: Frontend Processing
┌──────────────────┐
│ React Component  │
│ - Validate input │
│ - Show loading   │
└──────┬───────────┘
       │
       ▼
Step 3: API Request
┌────────────────────┐
│ POST /api/query    │
│ {                  │
│   query: "...",    │
│   k: 5             │
│ }                  │
└──────┬─────────────┘
       │
       ▼
Step 4: Generate Query Embedding
┌─────────────────────────┐
│ OpenAI Embeddings API   │
│ Input: User query       │
│ Output: 1536-dim vector │
└──────┬──────────────────┘
       │
       ▼
Step 5: Vector Search
┌───────────────────────────┐
│ Pinecone Query            │
│ - Search similar vectors  │
│ - Filter by metadata      │
│ - Return top 5 matches    │
└──────┬────────────────────┘
       │
       ▼
Step 6: Context Preparation
┌─────────────────────────────┐
│ Combine retrieved documents │
│ - Extract content           │
│ - Format with metadata      │
│ - Build prompt context      │
└──────┬──────────────────────┘
       │
       ▼
Step 7: LLM Generation
┌────────────────────────────┐
│ OpenAI GPT-4 API           │
│ Prompt:                    │
│ "Given context: [docs]     │
│  Answer: [query]"          │
└──────┬─────────────────────┘
       │
       ▼
Step 8: Response Assembly
┌─────────────────────────┐
│ Format Response         │
│ {                       │
│   answer: "...",        │
│   sources: [...],       │
│   confidence: 0.95      │
│ }                       │
└──────┬──────────────────┘
       │
       ▼
Step 9: Display to User
┌────────────────────────┐
│ React UI               │
│ - Show answer          │
│ - Display sources      │
│ - Allow follow-ups     │
└────────────────────────┘
```

## Data Processing Pipeline (Offline)

```
┌──────────────────┐
│  Raw Content     │
│  (Web scraping,  │
│   APIs, Manual)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  Content Cleaning    │
│  - Remove HTML       │
│  - Fix formatting    │
│  - Extract metadata  │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   Text Chunking      │
│   - 500-1000 tokens  │
│   - Overlap: 50      │
│   - Preserve context │
└────────┬─────────────┘
         │
         ▼
┌─────────────────────────┐
│  Generate Embeddings    │
│  (OpenAI API)           │
│  - Batch processing     │
│  - Rate limiting        │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Upload to Pinecone      │
│  - Vectors + metadata    │
│  - Batch upsert          │
│  - Verify upload         │
└──────────────────────────┘
```

## Component Architecture

### Frontend Components

```
src/
├── App.jsx                     (Root component)
│   │
│   ├── Header                  (Logo, title)
│   │
│   ├── QueryInterface          (Main search area)
│   │   ├── QueryInput         (Text input + submit)
│   │   └── ExampleQueries     (Suggested questions)
│   │
│   ├── ResponseDisplay        (Answer display)
│   │   ├── LoadingState       (While processing)
│   │   ├── AnswerText         (Formatted response)
│   │   ├── SourceCitations    (References)
│   │   └── RelatedQuestions   (Follow-ups)
│   │
│   └── Footer                  (Links, info)
│
└── services/
    └── api.js                  (API client)
```

### Backend Functions

```
netlify/functions/
│
├── query.js                    (Main query handler)
│   ├── validateInput()
│   ├── generateEmbedding()
│   ├── searchVectors()
│   ├── constructPrompt()
│   ├── generateResponse()
│   └── formatResponse()
│
└── health.js                   (Health check)
    └── checkServices()
```

## Database Schema

### Pinecone Vector Structure

```javascript
{
  id: "chunk_001",                    // Unique identifier
  values: [0.123, -0.456, ...],      // 1536-dimensional vector
  metadata: {
    content: "Full text of chunk",   // Original text
    title: "Load Balancing",         // Document title
    category: "scalability",         // Topic category
    source: "System Design Primer",  // Content source
    url: "https://...",              // Source URL
    tags: ["load-balancing", ...],   // Topic tags
    difficulty: "intermediate",      // Difficulty level
    chunk_index: 0,                  // Position in document
    total_chunks: 3,                 // Total chunks in doc
    timestamp: "2024-11-13T..."      // Created date
  }
}
```

## Technology Stack Details

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3+ | UI framework |
| Vite | 5.2+ | Build tool |
| Tailwind CSS | 3.4+ | Styling |
| Axios | 1.6+ | HTTP client |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 18+ | Runtime |
| Netlify Functions | 2.6+ | Serverless |
| OpenAI | 4.47+ | AI/ML |
| Pinecone | 2.2+ | Vector DB |

### Development
| Tool | Purpose |
|------|---------|
| ESLint | Code linting |
| Prettier | Code formatting |
| Git | Version control |
| npm | Package management |

## Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Layers                  │
├─────────────────────────────────────────┤
│                                          │
│  1. Transport Security                   │
│     ✓ HTTPS only                        │
│     ✓ TLS 1.3                           │
│                                          │
│  2. Authentication                       │
│     ✓ API key validation                │
│     ✓ Rate limiting                     │
│                                          │
│  3. Input Validation                     │
│     ✓ Query sanitization                │
│     ✓ Length limits                     │
│     ✓ XSS prevention                    │
│                                          │
│  4. API Security                         │
│     ✓ Environment variables             │
│     ✓ No key exposure                   │
│     ✓ Scoped permissions                │
│                                          │
│  5. Output Sanitization                  │
│     ✓ Response validation               │
│     ✓ Content filtering                 │
│                                          │
└─────────────────────────────────────────┘
```

## Scalability Considerations

### Current Scale (MVP)
- Users: 100-1000 concurrent
- Queries: ~1000/day
- Documents: ~100 topics
- Vectors: ~1000 chunks

### Growth Path
```
Phase 1 (Current)
├── Pinecone: Starter tier (100K vectors)
├── Netlify: Free tier
└── OpenAI: Pay-as-you-go

Phase 2 (Growth)
├── Pinecone: Standard tier (millions of vectors)
├── Netlify: Pro tier
├── Caching layer (Redis)
└── CDN optimization

Phase 3 (Scale)
├── Pinecone: Enterprise
├── Load balancing
├── Database sharding
└── Advanced caching
```

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Page Load | <2s | TBD |
| Query Response | <3s | TBD |
| Embedding Generation | <500ms | TBD |
| Vector Search | <200ms | TBD |
| LLM Generation | <2s | TBD |
| Uptime | 99.5% | TBD |

## Monitoring & Observability

```
┌─────────────────────────────────────┐
│         Monitoring Stack             │
├─────────────────────────────────────┤
│                                      │
│  Application Logs                    │
│  ├── Function invocations            │
│  ├── Error tracking                  │
│  └── Performance metrics             │
│                                      │
│  Netlify Analytics                   │
│  ├── Traffic patterns                │
│  ├── Function duration               │
│  └── Error rates                     │
│                                      │
│  OpenAI Dashboard                    │
│  ├── API usage                       │
│  ├── Token consumption               │
│  └── Cost tracking                   │
│                                      │
│  Pinecone Metrics                    │
│  ├── Query latency                   │
│  ├── Index size                      │
│  └── Request volume                  │
│                                      │
└─────────────────────────────────────┘
```

## Deployment Pipeline

```
Developer Machine
       │
       │ git push
       ▼
GitHub Repository
       │
       │ webhook
       ▼
Netlify Build System
       │
       ├─→ Install dependencies
       ├─→ Run build (Vite)
       ├─→ Run tests
       └─→ Bundle functions
       │
       ▼
Production Deployment
       │
       ├─→ Deploy to CDN
       ├─→ Deploy functions
       └─→ Update environment
       │
       ▼
   Live Site 🚀
```

## Future Architecture Enhancements

### Phase 2
- [ ] Conversation memory
- [ ] Query caching
- [ ] Hybrid search (vector + keyword)

### Phase 3
- [ ] Multi-tenancy
- [ ] Custom embeddings
- [ ] Real-time updates

### Phase 4
- [ ] A/B testing framework
- [ ] Advanced analytics
- [ ] ML model fine-tuning

---

**Architecture Version**: 1.0  
**Last Updated**: November 2024  
**Status**: Phase 1 Complete