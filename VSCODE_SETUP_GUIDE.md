# VS Code Setup Guide - System Design RAG Project

## Complete Walkthrough: From Zero to Running

This guide will walk you through setting up the project in VS Code from scratch.

---

## Part 1: Prerequisites (5 minutes)

### 1. Install Required Software

**Python 3.9+**
```bash
# Check if you have Python
python3 --version

# If not installed:
# - macOS: brew install python3
# - Windows: Download from python.org
# - Linux: sudo apt-get install python3 python3-pip python3-venv
```

**Node.js 18+**
```bash
# Check if you have Node.js
node --version
npm --version

# If not installed:
# Download from: https://nodejs.org/ (LTS version)
```

**VS Code**
- Download from: https://code.visualstudio.com/
- Install these extensions (recommended):
  - Python (by Microsoft)
  - Pylance (by Microsoft)
  - ES7+ React/Redux/React-Native snippets
  - Prettier - Code formatter
  - GitLens

**Git**
```bash
# Check if you have Git
git --version

# If not installed:
# Download from: https://git-scm.com/
```

---

## Part 2: Create Project Directory (2 minutes)

### Open Terminal/Command Prompt

```bash
# Navigate to where you want your projects
cd ~/Documents  # macOS/Linux
# or
cd C:\Users\YourName\Documents  # Windows

# Create project directory
mkdir system-design-rag
cd system-design-rag

# Initialize git (optional but recommended)
git init
```

---

## Part 3: Download and Organize Files (3 minutes)

### File Structure You'll Create

```
system-design-rag/
├── .env.example
├── .gitignore
├── README.md
├── PRD.md
├── SETUP_PHASE1.md
├── QUICK_START.md
├── PYTHON_CONVERSION_SUMMARY.md
├── ARCHITECTURE.md
├── PROJECT_CHECKLIST.md
├── PHASE1_SUMMARY.md
├── requirements.txt
├── package.json
├── netlify.toml
├── scripts/
│   ├── scrape_content.py
│   ├── validate_data.py
│   ├── chunk_content.py
│   ├── generate_embeddings.py
│   └── upload_to_pinecone.py
└── data/
    └── sources.json
```

### How to Place Files

**Option A: Download from Claude (Easiest)**
1. Click on each file link I provided earlier
2. Copy the content
3. Create the file in your project directory
4. Paste the content

**Option B: Use Terminal**
```bash
# In your system-design-rag directory

# Create folders
mkdir -p scripts data/raw data/processed data/embeddings

# Create empty files (you'll paste content into them)
touch README.md PRD.md requirements.txt package.json
touch .env.example .gitignore netlify.toml
touch scripts/scrape_content.py
touch scripts/validate_data.py
touch scripts/chunk_content.py
touch scripts/generate_embeddings.py
touch scripts/upload_to_pinecone.py
touch data/sources.json
```

---

## Part 4: Open Project in VS Code (1 minute)

### Method 1: From Terminal
```bash
# Make sure you're in the project directory
cd ~/Documents/system-design-rag

# Open in VS Code
code .
```

### Method 2: From VS Code
1. Open VS Code
2. File → Open Folder
3. Navigate to `system-design-rag`
4. Click "Open"

### First Time Setup in VS Code
When VS Code opens:
1. If prompted to "Install recommended extensions" → Click "Install"
2. If prompted to "Select Python interpreter" → Wait (we'll do this after creating venv)

---

## Part 5: Set Up Python Virtual Environment (5 minutes)

### In VS Code Terminal

Open a new terminal: **Terminal → New Terminal** (or `` Ctrl+` ``)

```bash
# 1. Create virtual environment
python3 -m venv venv

# You should now see a 'venv' folder in your project

# 2. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# You should now see (venv) at the start of your terminal prompt
# Example: (venv) user@computer:~/system-design-rag$

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install Python dependencies
pip install -r requirements.txt

# This will take 2-3 minutes
# You'll see it installing: openai, pinecone-client, langchain, tiktoken, etc.

# 5. Verify installation
pip list
# You should see all installed packages
```

### Select Python Interpreter in VS Code

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: "Python: Select Interpreter"
3. Choose: `./venv/bin/python` (the one with venv)

You should now see `Python 3.x.x ('venv')` in the bottom-left of VS Code.

---

## Part 6: Set Up Node.js Dependencies (3 minutes)

### In VS Code Terminal (same terminal)

```bash
# Make sure you're in the project root
pwd  # Should show: .../system-design-rag

# Install Node.js dependencies
npm install

# This creates node_modules folder and package-lock.json
```

---

## Part 7: Configure Environment Variables (5 minutes)

### Create .env File

In VS Code:
1. Right-click in Explorer (left sidebar) → New File
2. Name it: `.env`
3. Add this content:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration  
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=system-design-rag

# API Configuration
VITE_API_URL=/.netlify/functions
```

### Get API Keys (Do This Now or Later)

**OpenAI API Key:**
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Paste into `.env` file: `OPENAI_API_KEY=sk-your-actual-key`
6. **Important**: Add $5-10 of credit to your account

**Pinecone API Key:**
1. Go to: https://app.pinecone.io/
2. Sign in or create account (free tier is fine)
3. Click "API Keys" in sidebar
4. Copy your API key
5. Paste into `.env` file: `PINECONE_API_KEY=your-actual-key`
6. Note your environment (e.g., `us-east-1`)

**For Now (Testing Without API Keys):**
You can skip getting API keys for now. The first two scripts (scrape and validate) work without them!

---

## Part 8: First Test - Verify Setup (5 minutes)

### Test Python Environment

In VS Code terminal:

```bash
# Make sure venv is activated (you should see (venv) in prompt)
# If not: source venv/bin/activate

# Test 1: Check Python
python3 --version
# Should show: Python 3.9+ 

# Test 2: Check installed packages
pip list | grep openai
# Should show: openai, langchain-openai

# Test 3: Verify scripts are accessible
ls -la scripts/
# Should show: All 5 .py files
```

### Test Node Environment

```bash
# Test Node.js
node --version
# Should show: v18+

# Test npm
npm --version

# Verify package.json scripts
npm run
# Should list all available scripts
```

---

## Part 9: Reading Guide - Start Here! (10 minutes)

### Recommended Reading Order

Open these files in VS Code in this order:

**1. PYTHON_CONVERSION_SUMMARY.md** (5 min read)
- Why Python for data pipeline
- What changed from original plan
- Quick overview of all scripts

**2. QUICK_START.md** (3 min read)
- 30-minute setup guide
- Next immediate steps
- Testing checklist

**3. README.md** (5 min read)
- Project overview
- Features and goals
- Available commands

**4. PRD.md** (10 min read - optional for now)
- Full product requirements
- Technical architecture
- All phases detailed

### How to Open Files in VS Code

**Method 1: Explorer**
- Click on file in left sidebar

**Method 2: Quick Open**
- Press `Cmd+P` (Mac) or `Ctrl+P` (Windows)
- Type filename (e.g., "quick")
- Press Enter

**Method 3: Split View** (Recommended!)
- Open first file
- Right-click tab → "Split Right"
- Now you can read docs side-by-side

---

## Part 10: Run Your First Scripts (10 minutes)

### Script 1: Collect Sample Content

In VS Code terminal:

```bash
# Make sure venv is activated!
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Run the scraper
npm run scrape
# Or directly: python3 scripts/scrape_content.py

# Expected output:
# 🚀 System Design Content Scraper
# 📝 Starting content collection...
# ✅ Saved: load-balancing-basics.json
# ✅ Saved: caching-strategies.json
# ✅ Saved: database-scaling.json
# ✅ Saved: api-design-rest.json
# ✅ Saved: microservices-architecture.json
# ✅ Successfully saved: 5 files
```

**What happened?**
- Created `data/raw/` folder
- Created 5 JSON files with system design content
- Created index file

**View the results:**
```bash
# In terminal
ls -la data/raw/

# Or in VS Code: 
# Click on data/raw/ folder in Explorer
# You should see 5 .json files + index.json
```

### Script 2: Validate Content

```bash
# Run validation
npm run validate
# Or: python3 scripts/validate_data.py

# Expected output:
# 🔍 Starting content validation...
# 📁 Found 5 files to validate
# ✅ load-balancing-basics.json
# ✅ caching-strategies.json
# ✅ database-scaling.json
# ✅ api-design-rest.json
# ✅ microservices-architecture.json
# 
# 📊 Validation Results
# ✅ Passed: 5
# ❌ Failed: 0
# ⚠️  Warnings: 0
# 
# 🎉 All validations passed!
```

### Script 3: Generate Detailed Report

```bash
# Run validation with report
npm run validate:report

# This creates: data/raw/validation-report.json
# Shows statistics about your content
```

---

## Part 11: Explore the Code (10 minutes)

### Open and Review Python Scripts

In VS Code, open these files and read through them:

**1. scripts/scrape_content.py**
- Line 24-30: See the sample content structure
- Line 180+: See how content is saved to JSON

**2. scripts/validate_data.py**  
- Line 38-50: Validation rules
- Line 85-180: Validation logic

**Key Features to Notice:**
- Colored terminal output (from `colorama`)
- Clear error messages
- Type hints (e.g., `def count_tokens(text: str) -> int:`)
- Docstrings explaining what each function does

### VS Code Tips for Reading Code

**Navigate Code:**
- `Cmd+Click` (Mac) or `Ctrl+Click` (Windows) on function name → Jump to definition
- `Cmd+[` / `Cmd+]` → Navigate back/forward
- `Cmd+Shift+O` → Jump to symbol in file

**Understand Imports:**
- Hover over import → See documentation
- Right-click import → "Go to Definition"

**See Documentation:**
- Hover over any function → See docstring

---

## Part 12: Next Steps - Test Remaining Scripts (With API Keys)

### Once You Have API Keys

Update your `.env` file with real API keys, then:

```bash
# Make sure venv is activated
source venv/bin/activate

# Test chunking (doesn't need API keys!)
npm run chunk
# Creates: data/processed/chunks.json

# Test embedding generation (needs OPENAI_API_KEY)
npm run embed
# Creates: data/embeddings/embeddings.json
# Cost: ~$0.001 for 5 sample documents

# Test Pinecone upload (needs PINECONE_API_KEY)
npm run upload
# Uploads vectors to Pinecone
# Creates index if needed
# Tests search functionality
```

### Run Entire Pipeline

```bash
# Run everything in sequence
npm run data:all

# This runs:
# 1. scrape → 2. validate → 3. chunk → 4. embed → 5. upload
```

---

## Part 13: VS Code Workspace Tips

### Recommended Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "venv": true,
    "node_modules": true
  }
}
```

### Useful VS Code Shortcuts

**Terminal:**
- `` Ctrl+` `` → Toggle terminal
- `Cmd+Shift+C` → Open external terminal

**Files:**
- `Cmd+P` → Quick open file
- `Cmd+Shift+E` → Focus on Explorer
- `Cmd+B` → Toggle sidebar

**Search:**
- `Cmd+F` → Find in file
- `Cmd+Shift+F` → Search in all files

**Python Specific:**
- `Shift+Enter` → Run selected code in terminal
- `Cmd+Shift+P` → Command palette

---

## Part 14: Troubleshooting Common Issues

### Issue: "python3: command not found"

**Solution:**
```bash
# Try just "python"
python --version

# If that works, use "python" instead of "python3"
# Or create an alias in your shell
```

### Issue: "venv/bin/activate: No such file"

**Solution:**
```bash
# Make sure you're in the right directory
pwd  # Should show: .../system-design-rag

# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Issue: "pip: command not found" (after activating venv)

**Solution:**
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Issue: Virtual environment not activating in VS Code terminal

**Solution:**
1. Close VS Code
2. Delete venv folder
3. Reopen VS Code
4. Create venv again
5. Select interpreter: `Cmd+Shift+P` → "Python: Select Interpreter"

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Solution:**
```bash
# Make sure venv is activated (look for (venv) in prompt)
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Scripts run but no output

**Solution:**
```bash
# Run with python3 directly to see errors
python3 scripts/scrape_content.py

# Check if data directory exists
ls -la data/
```

---

## Part 15: Quick Reference - Commands You'll Use

### Activate Environment
```bash
# Every time you open a new terminal:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Run Scripts (npm commands)
```bash
npm run scrape      # Collect content
npm run validate    # Validate data
npm run chunk       # Chunk content
npm run embed       # Generate embeddings (needs OpenAI key)
npm run upload      # Upload to Pinecone (needs Pinecone key)
npm run data:all    # Run entire pipeline
```

### Run Scripts (direct Python)
```bash
python3 scripts/scrape_content.py
python3 scripts/validate_data.py
python3 scripts/validate_data.py --report
python3 scripts/chunk_content.py
python3 scripts/generate_embeddings.py
python3 scripts/upload_to_pinecone.py
```

### Check Status
```bash
# Python environment
which python          # Should show venv path
pip list             # Show installed packages

# Project files
ls -la data/raw/          # View collected data
ls -la data/processed/    # View chunked data
ls -la data/embeddings/   # View embeddings

# Git status
git status           # See what's changed
```

---

## Checklist: Are You Set Up?

Use this to verify everything is working:

- [ ] VS Code is installed and open
- [ ] Project folder created: `system-design-rag`
- [ ] All files downloaded and placed correctly
- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Virtual environment activated (`(venv)` in terminal prompt)
- [ ] Python dependencies installed (`pip list` shows packages)
- [ ] Node.js dependencies installed (`node_modules` folder exists)
- [ ] `.env` file created (even if keys not added yet)
- [ ] Read PYTHON_CONVERSION_SUMMARY.md
- [ ] Ran `npm run scrape` successfully
- [ ] Ran `npm run validate` successfully
- [ ] See 5 JSON files in `data/raw/`

**If all checked: You're ready to go! 🎉**

---

## What to Do Next

### Today (No API Keys Required)
1. ✅ Read the documentation
2. ✅ Run scrape and validate scripts
3. ✅ Explore the generated JSON files
4. ✅ Review the Python code

### This Week (With API Keys)
1. Get OpenAI API key
2. Get Pinecone API key
3. Update `.env` file
4. Run `npm run data:all`
5. Verify data in Pinecone

### Next Week (Phase 3)
1. Create Netlify Functions
2. Implement query endpoint
3. Test RAG functionality

---

## Need Help?

**Common Questions:**

Q: Do I need API keys right now?
A: No! The first 2 scripts work without API keys.

Q: How much will API keys cost?
A: ~$0.001 for 5 sample documents. Very cheap for testing.

Q: Can I use Python 3.8?
A: Minimum is 3.9, but 3.10+ is recommended.

Q: What if I don't have VS Code?
A: Any code editor works, but VS Code has the best Python support.

Q: Where should I ask questions?
A: Come back here! I'm happy to help troubleshoot.

---

**You're all set! Start with reading PYTHON_CONVERSION_SUMMARY.md and running the first two scripts. Good luck! 🚀**