# Chart Generator Backend

FastAPI backend for automatic chart generation from JSON data.

## Setup with Poetry

Poetry automatically manages virtual environments, so you don't need to create one manually.

### Installation

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Run the server**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Common Poetry Commands

- `poetry install` - Install all dependencies
- `poetry add <package>` - Add a new dependency
- `poetry add --group dev <package>` - Add a dev dependency
- `poetry run <command>` - Run a command in the Poetry environment
- `poetry shell` - Activate the Poetry shell (optional, you can use `poetry run` instead)
- `poetry update` - Update dependencies

### Alternative: Using venv

If you prefer traditional venv:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

