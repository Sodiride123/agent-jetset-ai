# Deploy Dependencies

This guide prepares a VM image with all dependencies pre-installed. This image can be shared and reused.

## Prerequisites

The sandbox comes with system dependencies pre-installed:
- Python 3.11+
- Node.js 20+
- npm
- jq
- git

## Step 1: Clone Repository

```bash
# Navigate to workspace
cd /workspace

# Clone the repository
git clone https://github.com/NinjaTech-AI/agent-jetset-ai.git

# Navigate to project directory
cd agent-jetset-ai
```

## Step 2: Install Backend Dependencies

```bash
# Navigate to backend directory
cd /workspace/agent-jetset-ai/backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
```

## Step 3: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd /workspace/agent-jetset-ai/frontend

# Install Node.js dependencies
npm install
```

## Step 4: Verify Installation

```bash
# Check backend dependencies
cd /workspace/agent-jetset-ai/backend
source .venv/bin/activate
python3 -c "import flask; import requests; print('Backend dependencies OK')"
deactivate

# Check frontend dependencies
cd /workspace/agent-jetset-ai/frontend
npm list --depth=0 && echo "Frontend dependencies OK"

# Check project structure
cd /workspace/agent-jetset-ai
ls -la
```

Expected output:
- `backend/` directory with `.venv/` folder
- `frontend/` directory with `node_modules/` folder
- `settings.json` file
- `start.sh` file

## Step 5: Clean Up (Optional)

Before creating the VM image, clean up unnecessary files:

```bash
# Remove any cache files
cd /workspace/agent-jetset-ai
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Clear npm cache
npm cache clean --force
```

## VM Image Ready

The VM image is now ready to be saved and shared. The image includes:
- All system dependencies (Python, Node.js, jq, git)
- Backend Python virtual environment with all packages
- Frontend Node.js dependencies

**Note:** This image does NOT contain any API keys or credentials. See `Deploy app.md` for configuration and startup instructions.
