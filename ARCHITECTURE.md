# Architecture Documentation

## Overview

The Chart Generator is a full-stack application that automatically generates charts from arbitrary JSON data. The architecture is designed around a stable **ChartSpec** contract that decouples the backend inference logic from the frontend rendering library.

## Architecture Principles

1. **Stable Contract**: The `ChartSpec` interface is the single source of truth between frontend and backend
2. **Library Agnostic**: ChartSpec can be converted to any charting library (Highcharts, Chart.js, D3, etc.)
3. **Deterministic**: Chart inference is rule-based and testable
4. **Extensible**: New chart types can be added without rewriting the frontend
5. **Accessible**: Charts include titles, labels, and fallback tabular views

## System Architecture

```
┌─────────────────┐
│   React Frontend │
│  (TypeScript)    │
│                 │
│  - JsonInput    │
│  - ChartDisplay │
│  - RTK Query    │
└────────┬────────┘
         │ HTTP/REST
         │ ChartSpec
         ▼
┌─────────────────┐
│  FastAPI Backend │
│    (Python)      │
│                 │
│  - Validation   │
│  - Inference    │
│  - ChartSpec    │
└─────────────────┘
```

## API Contracts

### 1. Generate Chart Endpoint

**POST** `/api/v1/charts/generate`

**Request Body:**
```json
{
  "data": {
    "points": [
      { "t": "2025-12-01", "value": 10 },
      { "t": "2025-12-02", "value": 15 }
    ]
  },
  "hints": {
    "preferred_chart_type": "line",
    "x_field": "t",
    "y_field": "value",
    "units": {
      "value": "kg"
    },
    "formatting": {
      "t": "%Y-%m-%d"
    }
  }
}
```

**Response:**
```json
{
  "chart_type": "line",
  "title": "Time Series Data",
  "subtitle": null,
  "series": [
    {
      "name": "Series 1",
      "data": [[1733011200000, 10], [1733097600000, 15]],
      "type": null,
      "color": null,
      "y_axis": 0
    }
  ],
  "x_axis": {
    "title": "Time",
    "field": "t",
    "type": "datetime",
    "unit": null,
    "format": "%Y-%m-%d",
    "min": null,
    "max": null
  },
  "y_axis": {
    "title": "Value",
    "field": "value",
    "type": "linear",
    "unit": "kg",
    "format": null,
    "min": null,
    "max": null
  },
  "rationale": "Line chart selected because data appears to be a time series with 1 series. Line charts are ideal for showing trends over time.",
  "alternative_types": ["area", "column"],
  "description": "Chart showing time series data",
  "config": {}
}
```

### 2. Validate Data Endpoint

**POST** `/api/v1/charts/validate`

**Request Body:**
```json
{
  "points": [
    { "t": "2025-12-01", "value": 10 }
  ]
}
```

**Response:**
```json
{
  "valid": true,
  "patterns": {
    "is_time_series": true,
    "is_categorical": false,
    "is_multi_series": false,
    "is_heatmap": false
  },
  "message": "Data structure is valid"
}
```

### 3. Get Chart Types Endpoint

**GET** `/api/v1/charts/types`

**Response:**
```json
{
  "chart_types": [
    {
      "type": "line",
      "description": "Line chart for time series and continuous data",
      "best_for": ["Time series", "Trends over time", "Continuous data"]
    },
    ...
  ]
}
```

## ChartSpec Contract

The `ChartSpec` is the core contract between frontend and backend. It is defined identically in both:

- **Backend**: `backend/app/models/chart_spec.py` (Pydantic)
- **Frontend**: `frontend/src/types/chartSpec.ts` (TypeScript)

### ChartSpec Fields

| Field | Type | Description |
|------|------|-------------|
| `chart_type` | `ChartType` enum | Recommended chart type (line, bar, column, pie, area, scatter, heatmap) |
| `title` | `string` | Chart title |
| `subtitle` | `string?` | Optional subtitle |
| `series` | `SeriesSpec[]` | Array of data series (min 1) |
| `x_axis` | `AxisSpec` | X-axis specification |
| `y_axis` | `AxisSpec?` | Y-axis specification (null for pie charts) |
| `rationale` | `string` | Explanation of chart type selection |
| `alternative_types` | `ChartType[]` | Other chart types that could work |
| `description` | `string?` | Accessibility description |
| `config` | `object` | Additional chart-library agnostic config |

### SeriesSpec

| Field | Type | Description |
|------|------|-------------|
| `name` | `string` | Series name/legend label |
| `data` | `array` | Data points (format varies by chart type) |
| `type` | `string?` | Series type override |
| `color` | `string?` | Series color (hex) |
| `y_axis` | `number` | Y-axis index (for multi-axis) |

### AxisSpec

| Field | Type | Description |
|------|------|-------------|
| `title` | `string` | Axis title/label |
| `field` | `string?` | Data field name |
| `type` | `string` | Axis type: linear, datetime, category, log |
| `unit` | `string?` | Unit of measurement |
| `format` | `string?` | Format string |
| `min` | `number?` | Minimum value |
| `max` | `number?` | Maximum value |

## Chart Inference Rules

The backend uses rule-based inference to determine chart types:

### 1. Time Series Detection
- **Pattern**: Data contains time/date fields
- **Fields**: `t`, `time`, `date`, `timestamp`, `x`
- **Result**: `LINE` or `AREA` chart

### 2. Categorical Detection
- **Pattern**: Data has labels/categories
- **Fields**: `label`, `category`, `name`
- **Result**: `BAR`, `COLUMN`, or `PIE` (if single category)

### 3. Multi-Series Detection
- **Pattern**: Data has multiple series
- **Structure**: `{ "series": [...] }` or multiple value arrays
- **Result**: `LINE` or `BAR` chart

### 4. Heatmap Detection
- **Pattern**: 2D grid data
- **Structure**: `{ "rows": [...], "columns": [...], "values": [[...]] }`
- **Result**: `HEATMAP`

### 5. Default
- **Fallback**: `COLUMN` chart

## Data Structure Patterns

The system recognizes these JSON patterns:

### Pattern 1: Time Series
```json
{
  "points": [
    { "t": "2025-12-01", "value": 10 },
    { "t": "2025-12-02", "value": 15 }
  ]
}
```

### Pattern 2: Categorical
```json
{
  "items": [
    { "label": "A", "value": 45 },
    { "label": "B", "value": 30 }
  ]
}
```

### Pattern 3: Multi-Series
```json
{
  "series": [
    {
      "name": "CPU",
      "points": [
        { "t": "2025-12-01", "value": 50 }
      ]
    },
    {
      "name": "Memory",
      "points": [
        { "t": "2025-12-01", "value": 60 }
      ]
    }
  ]
}
```

### Pattern 4: Categories + Values
```json
{
  "categories": ["A", "B", "C"],
  "values": [45, 30, 25]
}
```

## Frontend Rendering Strategy

### ChartSpec → Highcharts Conversion

The `chartSpecToHighcharts` utility (`frontend/src/utils/chartConverter.ts`) converts ChartSpec to Highcharts options:

1. **Chart Type Mapping**: Maps `ChartType` enum to Highcharts chart types
2. **Series Conversion**: Formats series data based on chart type
3. **Axis Configuration**: Maps `AxisSpec` to Highcharts axis options
4. **Accessibility**: Adds titles, descriptions, and labels

### Component Structure

- **JsonInput**: Handles JSON input (paste/upload) and optional hints
- **ChartDisplay**: Renders chart using Highcharts + provides tabular fallback
- **App**: Main orchestrator using RTK Query for API calls

## Validation & Security

### Backend Validation

1. **Pydantic Models**: Automatic validation of request/response structures
2. **Data Structure Checks**: Validates JSON structure before inference
3. **Type Safety**: Type checking for all data transformations
4. **Error Handling**: Helpful error messages for invalid payloads

### Security Considerations

1. **Input Size Limits**: Consider adding max payload size limits
2. **Rate Limiting**: Add rate limiting for production
3. **CORS**: Configured for local development (adjust for production)
4. **Sanitization**: JSON parsing is safe (no code execution)

## Extensibility

### Adding New Chart Types

1. **Backend**:
   - Add to `ChartType` enum in `chart_spec.py`
   - Add detection logic in `chart_inference.py`
   - Update inference rules

2. **Frontend**:
   - Add to `ChartType` enum in `chartSpec.ts`
   - Update `chartConverter.ts` to handle new type
   - Highcharts will automatically support if it's a standard type

### Adding New Data Patterns

1. Update `_extract_data` in `chart_inference.py`
2. Add pattern detection methods
3. Update inference rules

## Testing Strategy

### Backend Tests
- Unit tests for inference rules
- Integration tests for API endpoints
- Validation tests for edge cases

### Frontend Tests
- Component tests for UI
- Integration tests for API calls
- Chart rendering tests

## Deployment

### Backend

**Using Poetry (recommended):**
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Or using traditional venv:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm run preview  # or serve with nginx/apache
```

## Future Enhancements

1. **Chart Type Switching**: Allow users to switch between alternative chart types
2. **Export**: Export charts as PNG/SVG/PDF
3. **Templates**: Save and reuse chart configurations
4. **Real-time Updates**: Support streaming data updates
5. **Custom Styling**: Allow theme customization
6. **Advanced Inference**: ML-based chart type recommendation

