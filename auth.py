import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for, jsonify, Blueprint
from dotenv import load_dotenv
from db import get_db_connection  # Import database connection function


auth_bp = Blueprint("auth", __name__)  # Define Blueprint for auth routes


# Load environment variables
env_path = os.path.abspath("proj.env")
load_dotenv(env_path)


# Spotify Authentication Setup
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-library-read user-top-read user-read-recently-played playlist-modify-public playlist-modify-private"
)

def get_spotify_client():
    """Retrieve an authenticated Spotipy client."""
    token_info = session.get("token_info", None)
    if not token_info:
        return None
    
    sp = spotipy.Spotify(auth=token_info["access_token"])
    return sp

@auth_bp.route("/")
def login():
    """Redirect user to Spotify for authentication."""
    session.pop("token_info", None)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@auth_bp.route("/callback")
def callback():
    """Handle the callback from Spotify after login."""
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info

    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_info = sp.current_user()

    # Store user in the database
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (spotify_id, display_name, profile_image)
        VALUES (%s, %s, %s)
        ON CONFLICT (spotify_id) DO NOTHING
        """,
        (user_info["id"], user_info["display_name"], user_info["images"][0]["url"] if user_info["images"] else None)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("routes.get_user_profile"))

@auth_bp.route("/debug-token")
def debug_token():
    """Debugging function to check if token is stored."""
    sp = get_spotify_client()
    if not sp:
        return "No token found, please re-authenticate."

    token_info = session.get("token_info")
    return jsonify(token_info)








































# import os
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# from flask import Flask, request, redirect, session, url_for, jsonify
# from dotenv import load_dotenv
# from db import get_db_connection  # Import the database connection function
# import psycopg2
# from psycopg2.extras import execute_values
# from collections import Counter

# # Load environment variables
# env_path = os.path.abspath("proj.env")
# load_dotenv(env_path)

# # Flask App Configuration
# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")
# app.config["SESSION_COOKIE_NAME"] = "Spotify Login Session"

# # Spotify Authentication Setup
# sp_oauth = SpotifyOAuth(
#     client_id=os.getenv("SPOTIPY_CLIENT_ID"),
#     client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
#     redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
#     scope="user-library-read user-top-read user-read-recently-played playlist-modify-public playlist-modify-private"
# )

# def get_spotify_client():
#     """Retrieve an authenticated Spotipy client."""
#     token_info = session.get("token_info", None)
#     if not token_info:
#         return None
    
#     sp = spotipy.Spotify(auth=token_info["access_token"])
#     return sp

# @app.route("/")
# def login():
#     """Redirect user to Spotify for authentication."""
#     session.pop("token_info", None)
#     auth_url = sp_oauth.get_authorize_url()
#     return redirect(auth_url)

# @app.route("/callback")
# def callback():
#     """Handle the callback from Spotify after login."""
#     session.clear()
#     code = request.args.get("code")
#     token_info = sp_oauth.get_access_token(code)
#     session["token_info"] = token_info

#     sp = spotipy.Spotify(auth=token_info["access_token"])
#     user_info = sp.current_user()

#     # Store user in the database
#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         INSERT INTO users (spotify_id, display_name, profile_image)
#         VALUES (%s, %s, %s)
#         ON CONFLICT (spotify_id) DO NOTHING
#         """,
#         (user_info["id"], user_info["display_name"], user_info["images"][0]["url"] if user_info["images"] else None)
#     )

#     conn.commit()
#     cur.close()
#     conn.close()

#     return redirect(url_for("get_user_profile"))




# @app.route("/user-profile")
# def get_user_profile():
#     """Fetch user profile details."""
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))
    
#     user_info = sp.current_user()
    
#     return jsonify({
#         "id": user_info["id"],
#         "display_name": user_info["display_name"],
#         "email": user_info.get("email", "N/A"),
#         "profile_url": user_info["external_urls"]["spotify"],
#         "image": user_info["images"][0]["url"] if user_info["images"] else None
#     })


# @app.route("/user-top-artists")
# def get_top_artists():
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))

#     user_id = sp.current_user()["id"]
    
#     # Fetch user_id from DB
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM users WHERE spotify_id = %s", (user_id,))
#     result = cur.fetchone()

#     if not result:
#         return jsonify({"error": "User not found in database"}), 400

#     db_user_id = result[0]

#     # Fetch and store top artists
#     user_top_artists = sp.current_user_top_artists(limit=10)["items"]
#     artists_data = [
#         (db_user_id, artist["name"], artist["id"], artist["popularity"], artist["followers"]["total"],
#          artist["external_urls"]["spotify"], artist["images"][0]["url"] if artist["images"] else None)
#         for artist in user_top_artists
#     ]

#     cur.execute("DELETE FROM user_artists WHERE user_id = %s", (db_user_id,))  # Clear old data
#     execute_values(cur, "INSERT INTO user_artists (user_id, artist_name, artist_id, popularity, followers, spotify_url, image_url) VALUES %s", artists_data)

#     conn.commit()
#     cur.close()
#     conn.close()

#     return jsonify({"message": "Top artists stored successfully!"})

    
# @app.route("/user-top-tracks")
# def get_top_tracks():
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))
    
    
#     raw_data = sp.current_user_top_tracks(limit=10)["items"]

#     # Extract relevant data
#     top_tracks = []
#     for track in raw_data:
#         top_tracks.append({
#             "name": track["name"],
#             "id": track["id"],
#             "artists": [artist["name"] for artist in track["artists"]],  # Extract artist names
#             "album": track["album"]["name"],
#             "album_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,  # Handle missing images
#             "popularity": track["popularity"],
#             "spotify_url": track["external_urls"]["spotify"],
#             "duration_ms": track["duration_ms"]
#         })

#     return jsonify({"top_tracks": top_tracks})


  


# @app.route("/user-recently-played")
# def get_recently_played():
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))
    
#     # Fetch recently played tracks from Spotify API
#     raw_data = sp.current_user_recently_played(limit=10)["items"]

#     # Extract relevant data
#     recently_played = []
#     for item in raw_data:
#         track = item["track"]
#         recently_played.append({
#             "name": track["name"],
#             "id": track["id"],
#             "artists": [artist["name"] for artist in track["artists"]],
#             "album": track["album"]["name"],
#             "album_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
#             "popularity": track["popularity"],
#             "spotify_url": track["external_urls"]["spotify"],
#             "played_at": item["played_at"]  # Timestamp when the track was played
#         })

#     return jsonify({"recently_played": recently_played})

# @app.route("/user-top-genres")
# def get_top_genres():
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))

#     user_id = sp.current_user()["id"]

#     # Fetch user_id from DB
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM users WHERE spotify_id = %s", (user_id,))
#     result = cur.fetchone()

#     if not result:
#         return jsonify({"error": "User not found in database"}), 400

#     db_user_id = result[0]

#     # Fetch genres from top artists
#     raw_data = sp.current_user_top_artists(limit=20)["items"]
#     genre_list = []
#     for artist in raw_data:
#         genre_list.extend(artist["genres"])  # Some artists have multiple genres

#     genre_counts = Counter(genre_list)
#     sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]

#     genre_data = [(db_user_id, genre[0]) for genre in sorted_genres]

#     cur.execute("DELETE FROM user_genres WHERE user_id = %s", (db_user_id,))
#     execute_values(cur, "INSERT INTO user_genres (user_id, genre_name) VALUES %s", genre_data)

#     conn.commit()
#     cur.close()
#     conn.close()

#     return jsonify({"message": "Top genres stored successfully!"})



# @app.route("/recommend-tracks")
# def recommend_tracks():
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))

#     # Fetch user's top genres
#     user_genres = get_top_genres().json["top_genres"]  # Get genre list
#     if not user_genres:
#         return jsonify({"error": "No genres found"}), 400
    

    
#     top_genre = user_genres[0][0]  # Most common genre


#     search_results = sp.search(q=top_genre, type="track", limit=10)
#     recommended_tracks = []
    
#     for item in search_results["tracks"]["items"]:
#         recommended_tracks.append({
#             "name": item["name"],
#             "id": item["id"],
#             "artists": [artist["name"] for artist in item["artists"]],
#             "album": item["album"]["name"],
#             "spotify_url": item["external_urls"]["spotify"]
#         })

#     return jsonify({"recommended_tracks": recommended_tracks})



# @app.route("/create-playlist", methods=["POST"])
# def create_playlist():
#     sp = get_spotify_client()
#     if not sp:
#         return redirect(url_for("login"))

#     user_id = sp.current_user()["id"]

#     # Get playlist name and genre from request
#     playlist_name = request.json.get("name", "My Smart Playlist")
#     selected_genre = request.json.get("genre", None)

#     # Fetch recommended tracks based on selected genre
#     recommended_tracks = recommend_tracks().json["recommended_tracks"]
#     track_uris = [f"spotify:track:{track['id']}" for track in recommended_tracks]

#     # Create a playlist and add tracks
#     playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
#     sp.user_playlist_add_tracks(user_id, playlist["id"], track_uris)

#     return jsonify({"message": "Playlist created!", "playlist_url": playlist["external_urls"]["spotify"]})



# @app.route("/debug-token")
# def debug_token():
#     sp = get_spotify_client()
#     if not sp:
#         return "No token found, please re-authenticate."

#     token_info = session.get("token_info")
#     return jsonify(token_info)




if __name__ == "__main__":
    app.run(port=8888)
