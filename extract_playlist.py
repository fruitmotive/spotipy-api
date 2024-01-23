import numpy as np
import pandas as pd
import spotipy 
import sys
from spotipy.oauth2 import SpotifyOAuth

def extract_playlist(spotipyObject):

    feature_name = ['acousticness', 'danceability', 'energy', 
                    'instrumentalness', 'key', 'liveness', 
                    'loudness', 'mode', 'speechiness', 'tempo', 
                    'time_signature', 'valence']

    ids = np.array([])
    names = np.array([])
    batch_size = 100
    offset = 0

    while batch_size == 100:
        part = spotipyObject.playlist_tracks(playlist_id, offset=offset)
        batch = np.array([track['track']['id'] for track in part['items']])
        names_ = np.array([track['track']['name'] for track in part['items']])
        ids = np.append(ids, batch)
        names = np.append(names, names_)
        
        batch_size = len(part['items'])
        offset += 100

    playlist = []

    for id in ids:
        features = []
        track_features = spotipyObject.audio_features(id)[0]
        for key in feature_name:
            features.append(track_features[key])
        playlist.append(features)

    playlist = pd.DataFrame(columns=feature_name, data=playlist)
    playlist['id'] = ids
    playlist['names'] = names
        
    return playlist



        

    


    
