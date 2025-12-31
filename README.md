# Chart Generator

A web application that automatically generates charts from JSON data using React 19 + TypeScript + Highcharts on the frontend and Python FastAPI on the backend.

## Architecture

- **Frontend**: React 19 + TypeScript + Vite 7 + Tailwind CSS v4 + Highcharts + RTK Query
- **Backend**: Python FastAPI + Pydantic for validation
- **Contract**: Stable ChartSpec interface between frontend and backend

## Project Structure

```
chart-generator/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── models/   # Pydantic models
│   │   ├── services/ # Chart inference logic
│   │   └── api/      # API endpoints
│   └── requirements.txt
├── frontend/         # React application
│   ├── src/
│   │   ├── types/    # TypeScript interfaces
│   │   ├── api/      # RTK Query slices
│   │   ├── components/ # React components
│   │   └── utils/    # ChartSpec → Highcharts conversion
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+ (for backend)
- Poetry (recommended) or pip + venv
- Node.js 18+ and npm (for frontend)

### Backend Setup

**Using Poetry (recommended):**
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

**Or using traditional venv:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will run on `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Start both backend and frontend** (in separate terminals)
2. **Open the frontend** in your browser
3. **Paste JSON data** or use the example buttons
4. **Click "Generate Chart"** to see the result

### Example JSON Formats

See the `examples/` directory for sample JSON files:
- `time-series.json` - Time series data
- `categorical.json` - Categorical breakdown
- `multi-series.json` - Multiple data series

## API Documentation

See `ARCHITECTURE.md` for detailed API contracts, architecture overview, and design decisions.

## Key Features

✅ **Automatic Chart Type Inference** - Analyzes JSON structure and recommends appropriate chart types  
✅ **Stable ChartSpec Contract** - Library-agnostic chart specification  
✅ **RTK Query Integration** - Efficient data fetching and caching  
✅ **Accessibility** - Charts include titles, labels, and tabular fallbacks  
✅ **Extensible** - Easy to add new chart types and data patterns  
✅ **Type Safe** - Full TypeScript + Pydantic validation  

## Project Structure

```
chart-generator/
├── backend/
│   ├── app/
│   │   ├── models/        # Pydantic models (ChartSpec, requests)
│   │   ├── services/      # Chart inference logic
│   │   ├── api/           # FastAPI routes
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── types/         # TypeScript interfaces
│   │   ├── api/           # RTK Query slices
│   │   ├── components/    # React components
│   │   ├── utils/         # ChartSpec → Highcharts converter
│   │   └── store/         # Redux store
│   └── package.json
├── examples/              # Sample JSON files
├── ARCHITECTURE.md        # Detailed architecture docs
└── README.md
```

