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
        
        request = requests.get(base + link).json()
        song_name = request['song_name']
        # print(f'Song Info: {song_info}')
        return song_name

    @dash_app.callback(Output('artist-name', 'children'), Input('interval-component', 'n_intervals'))
    def update_artist_name(_):
        base = 'http://127.0.0.1:5000/'
        link = "song/currentlyplaying/"
        headers = {}
        
        artist_info = requests.get(base + link).json().get('artist_name', 'Unknown Song')
        print(f'Artist Info: {artist_info}')
        return artist_info
    
    @dash_app.callback(Output('album-name', 'children'), Input('interval-component', 'n_intervals'))
    def update_artist_name(_):
        base = 'http://127.0.0.1:5000/'
        link = "song/currentlyplaying/"
        headers = {}
        
        album_info = requests.get(base + link).json().get('album_name', 'Unknown Song')
        print(f'Album Info: {album_info}')
        return album_info
    
    # @dash_app.callback(Output('tempo-store', 'data'), Input('interval-component', 'n_intervals'))
    # def get_song_tempo(_):
    #     base = 'http://127.0.0.1:5000/'
    #     link = "song/currentlyplaying/"
    #     request = requests.get(base + link).json()
    #     song_tempo = request['tempo']

    #     note_durations = {
    #         'sixteenth_note_duration' : song_tempo / 15,
    #         'eighth_note_duration' : song_tempo / 30,
    #         'quarter_note_duration' : song_tempo / 60,
    #         'half_note_duration' : song_tempo / 120,
    #         'whole_note_duration' : song_tempo / 240,
    #     }

    #     return {'tempo': song_tempo}, note_durations, song_tempo

    layout = html.Div([
        html.H1(id='song-title', children='Song Loading.', style={'textAlign':'center'}),
        html.P(id='artist-name', children='Artist Loading...', style={'textAlign':'center'}),
        html.P(id='album-name', children='Album Loading...', style={'textAlign':'center'}),
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
    ])
        # dcc.Graph(id='graph-with-five-songs'),
        # dcc.Interval(id='song-interval-component', interval = 5000, n_intervals=0),
        # dcc.Store(id='tempo-store', data={'tempo': 2})
    
    # @dash_app.callback(Output('graph-with-five-songs', 'figure'), Input('song-interval-component', 'song_intervals'), Input('tempo-store', 'data'))
    # def update_figure(n, tempo_data):
    
    #     song_tempo = tempo_data['tempo']
    #     interval_time = 60000 / song_tempo

    #     link = "http://127.0.0.1:5000/song/recent/"
    #     track_info = requests.get(link)
    #     track_info_json = json.dumps(track_info.json())
    #     df = pd.read_json(track_info_json)
        
        
    #     figure = {
    #         'data': [
    #             {
    #                 'x': df['song_name'],  # X-axis data (e.g., song names)
    #                 'y': df['danceability'],  # Y-axis data (e.g., danceability scores)
    #                 'type': 'bar',
    #                 'marker': {'color': 'blue'}
    #             }
    #         ],
    #         'layout': {
    #             'title': 'Danceability of Recently Played Songs',
    #             'xaxis': {'title': 'Song Name'},
    #             'yaxis': {'title': 'Danceability Score'}
    #         }
    #     }

    #     return figure, dcc.Interval(interval=interval_time, id='song-interval-component')

    # return layout

dash_app.layout = html.Div(create_dashboard_layout())

if __name__ == "__main__":
    dash_app.run(debug=True)