import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State

# components
button = html.Button("Run", id="run-button", className="btn btn-outline-primary")
output = html.Div(id="output")
# layout
app = dash.Dash(__name__)
app.layout = html.Div([button, output])
# callbacks
@app.callback(Output("output", "children"), [Input("run-button", "n_clicks")])
def click_button(n_clicks):
    if n_clicks:
        return f"Clicked {n_clicks} {'time!' if n_clicks == 1 else 'times!'}"
    return "Not Clicked"


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
