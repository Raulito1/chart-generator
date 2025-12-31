"""
Request models for chart generation API.
"""
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from .chart_spec import ChartType


class UserHints(BaseModel):
    """Optional user-provided hints for chart generation."""
    preferred_chart_type: Optional[ChartType] = Field(None, description="User's preferred chart type")
    x_field: Optional[str] = Field(None, description="Suggested field name for X-axis")
    y_field: Optional[str] = Field(None, description="Suggested field name for Y-axis")
    units: Optional[Dict[str, str]] = Field(
        None, 
        description="Units for fields, e.g., {'value': 'kg', 'time': 'seconds'}"
    )
    formatting: Optional[Dict[str, str]] = Field(
        None,
        description="Format strings for fields, e.g., {'value': '{:.2f}', 'date': '%Y-%m-%d'}"
    )


class ChartRequest(BaseModel):
    """Request payload for chart generation."""
    data: Union[Dict[str, Any], List[Any]] = Field(..., description="User-provided JSON data (object or array)")
    hints: Optional[UserHints] = Field(None, description="Optional user hints for chart generation")
    
    @field_validator("data")
    @classmethod
    def validate_data(cls, v: Union[Dict[str, Any], List[Any]]) -> Dict[str, Any]:
        """Normalize data: convert arrays to dict format, validate structure."""
        if isinstance(v, list):
            if not v:
                raise ValueError("Data array cannot be empty")
            # Normalize array to dict format: { "data": [...] }
            return {"data": v}
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Data object cannot be empty")
            return v
        else:
            raise ValueError("Data must be a JSON object or array")

