import csv
import copy
import sys 
import time 
import spotipy 
from requests.exceptions import ReadTimeout
from spotipy.oauth2 import SpotifyOAuth
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


class current_session():

    @staticmethod
    def print_current_track(curr_track):
        artists = [artist['name'] for artist in curr_track['item']['artists']] 
        curr_artist_name = ', '.join(artists)
        curr_track_name = curr_track['item']['name']
        curr_time = time.ctime(time.time())
        print(f'{curr_time} {curr_artist_name} - {curr_track_name} is currently playing')


    def __init__(self, authorization_data):
        self.OAuthObject = SpotifyOAuth(**authorization_data)
        self.spotipyObject = spotipy.Spotify(oauth_manager=self.OAuthObject)

        # SET OF FEATURES TO BE PRINTED IN history.csv FILE
        self.labels = ['track_id', 'track_name', 'track_duration', 
                       'track_progress_ms', 'track_progress_ratio', 
                       'track_timestamp', 'album_name', 'album_id',
                       'album_release_date', 'artist_name', 'artist_id', 
                       'acousticness', 'danceability', 'energy', 
                       'instrumentalness', 'key', 'liveness', 
                       'loudness', 'mode', 'speechiness', 'tempo', 
                       'time_signature', 'valence']
        
    def get_prev_playback(self, prev_track):
        try:
            prev_playback = {}

            # TRACK INFO
            prev_playback['track_id'] = prev_track['item']['id']
            prev_playback['track_name'] = prev_track['item']['name']
            prev_playback['track_duration'] = prev_track['item']['duration_ms']
            prev_playback['track_progress_ms'] = prev_track['progress_ms']
            prev_playback['track_progress_ratio'] = prev_playback['track_progress_ms'] \
                                                    / prev_playback['track_duration']
            prev_playback['track_timestamp'] = time.time() \
                                               - prev_playback['track_progress_ms']

            # ALBUM INFO
            prev_playback['album_name'] = prev_track['item']['album']['name']
            prev_playback['album_id'] = prev_track['item']['album']['id']
            prev_playback['album_release_date'] = prev_track['item']['album']['release_date']

            # ARTIST INFO
            artists = [artist['name'] for artist in prev_track['item']['artists']]
            prev_playback['artist_name'] = ', '.join(artists)
            artists_id = [artist['id'] for artist in prev_track['item']['artists']]
            prev_playback['artist_id'] = ', '.join(artists_id)

            # AUDIO FEATURES
            track_features = self.spotipyObject.audio_features(prev_track['item']['id'])[0]
            for key, value in track_features.items():
                if key not in ['analysis_url', 'duration_ms', 'id', 
                               'track_href', 'type', 'uri']:
                    prev_playback[key] = value

            return prev_playback

        except:
            return None
        
    def current_session(self):
        try:
            prev_track = {'item': {'id': None}}

            while True:  
                time.sleep(1)

                try:
                    access_token = self.OAuthObject.get_access_token()
                    if access_token['expires_at'] - time.time() < 600:
                        self.OAuthObject.refresh_access_token(access_token['refresh_token'])
                        self.spotipyObject = spotipy.Spotify(oauth_manager=self.OAuthObject)

                    curr_track = self.spotipyObject.current_user_playing_track()
                
                except ReadTimeout:       
                    print('Internet is not available!')
                    time.sleep(60)
                    continue

                if curr_track is None or curr_track['item'] is None:
                    continue
                
                elif prev_track['item']['id'] != curr_track['item']['id']:
                    to_be_printed = self.get_prev_playback(prev_track)
                    self.print_current_track(curr_track)
                    try:
                        with open('history.csv', 'a', encoding='UTF8', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=self.labels, delimiter=';')
                            writer.writerow(to_be_printed)
                            f.close()
                    except:
                        pass

                prev_track = copy.deepcopy(curr_track)

        except KeyboardInterrupt:
            print('Thanks for using!') 



