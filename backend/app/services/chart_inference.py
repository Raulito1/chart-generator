"""
Chart inference service: Analyzes JSON data and determines appropriate chart types.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from ..models.chart_spec import ChartSpec, ChartType, SeriesSpec, AxisSpec
from ..models.requests import UserHints


class ChartInferenceService:
    """Service for inferring chart types from JSON data."""
    
    @staticmethod
    def infer_chart(data: Dict[str, Any], hints: Optional[UserHints] = None) -> ChartSpec:
        """
        Main inference method: analyzes data structure and returns ChartSpec.
        
        Inference rules:
        1. Time series: data has time/date fields → LINE or AREA
        2. Categorical: data has labels/categories → BAR, COLUMN, or PIE
        3. Multi-series: data has multiple series → LINE or BAR
        4. Distribution: numeric values without categories → SCATTER or HISTOGRAM
        5. Heatmap: 2D grid data → HEATMAP
        """
        if hints and hints.preferred_chart_type:
            # Respect user preference if data structure supports it
            chart_type = hints.preferred_chart_type
        else:
            chart_type = ChartInferenceService._detect_chart_type(data)
        
        # Extract data points based on structure
        series_list, x_data, y_data = ChartInferenceService._extract_data(data, hints)
        
        # Build axes
        x_axis, y_axis = ChartInferenceService._build_axes(
            data, x_data, y_data, chart_type, hints
        )
        
        # Build series
        series = ChartInferenceService._build_series(series_list, chart_type, hints)
        
        # Generate rationale
        rationale = ChartInferenceService._generate_rationale(data, chart_type, series_list)
        
        # Find alternative chart types
        alternatives = ChartInferenceService._find_alternatives(chart_type, data)
        
        # Generate title
        title = ChartInferenceService._generate_title(data, chart_type)
        
        return ChartSpec(
            chart_type=chart_type,
            title=title,
            subtitle=None,
            series=series,
            x_axis=x_axis,
            y_axis=y_axis,
            rationale=rationale,
            alternative_types=alternatives,
            description=f"Chart showing {title.lower()}",
            config={}
        )
    
    @staticmethod
    def _detect_chart_type(data: Dict[str, Any]) -> ChartType:
        """Detect the most appropriate chart type from data structure."""
        # Check for time series pattern
        if ChartInferenceService._is_time_series(data):
            return ChartType.LINE
        
        # Check for categorical breakdown
        if ChartInferenceService._is_categorical(data):
            # If single category with values, pie chart might work
            if ChartInferenceService._is_single_category(data):
                return ChartType.PIE
            return ChartType.COLUMN
        
        # Check for multi-series
        if ChartInferenceService._is_multi_series(data):
            return ChartType.LINE
        
        # Check for 2D grid (heatmap)
        if ChartInferenceService._is_heatmap_data(data):
            return ChartType.HEATMAP
        
        # Default: column chart
        return ChartType.COLUMN
    
    @staticmethod
    def _is_time_series(data: Dict[str, Any]) -> bool:
        """Check if data represents a time series."""
        # Pattern 1: { "points": [{ "t": "2025-12-01", "value": 10 }, ...] }
        if "points" in data:
            points = data["points"]
            if isinstance(points, list) and points:
                first = points[0]
                if isinstance(first, dict):
                    # Check for time-like fields
                    time_fields = ["t", "time", "date", "timestamp", "x"]
                    for field in time_fields:
                        if field in first:
                            value = first[field]
                            if ChartInferenceService._looks_like_date(value):
                                return True
        
        # Pattern 2: { "dates": [...], "values": [...] }
        if "dates" in data or "times" in data:
            return True
        
        # Pattern 3: { "data": [{ "date": "...", ... }, ...] } - normalized array
        if "data" in data:
            data_list = data["data"]
            if isinstance(data_list, list) and data_list:
                first = data_list[0]
                if isinstance(first, dict):
                    time_fields = ["t", "time", "date", "timestamp"]
                    for field in time_fields:
                        if field in first:
                            value = first[field]
                            if ChartInferenceService._looks_like_date(value):
                                return True
        
        # Pattern 4: Direct array with time field
        for key, value in data.items():
            if isinstance(value, list) and value:
                if isinstance(value[0], dict):
                    for field in ["t", "time", "date", "timestamp"]:
                        if field in value[0]:
                            return True
        
        return False
    
    @staticmethod
    def _is_categorical(data: Dict[str, Any]) -> bool:
        """Check if data represents categorical breakdown."""
        # Pattern: { "items": [{ "label": "A", "value": 4 }, ...] }
        if "items" in data:
            items = data["items"]
            if isinstance(items, list) and items:
                first = items[0]
                if isinstance(first, dict):
                    if "label" in first or "category" in first or "name" in first:
                        return True
        
        # Pattern: { "data": [{ "category": "...", "sales": ... }, ...] } - normalized array
        if "data" in data:
            data_list = data["data"]
            if isinstance(data_list, list) and data_list:
                first = data_list[0]
                if isinstance(first, dict):
                    if "label" in first or "category" in first or "name" in first:
                        return True
        
        # Pattern: { "categories": [...], "values": [...] }
        if "categories" in data and "values" in data:
            return True
        
        return False
    
    @staticmethod
    def _is_single_category(data: Dict[str, Any]) -> bool:
        """Check if categorical data has single series (suitable for pie)."""
        if "items" in data:
            items = data["items"]
            if isinstance(items, list) and len(items) > 0:
                first = items[0]
                if isinstance(first, dict):
                    # Only one value field (not multiple series)
                    value_fields = [k for k in first.keys() if k not in ["label", "category", "name"]]
                    return len(value_fields) == 1
        return False
    
    @staticmethod
    def _is_multi_series(data: Dict[str, Any]) -> bool:
        """Check if data has multiple series."""
        if "series" in data:
            series = data["series"]
            if isinstance(series, list):
                return len(series) > 1
        
        # Pattern: { "data": [{ "store": "A", "category": "X", "sales": ... }, ...] }
        # Check if normalized array has grouping fields (store, category, etc.)
        if "data" in data:
            data_list = data["data"]
            if isinstance(data_list, list) and data_list:
                first = data_list[0]
                if isinstance(first, dict):
                    # Count grouping fields (non-numeric, non-date fields)
                    grouping_fields = []
                    for key, value in first.items():
                        if key not in ["id", "date", "timestamp", "t", "time"]:
                            if not isinstance(value, (int, float)):
                                grouping_fields.append(key)
                    # If we have grouping fields, it could be multi-series
                    if len(grouping_fields) > 0:
                        # Check if we have multiple unique values in grouping fields
                        unique_values = set()
                        for item in data_list[:10]:  # Sample first 10
                            if isinstance(item, dict):
                                for field in grouping_fields:
                                    if field in item:
                                        unique_values.add(str(item[field]))
                        if len(unique_values) > 1:
                            return True
        
        # Check for multiple value arrays
        value_keys = [k for k in data.keys() if k not in ["categories", "labels", "dates", "times", "data"]]
        if len(value_keys) > 1:
            return True
        
        return False
    
    @staticmethod
    def _is_heatmap_data(data: Dict[str, Any]) -> bool:
        """Check if data represents a 2D grid suitable for heatmap."""
        # Pattern: { "rows": [...], "columns": [...], "values": [[...], ...] }
        if "rows" in data and "columns" in data and "values" in data:
            return True
        return False
    
    @staticmethod
    def _extract_data(
        data: Dict[str, Any], 
        hints: Optional[UserHints]
    ) -> Tuple[List[Dict[str, Any]], List[Any], List[Any]]:
        """Extract data points, x values, and y values from JSON structure."""
        x_field = hints.x_field if hints else None
        y_field = hints.y_field if hints else None
        
        # Pattern 1: { "points": [{ "t": "...", "value": ... }, ...] }
        if "points" in data:
            points = data["points"]
            if isinstance(points, list):
                x_data = []
                y_data = []
                for point in points:
                    if isinstance(point, dict):
                        # Auto-detect x and y fields
                        if not x_field:
                            x_field = ChartInferenceService._find_x_field(point)
                        if not y_field:
                            y_field = ChartInferenceService._find_y_field(point)
                        
                        if x_field and x_field in point:
                            x_data.append(point[x_field])
                        if y_field and y_field in point:
                            y_data.append(point[y_field])
                
                return [{"x": x_data, "y": y_data}], x_data, y_data
        
        # Pattern 2: { "items": [{ "label": "...", "value": ... }, ...] }
        if "items" in data:
            items = data["items"]
            if isinstance(items, list):
                labels = []
                values = []
                for item in items:
                    if isinstance(item, dict):
                        label_key = x_field or "label"
                        value_key = y_field or "value"
                        if label_key in item:
                            labels.append(item[label_key])
                        if value_key in item:
                            values.append(item[value_key])
                
                return [{"x": labels, "y": values}], labels, values
        
        # Pattern 3: { "series": [{ "name": "...", "points": [...] }, ...] }
        if "series" in data:
            series = data["series"]
            if isinstance(series, list):
                series_list = []
                all_x = []
                all_y = []
                for s in series:
                    if isinstance(s, dict) and "points" in s:
                        points = s["points"]
                        x_vals = []
                        y_vals = []
                        for point in points:
                            if isinstance(point, dict):
                                x_field_local = x_field or ChartInferenceService._find_x_field(point)
                                y_field_local = y_field or ChartInferenceService._find_y_field(point)
                                if x_field_local and x_field_local in point:
                                    x_vals.append(point[x_field_local])
                                if y_field_local and y_field_local in point:
                                    y_vals.append(point[y_field_local])
                        series_list.append({
                            "name": s.get("name", "Series"),
                            "x": x_vals,
                            "y": y_vals
                        })
                        if x_vals:
                            all_x = x_vals  # Use first series x values
                        all_y.extend(y_vals)
                
                return series_list, all_x, all_y
        
        # Pattern 4: { "categories": [...], "values": [...] }
        if "categories" in data and "values" in data:
            categories = data["categories"]
            values = data["values"]
            if isinstance(categories, list) and isinstance(values, list):
                return [{"x": categories, "y": values}], categories, values
        
        # Pattern 5: { "data": [{ "date": "...", "sales": ... }, ...] } - normalized array
        if "data" in data:
            data_list = data["data"]
            if isinstance(data_list, list) and data_list:
                first = data_list[0]
                if isinstance(first, dict):
                    # Auto-detect fields
                    if not x_field:
                        x_field = ChartInferenceService._find_x_field(first)
                    if not y_field:
                        y_field = ChartInferenceService._find_y_field(first)
                    
                    # Check if we should group by a field (e.g., store, category)
                    grouping_field = None
                    for key in ["store", "category", "group", "series"]:
                        if key in first:
                            grouping_field = key
                            break
                    
                    if grouping_field:
                        # Group by the grouping field and create multiple series
                        grouped = {}
                        for item in data_list:
                            if isinstance(item, dict):
                                group_value = item.get(grouping_field, "Unknown")
                                if group_value not in grouped:
                                    grouped[group_value] = {"x": [], "y": []}
                                
                                if x_field and x_field in item:
                                    grouped[group_value]["x"].append(item[x_field])
                                if y_field and y_field in item:
                                    grouped[group_value]["y"].append(item[y_field])
                        
                        series_list = [
                            {"name": name, "x": data["x"], "y": data["y"]}
                            for name, data in grouped.items()
                        ]
                        
                        # Get all unique x values (dates, etc.)
                        all_x = set()
                        for s in series_list:
                            all_x.update(s["x"])
                        all_x = sorted(list(all_x))
                        
                        return series_list, all_x, []
                    else:
                        # Single series from array
                        x_data = []
                        y_data = []
                        for item in data_list:
                            if isinstance(item, dict):
                                if x_field and x_field in item:
                                    x_data.append(item[x_field])
                                if y_field and y_field in item:
                                    y_data.append(item[y_field])
                        
                        return [{"x": x_data, "y": y_data}], x_data, y_data
        
        # Pattern 6: Direct key-value pairs (fallback)
        # Try to find two arrays or lists
        keys = list(data.keys())
        if len(keys) >= 2:
            first_key = keys[0]
            second_key = keys[1]
            if isinstance(data[first_key], list) and isinstance(data[second_key], list):
                return [
                    {"x": data[first_key], "y": data[second_key]}
                ], data[first_key], data[second_key]
        
        # Default: empty
        return [], [], []
    
    @staticmethod
    def _find_x_field(point: Dict[str, Any]) -> Optional[str]:
        """Find the X-axis field name in a data point."""
        x_candidates = ["t", "time", "date", "timestamp", "x", "label", "category", "name"]
        for candidate in x_candidates:
            if candidate in point:
                return candidate
        # Return first non-numeric key if exists
        for key in point.keys():
            if not isinstance(point[key], (int, float)):
                return key
        return None
    
    @staticmethod
    def _find_y_field(point: Dict[str, Any]) -> Optional[str]:
        """Find the Y-axis field name in a data point."""
        y_candidates = ["value", "y", "values", "count", "amount", "sales", "units", "quantity", "price", "revenue"]
        for candidate in y_candidates:
            if candidate in point:
                return candidate
        # Return first numeric key if exists (excluding id)
        for key in point.keys():
            if key != "id" and isinstance(point[key], (int, float)):
                return key
        return None
    
    @staticmethod
    def _build_axes(
        data: Dict[str, Any],
        x_data: List[Any],
        y_data: List[Any],
        chart_type: ChartType,
        hints: Optional[UserHints]
    ) -> Tuple[AxisSpec, Optional[AxisSpec]]:
        """Build axis specifications."""
        # X-axis
        x_title = "Category"
        x_type = "category"
        x_field = hints.x_field if hints else None
        
        if chart_type == ChartType.PIE:
            # Pie charts don't have axes
            return AxisSpec(title="", field=None, type="category"), None
        
        # Determine X-axis type and title
        if x_data:
            first_x = x_data[0]
            if ChartInferenceService._looks_like_date(first_x):
                x_type = "datetime"
                x_title = "Time"
            elif isinstance(first_x, (int, float)):
                x_type = "linear"
                x_title = "X"
            else:
                x_type = "category"
                x_title = "Category"
        
        x_axis = AxisSpec(
            title=x_title,
            field=x_field,
            type=x_type,
            unit=hints.units.get(x_field) if hints and hints.units and x_field else None,
            format=hints.formatting.get(x_field) if hints and hints.formatting and x_field else None
        )
        
        # Y-axis
        y_axis = None
        if chart_type != ChartType.PIE:
            y_title = "Value"
            y_type = "linear"
            y_field = hints.y_field if hints else None
            
            if y_data:
                first_y = y_data[0]
                if isinstance(first_y, (int, float)):
                    y_type = "linear"
                else:
                    y_type = "category"
            
            y_axis = AxisSpec(
                title=y_title,
                field=y_field,
                type=y_type,
                unit=hints.units.get(y_field) if hints and hints.units and y_field else None,
                format=hints.formatting.get(y_field) if hints and hints.formatting and y_field else None
            )
        
        return x_axis, y_axis
    
    @staticmethod
    def _build_series(
        series_list: List[Dict[str, Any]],
        chart_type: ChartType,
        hints: Optional[UserHints]
    ) -> List[SeriesSpec]:
        """Build series specifications from extracted data."""
        series = []
        
        for idx, s in enumerate(series_list):
            name = s.get("name", f"Series {idx + 1}")
            x_vals = s.get("x", [])
            y_vals = s.get("y", [])
            
            # Format data based on chart type
            if chart_type == ChartType.PIE:
                # Pie charts: [{ name: "A", y: 10 }, ...]
                data = [
                    {"name": str(x_vals[i]), "y": y_vals[i]}
                    for i in range(min(len(x_vals), len(y_vals)))
                ]
            elif chart_type == ChartType.HEATMAP:
                # Heatmap: special format
                data = y_vals  # Will be handled specially
            else:
                # Line/Bar/Column: pairs or arrays
                if len(x_vals) == len(y_vals):
                    data = [[x_vals[i], y_vals[i]] for i in range(len(x_vals))]
                else:
                    data = y_vals
            
            series.append(SeriesSpec(
                name=name,
                data=data,
                type=None,
                color=None,
                y_axis=0
            ))
        
        return series
    
    @staticmethod
    def _generate_rationale(data: Dict[str, Any], chart_type: ChartType, series_list: List[Dict[str, Any]]) -> str:
        """Generate human-readable rationale for chart type selection."""
        num_series = len(series_list)
        
        if chart_type == ChartType.LINE:
            return f"Line chart selected because data appears to be a time series with {num_series} series. Line charts are ideal for showing trends over time."
        elif chart_type == ChartType.PIE:
            return f"Pie chart selected because data represents a single categorical breakdown with {len(series_list[0].get('x', []))} categories. Pie charts effectively show proportions."
        elif chart_type == ChartType.COLUMN:
            return f"Column chart selected because data represents categorical data with {num_series} series. Column charts are effective for comparing categories."
        elif chart_type == ChartType.BAR:
            return f"Bar chart selected for categorical comparison with {num_series} series. Bar charts work well when category names are long."
        elif chart_type == ChartType.AREA:
            return f"Area chart selected for time series data with {num_series} series. Area charts emphasize the magnitude of change over time."
        elif chart_type == ChartType.SCATTER:
            return f"Scatter plot selected for numeric data pairs. Scatter plots reveal relationships between two numeric variables."
        elif chart_type == ChartType.HEATMAP:
            return f"Heatmap selected because data represents a 2D grid. Heatmaps are ideal for visualizing matrix data."
        else:
            return f"Chart type {chart_type.value} selected based on data structure."
    
    @staticmethod
    def _find_alternatives(chart_type: ChartType, data: Dict[str, Any]) -> List[ChartType]:
        """Find alternative chart types that could work with this data."""
        alternatives = []
        
        if chart_type == ChartType.LINE:
            alternatives = [ChartType.AREA, ChartType.COLUMN]
        elif chart_type == ChartType.COLUMN:
            alternatives = [ChartType.BAR, ChartType.LINE]
        elif chart_type == ChartType.BAR:
            alternatives = [ChartType.COLUMN, ChartType.LINE]
        elif chart_type == ChartType.PIE:
            alternatives = [ChartType.COLUMN, ChartType.BAR]
        elif chart_type == ChartType.AREA:
            alternatives = [ChartType.LINE, ChartType.COLUMN]
        
        return alternatives
    
    @staticmethod
    def _generate_title(data: Dict[str, Any], chart_type: ChartType) -> str:
        """Generate a chart title from data structure."""
        # Try to infer from keys
        if "title" in data:
            return str(data["title"])
        
        # Generate from structure
        if "points" in data:
            return "Time Series Data"
        elif "items" in data:
            return "Categorical Breakdown"
        elif "series" in data:
            return "Multi-Series Data"
        else:
            return f"{chart_type.value.title()} Chart"
    
    @staticmethod
    def _looks_like_date(value: Any) -> bool:
        """Check if a value looks like a date/time."""
        if isinstance(value, str):
            # Common date patterns
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{4}-\d{2}-\d{2}T',  # ISO format
            ]
            for pattern in date_patterns:
                if re.search(pattern, value):
                    return True
            # Try parsing
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return True
            except:
                pass
        elif isinstance(value, (int, float)):
            # Unix timestamp (reasonable range: 2000-2100)
            if 946684800 <= value <= 4102444800:
                return True
        return False

