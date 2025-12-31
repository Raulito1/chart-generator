"""
ChartSpec: Stable contract between backend and frontend for chart configuration.
This model is designed to be chart-library agnostic and can be converted to
Highcharts, Chart.js, or any other library on the frontend.
"""
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class ChartType(str, Enum):
    """Supported chart types with rationale for inference."""
    LINE = "line"
    BAR = "bar"
    COLUMN = "column"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"


class AxisSpec(BaseModel):
    """Specification for a chart axis."""
    title: str = Field(..., description="Axis title/label")
    field: Optional[str] = Field(None, description="Data field name for this axis")
    type: str = Field("linear", description="Axis type: linear, datetime, category, log")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'kg', '%', '$')")
    format: Optional[str] = Field(None, description="Format string for values")
    min: Optional[float] = Field(None, description="Minimum axis value")
    max: Optional[float] = Field(None, description="Maximum axis value")


class SeriesSpec(BaseModel):
    """Specification for a data series."""
    name: str = Field(..., description="Series name/legend label")
    data: List[Union[Dict[str, Any], List[Union[float, str]], float]] = Field(
        ..., description="Series data points"
    )
    type: Optional[str] = Field(None, description="Series type override (if different from chart type)")
    color: Optional[str] = Field(None, description="Series color (hex code)")
    y_axis: int = Field(0, description="Y-axis index (for multi-axis charts)")


class ChartSpec(BaseModel):
    """
    Complete chart specification contract.
    This is the stable interface returned by the backend and consumed by the frontend.
    """
    chart_type: ChartType = Field(..., description="Recommended chart type")
    title: str = Field(..., description="Chart title")
    subtitle: Optional[str] = Field(None, description="Chart subtitle")
    
    # Data series
    series: List[SeriesSpec] = Field(..., min_length=1, description="Chart data series")
    
    # Axes configuration
    x_axis: AxisSpec = Field(..., description="X-axis specification")
    y_axis: Optional[AxisSpec] = Field(None, description="Y-axis specification (None for pie charts)")
    
    # Metadata
    rationale: str = Field(..., description="Explanation of why this chart type was chosen")
    alternative_types: List[ChartType] = Field(
        default_factory=list, 
        description="Other chart types that could work with this data"
    )
    
    # Accessibility
    description: Optional[str] = Field(None, description="Chart description for screen readers")
    
    # Additional configuration (chart-library agnostic)
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional chart configuration options"
    )
    
    @field_validator("chart_type")
    @classmethod
    def validate_chart_type(cls, v: ChartType) -> ChartType:
        """Ensure chart type is valid."""
        return v
    
    @field_validator("series")
    @classmethod
    def validate_series(cls, v: List[SeriesSpec]) -> List[SeriesSpec]:
        """Ensure at least one series exists."""
        if not v:
            raise ValueError("At least one series is required")
        return v

