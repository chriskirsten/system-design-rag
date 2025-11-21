# Phase 1 Setup Guide - System Design RAG

## Overview
Phase 1 focuses on establishing the development environment and building the data collection pipeline.

## Prerequisites

### Required Software
- **Python 3.9+** (for data pipeline scripts)
- **Node.js (v18 or higher)** (for frontend and Netlify Functions)
- npm or yarn
- Git
- Code editor (VS Code recommended)

### Required API Keys
1. **OpenAI API Key**
   - Sign up at https://platform.openai.com
   - Create API key in dashboard
   - Set billing limits ($5-10 recommended for development)

2. **Pinecone API Key**
   - Sign up at https://www.pinecone.io
   - Create a free account (Starter tier)
   - Generate API key from console

3. **Netlify Account**
   - Sign up at https://www.netlify.com
   - Connect GitHub repository
   - No API key needed initially

## Phase 1 Tasks

### Task 1: Development Environment Setup

#### 1.0 Python Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python3 --version
pip list
```

#### 1.1 Initialize React Project
```bash
# Create new Vite + React project
npm create vite@latest system-design-rag -- --template react
cd system-design-rag
npm install

# Install dependencies
npm install axios dotenv
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### 1.2 Configure Tailwind CSS
Update `tailwind.config.js`:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Update `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### 1.3 Set Up Netlify Functions
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Install dependencies for serverless functions
npm install @netlify/functions openai @pinecone-database/pinecone
```

Create `netlify.toml`:
```toml
[build]
  command = "npm run build"
  functions = "netlify/functions"
  publish = "dist"

[dev]
  command = "npm run dev"
  port = 5173
  targetPort = 5173
  
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

#### 1.4 Environment Variables
Create `.env` file (never commit this):
```env
VITE_API_URL=/.netlify/functions
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=system-design-rag
```

Create `.env.example` (commit this):
```env
VITE_API_URL=/.netlify/functions
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=system-design-rag
```

### Task 2: Data Collection Scripts

#### 2.1 Project Structure for Scripts
```bash
mkdir -p scripts data/raw data/processed data/embeddings
```

#### 2.2 Content Scraper Script
Create `scripts/scrape_content.py`:
```python
# Web scraper for system design content
# This will scrape publicly available system design resources
```

#### 2.3 Data Validation Script
Create `scripts/validate_data.py`:
```python
# Validates scraped content structure and quality
```

#### 2.4 Manual Content Sources
Create `data/sources.json`:
```json
{
  "sources": [
    {
      "name": "System Design Primer",
      "url": "https://github.com/donnemartin/system-design-primer",
      "type": "github",
      "topics": ["general"]
    },
    {
      "name": "High Scalability Blog",
      "url": "http://highscalability.com/",
      "type": "blog",
      "topics": ["scalability", "architecture"]
    }
  ]
}
```

### Task 3: Data Processing Pipeline

#### 3.1 Text Chunking Script
Create `scripts/chunk_content.py`:
```python
# Splits documents into optimal chunks for embeddings
# Target: 500-1000 tokens per chunk
# Uses tiktoken for accurate token counting
```

#### 3.2 Embedding Generation Script
Create `scripts/generate_embeddings.py`:
```python
# Generates embeddings using OpenAI API
# Uses text-embedding-3-small model
# Batch processing with progress tracking
```

#### 3.3 Pinecone Upload Script
Create `scripts/upload_to_pinecone.py`:
```python
# Uploads vectors to Pinecone index
# Includes metadata for filtering and retrieval
# Creates index if it doesn't exist
```

## Development Workflow

### Step-by-Step Process

1. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Set up React project**
   ```bash
   npm create vite@latest system-design-rag -- --template react
   cd system-design-rag
   npm install
   ```

3. **Install all dependencies**
   ```bash
   # Python dependencies (in activated venv)
   pip install -r requirements.txt
   
   # Node.js dependencies
   npm install axios dotenv
   npm install -D tailwindcss postcss autoprefixer
   npm install @netlify/functions openai @pinecone-database/pinecone
   ```

3. **Create folder structure**
   ```bash
   mkdir -p scripts data/raw data/processed data/embeddings netlify/functions
   ```

4. **Configure environment**
   - Create `.env` file with API keys
   - Set up `netlify.toml`
   - Configure Tailwind

5. **Build data collection scripts** (Python)
   - Content scraper
   - Data validator
   - Chunking algorithm
   - Embedding generator
   - Pinecone uploader

6. **Test locally**
   ```bash
   # Activate Python virtual environment first
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   
   # Test data collection
   python3 scripts/scrape_content.py
   python3 scripts/validate_data.py
   
   # Test data processing
   python3 scripts/chunk_content.py
   python3 scripts/generate_embeddings.py
   python3 scripts/upload_to_pinecone.py
   ```

## Testing Checklist

### Development Environment
- [ ] Node.js and npm installed and working
- [ ] Project created with Vite
- [ ] Tailwind CSS configured correctly
- [ ] Netlify CLI installed
- [ ] Environment variables set up
- [ ] `.gitignore` includes `.env` and sensitive files

### Data Collection
- [ ] Scraper successfully extracts content
- [ ] Content is properly formatted
- [ ] Validation script catches errors
- [ ] At least 10 sample documents collected

### Data Processing
- [ ] Chunking produces appropriate sizes
- [ ] Embeddings generated successfully
- [ ] Pinecone index created
- [ ] Vectors uploaded without errors
- [ ] Metadata properly attached

## Common Issues and Solutions

### Issue: OpenAI Rate Limits
**Solution**: Add delays between API calls, implement exponential backoff

### Issue: Pinecone Connection Errors
**Solution**: Verify API key and environment settings, check index name

### Issue: Large File Processing
**Solution**: Process in batches, add progress logging

### Issue: Memory Issues
**Solution**: Process data in chunks, use streams for large files

## Next Steps

After completing Phase 1:
1. Verify Pinecone index has data
2. Test vector search functionality
3. Begin Phase 2: RAG Implementation
4. Create API endpoints for query handling

## Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Pinecone Quickstart](https://docs.pinecone.io/docs/quickstart)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)