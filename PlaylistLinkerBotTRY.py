import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 🔐 Встав сюди свої ключі
CLIENT_ID = '825c28758767439abe9ce4d498848150'
CLIENT_SECRET = '4a8b70ff1e2e475dbbfe2f0a1c9821b5'

# Аутентифікація
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_track_urls_from_playlist(playlist_url):
    # Отримуємо ID плейлиста зі ссилки
    playlist_id = playlist_url.split("/")[-1].split("?")[0]

    # Отримуємо треки
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']

    # Якщо плейлист довгий — витягуємо все
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    # Витягуємо ссилки на треки
    track_urls = []
    for i, item in enumerate(tracks, start=1):
        track = item['track']
        if track:
            track_urls.append(f"{i}. {track['external_urls']['spotify']}")

    return track_urls


# 🧪 Тест
if __name__ == "__main__":
    url = input("Введи посилання на плейлист: ")
    links = get_track_urls_from_playlist(url)
    print("\n".join(links))
