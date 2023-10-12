import dash
from dash import html, dcc, Output
from dash.dependencies import Input
import requests
import pandas as pd
import json

dash_app = dash.Dash(__name__)

def create_dashboard_layout():
    
    @dash_app.callback(Output('song-title', 'children'), Input('interval-component', 'n_intervals'))
    def update_song_title(_):
        base = 'http://127.0.0.1:5000/'
        link = "song/currentlyplaying/"
        headers = {}
        
        song_info = requests.get(base + link).json().get('song_name', 'Unknown Song')
        print(f'Song Info: {song_info}')
        return song_info

    @dash_app.callback(Output('artist-name', 'children'), Input('interval-component', 'n_intervals'))
    def update_artist_name(_):
        base = 'http://127.0.0.1:5000/'
        link = "song/currentlyplaying/"
        headers = {}
        
        artist_info = requests.get(base + link).json().get('artist_name', 'Unknown Song')
        print(f'Artist Info: {artist_info}')
        return artist_info
    
    def get_track_info():
        
        link = "http://127.0.0.1:5000/song/recent/"
        track_info = requests.get(link)
        track_info_json = json.dumps(track_info.json())

        df = pd.read_json(track_info_json)
        return df
    
    df = get_track_info()
    
    bar_chart = dcc.Graph(
        id='bar-chart',
        figure={
            'data': [
                {
                    'x': df['song_name'],  # X-axis data (e.g., song names)
                    'y': df['danceability'],  # Y-axis data (e.g., danceability scores)
                    'type': 'bar',
                    'marker': {'color': 'blue'}
                }
            ],
            'layout': {
                'title': 'Danceability of Recently Played Songs',
                'xaxis': {'title': 'Song Name'},
                'yaxis': {'title': 'Danceability Score'}
            }
        }
    )

    layout = html.Div([
        html.H1(id='song-title', children='Song Loading...', style={'textAlign':'center'}),
        html.P(id='artist-name', children='Artist Loading...', style={'textAlign':'center'}),
        bar_chart,
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
        
    ])
    
    return layout

dash_app.layout = html.Div(create_dashboard_layout())

if __name__ == "__main__":
    dash_app.run()