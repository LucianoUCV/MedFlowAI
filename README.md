# MedFlowAI

Medical AI Flow Management System - A FastAPI-based backend service for medical workflow automation and AI integration.

## Project Structure

```
├── app/                         # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI app with all routes
│   └── services/                # Folder for business logic
│       ├── __init__.py
│       ├── llm_service.py       # Service for AI chat and summary
│       └── supabase_service.py  # Service for Supabase integration
├── assets/                      # Assets folder 
│   └── logopreview1.png         # Application logo
├── templates/                   # Folder with all html pages
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example environment variables
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MedFlowAI
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process # If not configured for Windows
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Server

### Option 1: Using the entry point script
```bash
python main.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using uvicorn with custom settings
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --log-level info

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at `http://localhost:8000`

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **Tailwind CSS** - CSS framework
- **HTMX** - Front-end JavaScript library that extends HTML
- **Alpine.js** - drop in version of a JS framework
