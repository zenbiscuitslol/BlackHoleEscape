#!/usr/bin/env bash
set -euo pipefail

# --- Always run from project root ---
cd "$(dirname "$0")"

# --- Step 1: Ensure Python + pip exist ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python3 not found. Please install Python 3.9+." >&2
  exit 1
fi
if ! command -v pip3 >/dev/null 2>&1; then
  echo "❌ pip3 not found. Installing it..."
  python3 -m ensurepip --upgrade || {
    echo "❌ Failed to install pip automatically." >&2
    exit 1
  }
fi

# --- Step 2: Create and activate venv (optional but safer) ---
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtual environment (.venv)..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# --- Step 3: Install dependencies ---
if [ ! -f "requirements.txt" ]; then
  echo "🧾 Creating requirements.txt with default packages..."
  cat > requirements.txt <<'EOF'
flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
requests>=2.32.0
EOF
fi

echo "📥 Installing dependencies..."
pip install -r requirements.txt

# --- Step 4: Load environment variables from .env ---
if [ -f .env ]; then
  echo "🔑 Loading .env..."
  export FT_CLIENT_ID="$(grep -E '^FT_CLIENT_ID=' .env | cut -d '=' -f2- | tr -d '\r')"
  export FT_CLIENT_SECRET="$(grep -E '^FT_CLIENT_SECRET=' .env | cut -d '=' -f2- | tr -d '\r')"
else
  echo "⚠️  .env file not found! API keys may be missing."
fi

# --- Step 5: Run Flask server ---
export FLASK_APP=main.connect
export FLASK_ENV=development
echo "🚀 Starting Flask..."
python3 -m flask run --debug --port=5000
