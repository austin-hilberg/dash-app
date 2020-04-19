import base64
import datetime as dt
from io import BytesIO

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

# import non-app-specific project functions here
# from project_template import count_timebin_posts

# from ds_utils import (
#     date_window,
#     from_date_string,
#     get_conversation_posts,
#     get_conversations,
#     get_faction_conversation_posts,
#     get_factions,
#     get_logger,
#     make_query,
# )


# """""""""""""""""""""""""""""""""" Initialization """""""""""""""""""""""""""""""""""
# log = get_logger(__name__)
plt.style.use("seaborn-whitegrid")
# default_start_date, default_end_date = date_window(time_delta="1d")
# default_conversation = 532
# conversation_id_to_name = get_conversations()
# faction_id_to_name = get_factions()
conversation_id_to_name = {0: "A", 1: "B", 2: "C"}
default_start_date = pd.Timestamp("2020-03-01")
default_end_date = pd.Timestamp("2020-03-02")
default_conversation = 0
# """""""""""""""""""""""""""""""""" App Boilerplate """""""""""""""""""""""""""""""""""
external_scripts = [
    dict(
        src="https://code.jquery.com/jquery-3.3.1.slim.min.js",
        integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo",
        crossorigin="anonymous",
    ),
    dict(
        src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js",
        integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1",
        crossorigin="anonymous",
    ),
    dict(
        src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js",
        integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM",
        crossorigin="anonymous",
    ),
]
# external CSS stylesheets
external_stylesheets = [
    dict(
        rel="stylesheet",
        href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
        integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T",
        crossorigin="anonymous",
    ),
    dict(
        rel="stylesheet",
        href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
        integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T",
        crossorigin="anonymous",
    ),
]
app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
)
server = app.server  # expose for wsgi
# A hidden div where data can be stored and passed between callbacks
data_store = html.Div(id="data-store", style={"display": "none"})
# """"""""""""""""""""""""""""""" Custom App Functions """"""""""""""""""""""""""""""""
def fig_to_uri(fig, close_all=True, **save_args):
    """ encode a matplotlib figure as a URI """
    out_img = BytesIO()
    fig.savefig(out_img, format="png", **save_args)
    if close_all:
        fig.clf()
        plt.close("all")
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


# """""""""""""""""" Dash Components (to be arranged in the layout) """""""""""""""""""
# """""""""""""""""""""""""""""""""" Input Components """"""""""""""""""""""""""""""""""
# conversation dropdown
conversation_options = [
    dict(label=conv_name, value=conv_id)
    for conv_id, conv_name in conversation_id_to_name.items()
]
conversation_dropdown = dcc.Dropdown(
    id="conversation-dropdown",
    options=conversation_options,
    className="f-row",
    value=default_conversation,
    # multi=True,
)
conversation_dropdown_card = html.Div(
    [html.Div("Conversations:", className="f-row f-label"), conversation_dropdown],
    id="conversation-dropdown-row",
    className="f-column card",
)
date_range = dcc.DatePickerRange(
    id="date-range",
    min_date_allowed=dt.datetime(2019, 1, 1),
    max_date_allowed=dt.datetime(2022, 1, 1),
    start_date=default_start_date,
    end_date=default_end_date,
)
date_range_card = html.Div(
    [html.Div("Date Range:", className="f-row f-label"), date_range],
    className="f-column card",
    id="date-range-row",
)
run_button = html.Div(
    html.Button("Run", id="run-button", className="btn btn-outline-primary"),
    className="f-row",
)
run_button_card = html.Div(run_button, id="run-button-card", className="f-row card")
# """""""""""""""""""""""""""""""""" Output Components """"""""""""""""""""""""""""""""
mpl_figure = html.Img(id="mpl-figure")
# Loading object creates loading animation while output is being computed
mpl_figure_loading = dcc.Loading(mpl_figure, id="mpl-figure-loading", type="circle")
mpl_figure_card = html.Div(
    mpl_figure_loading, id="mpl-figure-card", className="f-row card"
)
plotly_figure = dcc.Graph(
    id="plotly-figure"
)  # generic container for plotly figure/chart
plotly_figure_loading = dcc.Loading(
    plotly_figure, id="plotly-figure-loading", type="circle"
)
plotly_figure_card = html.Div(
    plotly_figure_loading, id="plotly-figure-card", className="f-row card"
)
# """""""""""""""""""""""""""""""""" Component Layout """"""""""""""""""""""""""""""""""
input_row = html.Div(
    [date_range_card, run_button_card], id="input-row", className="f-row"
)
app.layout = html.Div(
    [conversation_dropdown_card, input_row, plotly_figure_loading, mpl_figure_loading],
    id="app-container",
    className="flex-container",
)
# """"""""""""""""""""""""""""""""""""" Callbacks """"""""""""""""""""""""""""""""""""""
# @app.callback(
#     Output("mpl-figure", "src"),
#     [Input("run-button", "n_clicks")],
#     [
#         State("date-range", "start_date"),
#         State("date-range", "end_date"),
#         State("conversation-dropdown", "value"),
#     ],
# )
# def fill_mpl_figure(n_clicks, start_date, end_date, conversation_id):
#     if not n_clicks:
#         print("returning initial empty figure")
#         f = plt.figure()
#         plt.title("Empty Figure")
#         return fig_to_uri(f)
#     post_counts = count_timebin_posts(start_date, end_date, conversation_id)
#     if post_counts is None:
#         f = plt.figure()
#         plt.title("Results Empty")
#         return fig_to_uri(f)
#     print("plotting post volume figure")
#     fig = plt.figure()
#     ax = fig.gca()
#     ax.plot(post_counts.time_bin.values, post_counts.n_posts)
#     plt.xticks(rotation=70)
#     plt.title(f"{conversation_id_to_name[conversation_id]} Conversation Post Volume")
#     plt.tight_layout()
#     return fig_to_uri(fig)


@app.callback(
    Output("plotly-figure", "figure"),
    [Input("run-button", "n_clicks")],
    [
        State("date-range", "start_date"),
        State("date-range", "end_date"),
        State("conversation-dropdown", "value"),
    ],
)
def fill_plotly_figure(n_clicks, start_date, end_date, conversation_id):
    if not n_clicks:
        return {}  # 'figure' object is dict-like, can return empty dict for no-op
    # post_counts = count_timebin_posts(start_date, end_date, conversation_id)
    n_bins = 10
    post_counts = pd.DataFrame(
        dict(
            n_posts=np.random.randint(0, 1000, size=n_bins),
            time_bin=pd.date_range(start_date, end_date, n_bins),
        )
    )
    fig = px.line(
        post_counts,
        x="time_bin",
        y="n_posts",
        title=f"{conversation_id_to_name[conversation_id]} Conversation Post Volume",
    )
    # remove margins
    # fig.update_layout(margin=dict(l=0, r=0, t=0, b=0, pad=0))
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
