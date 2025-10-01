"""Chart component helpers using Plotly."""

from typing import Any, Dict, List, Optional

import plotly.express as px
import plotly.graph_objects as go


def create_line_chart(
    data: Any,
    x: str,
    y: str,
    title: str = "",
    color: str = "#1E40AF",
    height: int = 350,
) -> go.Figure:
    """Create a line chart.

    Args:
        data: DataFrame or dict with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Line color (hex code)
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    fig = px.line(data, x=x, y=y, title=title)
    fig.update_traces(line_color=color, line_width=3)
    fig.update_layout(hovermode="x unified", plot_bgcolor="white", height=height)
    return fig


def create_bar_chart(
    data: Any,
    x: str,
    y: str,
    title: str = "",
    orientation: str = "v",
    color_scale: Optional[List[str]] = None,
    height: int = 350,
) -> go.Figure:
    """Create a bar chart.

    Args:
        data: DataFrame or dict with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal
        color_scale: List of colors for gradient
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    fig = px.bar(data, x=x, y=y, title=title, orientation=orientation)

    if color_scale:
        fig.update_traces(marker_color=color_scale)

    fig.update_layout(height=height, showlegend=False)
    return fig


def create_pie_chart(
    values: List[float],
    names: List[str],
    title: str = "",
    hole: float = 0.0,
    height: int = 300,
) -> go.Figure:
    """Create a pie or donut chart.

    Args:
        values: List of values
        names: List of labels
        title: Chart title
        hole: Size of hole (0 = pie, 0.4 = donut)
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    fig = px.pie(values=values, names=names, title=title, hole=hole)
    fig.update_layout(height=height, showlegend=True)
    return fig


def create_radar_chart(
    categories: List[str],
    values: List[float],
    name: str = "",
    fill_color: str = "rgba(30, 64, 175, 0.3)",
    line_color: str = "#1E40AF",
    height: int = 300,
) -> go.Figure:
    """Create a radar/spider chart.

    Args:
        categories: List of category names
        values: List of values for each category
        name: Series name
        fill_color: Fill color (rgba)
        line_color: Line color (hex)
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=name,
            fillcolor=fill_color,
            line=dict(color=line_color, width=3),
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=height,
    )
    return fig


def create_gauge_chart(
    value: float,
    title: str = "",
    min_value: float = 0,
    max_value: float = 100,
    reference: Optional[float] = None,
    steps: Optional[List[Dict[str, Any]]] = None,
    height: int = 300,
) -> go.Figure:
    """Create a gauge chart.

    Args:
        value: Current value
        title: Chart title
        min_value: Minimum value
        max_value: Maximum value
        reference: Reference line value
        steps: List of step dicts with 'range' and 'color'
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    gauge_config = {
        "axis": {"range": [min_value, max_value]},
        "bar": {"color": "#1E40AF"},
    }

    if steps:
        gauge_config["steps"] = steps

    if reference is not None:
        gauge_config["threshold"] = {
            "line": {"color": "black", "width": 2},
            "thickness": 0.75,
            "value": reference,
        }

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta" if reference else "gauge+number",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            delta={"reference": reference} if reference else None,
            gauge=gauge_config,
        )
    )
    fig.update_layout(height=height)
    return fig

