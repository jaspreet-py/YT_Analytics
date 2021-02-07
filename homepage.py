# Importing the required libraries
import requests, json, os, dash
import plotly.express as px
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL

# Importing all the functions made for fetching and transforming data
# into our main app.py file
from functions import (
    get_related_channels,
    get_channel_subs,
    get_channel_stats,
    get_vid_ids,
    get_vid_stats,
    get_year_stats,
)

# Fetching the secret API key from environment variables
# api_key = os.environ.get("YT_apikey")
api_key = "AIzaSyAwYxFLzjKRKUfqzq-4zGKApyHtd5c8KJU"


# Main Header for the App
header = html.Div(
    children=[
        html.Img(
            src="https://www.youtube.com/about/static/svgs/icons/brand-resources/YouTube_icon_full-color.svg?cache=f2ec7a5",
            height="20%",
            width="20%",
            style={
                "align-items": "center",
                "justify-content": "center",
            },
            className="header-emoji",
        ),
        html.H1(
            children="Youtube Channel Statistics",
            className="header-title",
        ),
        html.P(
            children="""Search for any Youtube Channel and get some
        Cool Statistics about it!""",
            className="header-description",
        ),
    ],
    className="header",
)


# Search Box where the User will input the Channel Name
search = html.Div(
    children=[
        html.Div(
            children=[
                dcc.Input(
                    id="user_input",
                    placeholder="Please Enter a Youtube Channel Name",
                    debounce=True,
                    type="text",
                    style={
                        "height": "35px",
                        "width": "650px",
                        "background-color": "lightgray",
                        "color": "black",
                        "font-size": "100%",
                        "border-radius": "5px",
                    },
                ),
            ],
        )
    ],
    className="search",
)


# Populate Channels based on the Search Query by the User
show_channels = html.Div(id="related_channels", style={"diplay": "flex"})

final_div = html.Div(id="final", style={"color": "white"})

# Loading in an external stylesheet to change the font of the App
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato",
        "rel": "stylesheet",
    },
]


# Creating a Dash App Instance and Changing it's Title
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
)
app.title = "Search Box"

# Forming the layout for the App
app.layout = html.Div(children=[header, search, show_channels, final_div])

# Defining a callback to ...
@app.callback(
    Output("related_channels", "children"),
    [
        Input(
            "user_input",
            "value",
        )
    ],
    # [State("user_input", "value")],
    # prevent_initial_call=True,
)

# Defining a function to show related channels to the User on the basis of the Search Query
def show_related_channels(input_value):
    # Fetching releated channels using the Youtube API and storing the data in a Dictionary
    channels_dict = get_related_channels(input_value)

    # Checking if the reponse from the function is a String, which indicates that it ran into
    # some error and will print out the error message
    if isinstance(channels_dict, str):
        children = [
            html.Div(
                html.H2(channels_dict),
                style={
                    "display": "flex",
                    "justify-content": "center",
                    "margin-top": "5%",
                    "color": "white",
                },
            )
        ]
    else:
        children = [
            html.Div(
                children=[
                    html.Img(
                        src=channels_dict[channel]["thumbnail"],
                        height="70px",
                        width="70px",
                        alt="avatar",
                        style={"border-radius": "50%"},
                    ),
                    html.Button(
                        # id=f"{channels_dict[channel]['channel_id']}",
                        id={
                            "type": "channel_button",
                            "index": f"{channels_dict[channel]['channel_id']}",
                        },
                        n_clicks=0,
                        children=[
                            html.H2(
                                children=[
                                    channel,
                                    html.P(
                                        f"{get_channel_subs(channels_dict[channel]['channel_id'])}",
                                        style={"margin-top": "1%"},
                                    ),
                                ],
                                # className = "channel_name"
                            ),
                        ],
                        # style={
                        #     "background": "none",
                        #     # "border-style": "none",
                        #     "color": "white",
                        # },
                        className="box",
                    ),
                ],
                style={
                    "padding-bottom": "2%",
                    "align-items": "center",
                    "display": "flex",
                    "padding-left": "2%",
                },
            )
            for channel in channels_dict
        ]
        # style = {"display": "block"}

    return children


# y = Output("related_channels", "style")


@app.callback(
    [Output("final", "children"), Output("related_channels", "style")],
    [Input({"type": "channel_button", "index": ALL}, "n_clicks")],
)
def update_final(clicks):
    ctx = dash.callback_context

    # print(clicks)

    # If conditional so that the function does not trigger without a click
    if not ctx.triggered or not ctx.triggered[0]["value"]:
        pass
    else:
        style = {"display": "none"}
        # print(clicks)
        # style = {"display": "none"}

        # A temporary variable containg the json string which contains the channel ID
        x = ctx.triggered[0]["prop_id"]
        x = x.replace(".n_clicks", "")
        # print(x)

        # Saving the channel ID that the user clicked on
        channel_id = json.loads(x)
        channel_id = channel_id["index"]
        # print(channel_id)

        # get basic channel statistics and storing them in separate variables
        (
            channel_upload_id,
            channel_title,
            channel_description,
            channel_thumb_url,
            channel_views,
            channel_subs,
            channel_vid_count,
        ) = get_channel_stats(channel_id)

        # formatting the numbers to include commas for better readability
        channel_views = f"{channel_views:,}"
        channel_subs = f"{channel_subs:,}"
        channel_vid_count = f"{channel_vid_count:,}"

        # get all the unique IDs related to all the videos of the channel and store
        # the data in a list
        channel_vid_ids = get_vid_ids(channel_upload_id)

        # A final list of dicts containg the data about all the videos associated with
        # a channel and storing it in a list, to further transform it into a pandas
        # DataFrame to help visualize the data
        df_list = get_vid_stats(channel_vid_ids)

        # Setting up Column names for our DataFrame
        df_column_names = [
            "Title",
            "Uploaded On",
            "Views",
            "Likes",
            "Dislikes",
            "Comments",
        ]

        # Converting the Data gathered in our {df_list} list into a DataFrame
        df = pd.DataFrame(data=df_list, columns=df_column_names)

        # Getting the top 10 videos by views from the {df}
        top_10_df = df.sort_values(by="Views", ascending=False).iloc[:10]

        # Getting the top 10 videos by likes from the {df}
        most_liked_df = df.sort_values(by="Likes", ascending=False).iloc[:10]

        yearly_stats = get_year_stats(df)

        channel_likes = df["Likes"].sum()
        channel_comments = df["Comments"].sum()
        channel_avg_views = int(df["Views"].mean().round())
        channel_avg_likes = int(df["Likes"].mean().round())

        # Formatting the numbers to include commas for better readability
        channel_likes = f"{channel_likes:,}"
        channel_comments = f"{channel_comments:,}"
        channel_avg_views = f"{channel_avg_views:,}"
        channel_avg_likes = f"{channel_avg_likes:,}"

        row = html.Div(
            children=[
                html.Div(
                    children=[
                        html.Img(
                            src=channel_thumb_url,
                            height="20%",
                            width="20%",
                            alt="avatar",
                            style={"border-radius": "50%"},
                        ),
                        html.H1(
                            f"{channel_title}",
                            style={
                                "color": "red",
                                "margin": "1px",
                                "font-weight": "bold",
                            },
                        ),
                        html.H3(
                            f"{channel_subs} Subscribers",
                            style={
                                "margin": "1px",
                                "font-weight": "normal",
                                "color": "white",
                            },
                        ),
                        html.P(
                            f"{channel_description}",
                            style={
                                "font-weight": "normal",
                                "font-style": "oblique",
                                "margin-top": "30px",
                                "color": "lightblue",
                            },
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "width": "29%",
                        "padding-left": "1%",
                    },
                ),
                html.Div(
                    f"""
            {channel_views} Views

            {channel_likes} Likes

            {channel_comments} Comments
                        """,
                    style={
                        "text-align": "right",
                        "display": "inline-block",
                        "width": "69%",
                        "vertical-align": "initial",
                        "padding-right": "1%",
                        "color": "lightblue",
                    },
                ),
            ],
            style={
                "white-space": "pre-wrap",
                "font-size": "18px",
                "font-weight": "bold",
                # "background": "rgba(121, 118, 118, 0.9)",
            },
        )

        most_viewed_graph = dcc.Graph(
            config={"displayModeBar": False},
            figure={
                "data": [
                    {
                        # "x": top_10_df["Title"],
                        "x": [title[:30] + " ..." for title in top_10_df["Title"]],
                        "y": top_10_df["Views"],
                        "type": "bar",
                        "marker": {"color": px.colors.sequential.Viridis},
                    }
                ],
                "layout": {
                    "title": {
                        "text": "Most Viewed Videos",
                        "x": 0.05,
                        "xanchor": "left",
                    },
                    "xaxis": {"fixedrange": True, "automargin": True, "color": "white"},
                    "yaxis": {"showgrid": False, "color": "white"},
                    "color": "Views",
                    "height": "50%",
                    "width": "50%",
                    "float": "left",
                    "paper_bgcolor": "black",
                    "plot_bgcolor": "black",
                    "font": {"color": "white"},
                },
            },
        )

        most_liked_graph = dcc.Graph(
            config={"displayModeBar": False},
            figure={
                "data": [
                    {
                        "x": [title[:30] + " ..." for title in most_liked_df["Title"]],
                        "y": most_liked_df["Likes"],
                        "type": "bar",
                        "marker": {"color": px.colors.sequential.Viridis},
                    }
                ],
                "layout": {
                    "title": {
                        "text": "Most Liked Videos",
                        "x": 0.05,
                        "xanchor": "left",
                    },
                    "xaxis": {"fixedrange": True, "automargin": True, "color": "white"},
                    "yaxis": {"showgrid": False, "color": "white"},
                    "height": "50%",
                    "width": "50%",
                    "paper_bgcolor": "black",
                    "plot_bgcolor": "black",
                    "font": {"color": "white"},
                },
            },
        )

        uploads_per_year_graph = dcc.Graph(
            config={"displayModeBar": False},
            figure={
                "data": [
                    {
                        "x": [key for key in yearly_stats],
                        "y": [
                            yearly_stats[key]["Number of Uploads"]
                            for key in yearly_stats
                        ],
                        "type": "line",
                        "marker": {"color": px.colors.sequential.Agsunset},
                    }
                ],
                "layout": {
                    "title": {
                        "text": "Number of Uploads per Year",
                        "x": 0.05,
                        "xanchor": "left",
                    },
                    "xaxis": {"showgrid": False, "automargin": True, "color": "white"},
                    "yaxis": {"showgrid": False, "color": "white"},
                    "height": "50%",
                    "width": "auto",
                    "plot_bgcolor": "black",
                    "paper_bgcolor": "black",
                    "font": {"color": "white"},
                },
            },
        )

        children = [
            row,
            html.Div(
                children=[
                    html.Div(
                        children=most_viewed_graph,
                        className="card",
                        style={
                            "width": "50%",
                            "margin": "auto",
                            "display": "inline-flex",
                            "align-items": "left",
                            "justify-content": "left",
                        },
                    ),
                    html.Div(
                        children=[
                            html.P(
                                f"{channel_vid_count} Videos",
                                style={"font-size": "44px"},
                            ),
                            html.P(
                                f"{channel_avg_views} Average Views per Video",
                                style={"font-size": "24px"},
                            ),
                            html.P(
                                f"{channel_avg_likes} Average Likes per Video",
                                style={"font-size": "24px"},
                            ),
                        ],
                        style={
                            "color": "white",
                            "width": "50%",
                            "height": "inherit",
                            "display": "inline-flex",
                            "align-items": "center",
                            "justify-content": "center",
                            "flex-direction": "column",
                        },
                    ),
                ],
                style={"display": "flex"},
            ),
            html.Div(
                children=[
                    html.Div(
                        children=uploads_per_year_graph,
                        className="card",
                        style={
                            "width": "50%",
                            # "margin": "auto",
                            "display": "inline-flex",
                            "float": "left",
                            "align-items": "left",
                            "justify-content": "left",
                        },
                    ),
                    html.Div(
                        children=most_liked_graph,
                        className="card",
                        style={
                            "width": "50%",
                            # "margin": "auto",
                            "display": "inline-flex",
                            "float": "right",
                            "align-items": "right",
                            "justify-content": "right",
                        },
                    ),
                ],
                style={"display": "flex"},
            ),
        ]

        return children, style


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
