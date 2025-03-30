import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import json
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = dbc.Container([
    html.H2("SBUS Live Dashboard", className="mt-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-graph'), width=12)
    ]),
    dcc.Interval(id='interval', interval=200, n_intervals=0),
    html.Div(id='status', className="mt-2")
])

@app.callback(
    Output('bar-graph', 'figure'),
    Output('status', 'children'),

    Input('interval', 'n_intervals')
)
def update_graph(n):
    if os.path.exists("shared.json"):
        try:
            with open("shared.json", "r") as f:
                data = json.load(f)
            channels = data["channels"]
            lost = data["lost_frame"]
            failsafe = data["failsafe"]
        except:
            channels = [0] * 16
            lost = 0
            failsafe = 0
    else:
        channels = [0] * 16
        lost = 0
        failsafe = 0
    print(f"Data read from JSON: {channels}")  # <-- Tutaj

    fig = {
        'data': [{
            'x': list(range(1, 17)),
            'y': channels,
            'type': 'bar'
        }],
        'layout': {
            'yaxis': {'range': [0, 2000]},
            'title': 'SBUS Channels (1-16)'
        }
    }
    status = f"Lost Frame: {lost} | Failsafe: {failsafe}"
    return fig, status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)