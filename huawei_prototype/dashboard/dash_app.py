from django_plotly_dash import DjangoDash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .dash_components import (
    create_alert_panel,
    create_metrics_panel,
    create_incident_list,
    create_weather_advisory,
    create_trend_chart,
    create_incident_breakdown
)

def register_dash_app():
    app = DjangoDash(
        "EmergencyDashboard",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Emergency Response Dashboard", className="text-center mb-4"),
            ], width=12)
        ], style={"flex": "0 0 auto"}),
        dbc.Row([
            dbc.Col([create_alert_panel()], width=12)
        ], className="mb-4", style={"flex": "0 0 auto"}),
        dbc.Row([
            dbc.Col([create_metrics_panel()], width=8),
            dbc.Col([create_weather_advisory()], width=4)
        ], className="mb-4", style={"flex": "0 0 auto"}),
        dbc.Row([
            dbc.Col([create_incident_list()], width=8, style={"height": "350px", "overflowY": "auto"}),
            dbc.Col([create_incident_breakdown()], width=4, style={"height": "350px", "overflowY": "auto"})
        ], className="mb-4", style={"flex": "0 0 auto"}),
        dbc.Row([
            dbc.Col([create_trend_chart()], width=12, style={"flex": "1 1 0", "minHeight": 0})
        ], style={"flex": "1 1 0", "minHeight": 0})
    ], fluid=True, style={
        "height": "100%",
        "width": "100%",
        "minHeight": 0,
        "minWidth": 0,
        "display": "flex",
        "flexDirection": "column",
        "marginTop": "32px",
        "marginLeft": "0px",
        "marginRight": "0px",
        "paddingLeft": "32px",
        "paddingRight": "32px"
    })
    return app

def create_dash_app():
    return register_dash_app()

# Register the app at import time
register_dash_app() 