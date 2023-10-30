import dash
from dash import html, dcc, Output
from dash.dependencies import Input
import requests
import pandas as pd
import json

dash_app = dash.Dash(__name__)

def create_dashboard_layout():

    layout = html.Div([
        html.H1(id='song-title', children='Song Title Loading...'),
        dcc.Graph(id='graph-with-five-songs'),
        dcc.Store(id='currently-playing'),
        dcc.Store(id='currently-playing-tempo'),
        dcc.Store(id='update-graph'),
        dcc.Interval(id='song-interval-component', interval=5000, n_intervals=0),
        dcc.Interval(id='current-song-interval-component', interval = 1000, n_intervals=0),
    ])

    @dash_app.callback(Output('song-title', 'children'), Input('currently-playing', 'data'), Input('song-interval-component', 'n_intervals'))
    def update_song_title(currently_playing, other):
        if currently_playing:
            song_name = currently_playing['song_name']
            print(f'Other: {str(other)}')
            return song_name
        else:
            return str('Nothing is currently Playing')


    @dash_app.callback(Output('currently-playing', 'data'), Input('current-song-interval-component', 'n_intervals'))
    def get_currently_playing(_):
        link = "http://127.0.0.1:5000/song/currentlyplaying/"
        track_info = requests.get(link)
        return track_info.json()

    @dash_app.callback(Output('currently-playing-tempo', 'data'), Input('currently-playing', 'n_intervals'))
    def set_tempo(currently_playing):
        if currently_playing:
            song_tempo = currently_playing['tempo']
            note_durations = {
                'sixteenth_note_duration' : song_tempo / 15,
                'eighth_note_duration' : song_tempo / 30,
                'quarter_note_duration' : song_tempo / 60,
                'half_note_duration' : song_tempo / 120,
                'whole_note_duration' : song_tempo / 240,
            }

            note_duration = note_durations['quarter_note_duration']

            return int(note_duration)

    @dash_app.callback(Output('update-graph', 'interval'), Input('currently-playing-tempo', 'data'))
    def set_update_interval(tempo):
        if tempo is not None:
            interval = int(tempo)  # Convert tempo to milliseconds
        else:
            interval = 5000  # Default interval if tempo is not available
        return interval

    @dash_app.callback(Output('graph-with-five-songs', 'figure'), Input('update-graph', 'n_intervals'))
    def update_figure(_):
        
        link = "http://127.0.0.1:5000/song/recent/"
        track_info = requests.get(link)
        track_info_json = json.dumps(track_info.json())
        df = pd.read_json(track_info_json)
        
        figure = {
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

        return figure

    return layout

dash_app.layout = html.Div(create_dashboard_layout())

if __name__ == "__main__":
    dash_app.run(debug=True)