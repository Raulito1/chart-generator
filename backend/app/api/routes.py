"""
API routes for chart generation.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json

from ..models.requests import ChartRequest
from ..models.chart_spec import ChartSpec
from ..services.chart_inference import ChartInferenceService

router = APIRouter(prefix="/api/v1", tags=["charts"])


@router.post("/charts/generate", response_model=ChartSpec)
async def generate_chart(request: ChartRequest) -> ChartSpec:
    """
    Generate a chart specification from JSON data.
    
    **Request Body:**
    ```json
    {
      "data": {
        "points": [
          {"t": "2025-12-01", "value": 10},
          {"t": "2025-12-02", "value": 15}
        ]
      },
      "hints": {
        "preferred_chart_type": "line",
        "x_field": "t",
        "y_field": "value"
      }
    }
    ```
    
    **Response:**
    Returns a ChartSpec with chart type, series, axes, and rationale.
    """
    try:
        # Validate and infer chart
        chart_spec = ChartInferenceService.infer_chart(request.data, request.hints)
        return chart_spec
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate chart: {str(e)}"
        )


@router.post("/charts/validate")
async def validate_data(data: Dict[str, Any]) -> JSONResponse:
    """
    Validate JSON data structure without generating a chart.
    
    Returns validation status and detected data patterns.
    """
    try:
        # Basic validation
        if not isinstance(data, dict):
            raise ValueError("Data must be a JSON object")
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Detect patterns
        patterns = {
            "is_time_series": ChartInferenceService._is_time_series(data),
            "is_categorical": ChartInferenceService._is_categorical(data),
            "is_multi_series": ChartInferenceService._is_multi_series(data),
            "is_heatmap": ChartInferenceService._is_heatmap_data(data),
        }
        
        return JSONResponse(content={
            "valid": True,
            "patterns": patterns,
            "message": "Data structure is valid"
        })
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "valid": False,
                "error": str(e)
            }
        )


@router.get("/charts/types")
async def get_chart_types() -> JSONResponse:
    """
    Get list of supported chart types with descriptions.
    """
    chart_types = [
        {
            "type": "line",
            "description": "Line chart for time series and continuous data",
            "best_for": ["Time series", "Trends over time", "Continuous data"]
        },
        {
            "type": "bar",
            "description": "Horizontal bar chart for categorical comparison",
            "best_for": ["Categorical data", "Long category names", "Comparisons"]
        },
        {
            "type": "column",
            "description": "Vertical column chart for categorical comparison",
            "best_for": ["Categorical data", "Comparisons", "Rankings"]
        },
        {
            "type": "pie",
            "description": "Pie chart for showing proportions",
            "best_for": ["Single category breakdown", "Proportions", "Percentages"]
        },
        {
            "type": "area",
            "description": "Area chart emphasizing magnitude over time",
            "best_for": ["Time series", "Cumulative data", "Stacked trends"]
        },
        {
            "type": "scatter",
            "description": "Scatter plot for relationships between variables",
            "best_for": ["Correlations", "Numeric pairs", "Distributions"]
        },
        {
            "type": "heatmap",
            "description": "Heatmap for 2D grid/matrix data",
            "best_for": ["Matrix data", "Correlation matrices", "2D grids"]
        },
    ]
    
    return JSONResponse(content={"chart_types": chart_types})

