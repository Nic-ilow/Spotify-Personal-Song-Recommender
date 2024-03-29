import requests
import pandas as pd
import json
import random


def get_tracks(headers, playlist_share_link):
    # Set up the API endpoint URL
    playlist_id = playlist_share_link.split('/')[-1].split('=')[0]

    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}"

    # Make the API request
    response = requests.get(endpoint, headers=headers)

    # Convert the response to a JSON object
    track_data = json.loads(response.content)

    return track_data

def get_playlist_info(track_data, headers):
    # Grab track popularities. Get id's to sanity check

    all_track_ids = []
    all_track_popularities = []
    for track in track_data['tracks']['items']:
        all_track_ids.append(track['track']['id'])
        all_track_popularities.append(track['track']['popularity'])
    all_track_ids_string = (',').join(all_track_ids)
    audiofeatures_endpoint = f'https://api.spotify.com/v1/audio-features?ids={all_track_ids_string}'

    response = requests.get(audiofeatures_endpoint, headers=headers)
    audio_features = response.json()['audio_features']

    playlist_info = pd.DataFrame(audio_features)
    playlist_info['popularity'] = all_track_popularities

    return playlist_info

def generate_rec_endpoint(playlist_info, user_inputs, use_means, seed_by_popularity = False):
    if use_means:
        mean_dict = {}
        mean_dict['target_danceability'] = playlist_info.danceability.mean()
        mean_dict['target_energy'] = playlist_info.energy.mean()
        mean_dict['target_speechiness'] = playlist_info.speechiness.mean()
        mean_dict['target_acousticness'] = playlist_info.acousticness.mean()
        mean_dict['target_tempo'] = playlist_info.tempo.mean()
        mean_dict['target_valence'] = playlist_info.valence.mean()

    if seed_by_popularity:
        mean_popularity = playlist_info.popularity.mean()
        seed_songs = playlist_info.id.iloc[(playlist_info.popularity-mean_popularity).abs().argsort()[:5]].to_list()
    else:
        seed_songs = playlist_info.id.iloc[random.sample(range(0, len(playlist_info)), 5)]

    seed_song_str = 'seed_tracks='
    for song_id in seed_songs:
        seed_song_str += song_id + '&'

    ep_string = ''
    if not use_means:
        for key, val in user_inputs.items():
            ep_string += (key + '=' + str(val) + '&')
    else:
        for key, val in mean_dict.items():
            ep_string += (key + '=' + str(val) + '&')

    ep_string = ep_string[:-1]

    rec_endpoint = f'https://api.spotify.com/v1/recommendations?limit=5&{seed_song_str}{ep_string}'

    return rec_endpoint

def get_recs(rec_endpoint, headers):
    recs = requests.get(rec_endpoint, headers=headers).json()

    filtered_dicts = []
    for track in recs['tracks']:
        artists = []
        for artist in track['artists']:
            artists.append(artist['name'])
        filtered = {}
        filtered['name'] = track['name']
        filtered['artist'] = ', '.join(artists)
        filtered['preview_url'] = track['preview_url']
        filtered['song_url'] = track['external_urls']['spotify']
        filtered_dicts.append(filtered)

        results = pd.DataFrame(filtered_dicts)

        return results

def main(access_token, playlist_share_link, user_inputs):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    track_data = get_tracks(headers, playlist_share_link)
    playlist_info = get_playlist_info(track_data, headers)
    rec_endpoint = generate_rec_endpoint(playlist_info, user_inputs, use_means=False)
    recs = get_recs(rec_endpoint, headers)

    return recs
