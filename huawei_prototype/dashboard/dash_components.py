import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import datetime

def create_alert_panel():
    """Create the alert panel component"""
    # Always do the lookup at render time
    try:
        from dashboard.models import Camera
        aye01 = Camera.objects.filter(camera_name__icontains="AYE-01").first()
        or01 = Camera.objects.filter(camera_name__icontains="OR-01").first()
        aye01_url = f"/cameras/view/{aye01.camera_id}/" if aye01 else "#"
        or01_url = f"/cameras/view/{or01.camera_id}/" if or01 else "#"
    except Exception:
        aye01_url = or01_url = "#"

    return dbc.Card([
        dbc.CardHeader([
            html.H4("Critical Alerts", className="mb-0"),
            html.Span("3 Unacknowledged", className="badge bg-danger ms-2")
        ], className="d-flex align-items-center"),
        dbc.CardBody([
            dbc.ListGroup([
                dbc.ListGroupItem([
                    html.Div([
                        html.Span("10:45 AM", className="text-muted me-2"),
                        html.Span("🚨", className="me-2"),
                        html.Strong("Major Collision: AYE nr Clementi (AYE-01)"),
                        html.A("View Details", href=aye01_url, className="btn btn-primary btn-sm ms-auto")
                    ], className="d-flex align-items-center")
                ], className="mb-2"),
                dbc.ListGroupItem([
                    html.Div([
                        html.Span("10:30 AM", className="text-muted me-2"),
                        html.Span("⚠️", className="me-2"),
                        html.Strong("Vehicle Fire: Orchard Rd (OR-01)"),
                        html.A("View Details", href=or01_url, className="btn btn-primary btn-sm ms-auto")
                    ], className="d-flex align-items-center")
                ])
            ])
        ])
    ])

def create_metrics_panel():
    """Create the metrics panel component"""
    return dbc.Card([
        dbc.CardHeader("Key Metrics"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H2("5", className="text-center"),
                    html.P("Active High-Severity Incidents", className="text-center text-muted")
                ], width=4),
                dbc.Col([
                    html.H2("3", className="text-center"),
                    html.P("New Incidents (Last 15 min)", className="text-center text-muted")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.H2("TPE-09", className="text-center text-danger"),
                        html.P("High Accident Probability", className="text-center text-muted")
                    ])
                ], width=4)
            ])
        ])
    ])

def create_incident_list():
    """Create the incident list component"""
    return dbc.Card([
        dbc.CardHeader("Incidents"),
        dbc.CardBody([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Time"),
                        html.Th("Type & Severity"),
                        html.Th("Location"),
                        html.Th("Status")
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td("10:45 AM"),
                        html.Td("Multi-Vehicle Collision (Severity: High)"),
                        html.Td("PIE-04"),
                        html.Td(dbc.Badge("New", color="danger"))
                    ]),
                    html.Tr([
                        html.Td("10:36 AM"),
                        html.Td("Reckless Driving (Severity: Medium)"),
                        html.Td("TPE-09"),
                        html.Td(dbc.Badge("Alert Sent", color="warning"))
                    ]),
                    html.Tr([
                        html.Td("10:30 AM"),
                        html.Td("Vehicle Fire (Severity: High)"),
                        html.Td("OR-01"),
                        html.Td(dbc.Badge("Alert Sent", color="danger"))
                    ])

                ])
            ], bordered=True, hover=True)
        ])
    ])

def create_weather_advisory():
    """Create the weather advisory component"""
    return dbc.Card([
        dbc.CardHeader("Weather Advisory"),
        dbc.CardBody([
            html.Div([
                html.H4("⚠️ Heavy Rain Alert", className="text-warning"),
                html.P("West Zone experiencing heavy rainfall. Reduced visibility and slippery roads reported.")
            ])
        ])
    ])

def create_trend_chart():
    """Create the trend chart component"""
    # Sample data for the last 6 hours
    hours = [datetime.datetime.now() - datetime.timedelta(hours=i) for i in range(6, 0, -1)]
    incidents = [3, 2, 4, 1, 3, 5]  # Sample incident counts

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=incidents,
        mode='lines+markers',
        name='Critical Incidents',
        line=dict(color='#dc3545', width=2)
    ))

    fig.update_layout(
        title="Critical Incidents Trend (Last 6 Hours)",
        xaxis_title="Time",
        yaxis_title="Number of Incidents",
        template="plotly_white",
        height=300
    )

    return dbc.Card([
        dbc.CardHeader("Incident Trend"),
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    ])

def create_incident_breakdown():
    """Create the incident breakdown component"""
    # Sample data
    incident_types = ['Collisions', 'Fires', 'Obstructions']
    counts = [5, 3, 2]

    fig = go.Figure(data=[go.Pie(
        labels=incident_types,
        values=counts,
        hole=.3,
        marker_colors=['#dc3545', '#ffc107', '#0dcaf0']
    )])

    fig.update_layout(
        title="Incident Type Breakdown",
        template="plotly_white",
        height=270,
        margin=dict(l=20, r=20, t=50, b=20)  # Reduced margins for better space utilization
    )

    return dbc.Card([
        dbc.CardHeader("Incident Breakdown (Last hour)"),
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    ]) 