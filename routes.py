from flask import jsonify, redirect, url_for, request, session, Blueprint
from collections import Counter
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from db import get_db_connection  # Import the database connection function
from auth import get_spotify_client  # Import authentication function
from psycopg2.extras import execute_values



routes_bp = Blueprint("routes", __name__) 

@routes_bp.route("/user-profile", methods=["GET"])
def get_user_profile():
    """Fetch user profile details."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))

    user_info = sp.current_user()

    return jsonify({
        "id": user_info["id"],
        "display_name": user_info["display_name"],
        "email": user_info.get("email", "N/A"),
        "profile_url": user_info["external_urls"]["spotify"],
        "image": user_info["images"][0]["url"] if user_info["images"] else None
    })

@routes_bp.route("/user-top-artists")
def get_top_artists():
    """Fetch and store top artists of the user."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))

    user_id = sp.current_user()["id"]

    # Fetch user_id from DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE spotify_id = %s", (user_id,))
    result = cur.fetchone()

    if not result:
        return jsonify({"error": "User not found in database"}), 400

    db_user_id = result[0]

    # Fetch and store top artists
    user_top_artists = sp.current_user_top_artists(limit=10)["items"]
    artists_data = [
        (db_user_id, artist["name"], artist["id"], artist["popularity"], artist["followers"]["total"],
         artist["external_urls"]["spotify"], artist["images"][0]["url"] if artist["images"] else None)
        for artist in user_top_artists
    ]

    cur.execute("DELETE FROM user_artists WHERE user_id = %s", (db_user_id,))  # Clear old data
    execute_values(cur, "INSERT INTO user_artists (user_id, artist_name, artist_id, popularity, followers, spotify_url, image_url) VALUES %s", artists_data)

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Top artists stored successfully!"})

@routes_bp.route("/user-top-genres")
def get_top_genres():
    """Fetch and store top genres based on user's top artists."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))

    user_id = sp.current_user()["id"]

    # Fetch user_id from DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE spotify_id = %s", (user_id,))
    result = cur.fetchone()

    if not result:
        return jsonify({"error": "User not found in database"}), 400

    db_user_id = result[0]

    # Fetch genres from top artists
    raw_data = sp.current_user_top_artists(limit=20)["items"]
    genre_list = []
    for artist in raw_data:
        genre_list.extend(artist["genres"])  # Some artists have multiple genres

    genre_counts = Counter(genre_list)
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    genre_data = [(db_user_id, genre[0]) for genre in sorted_genres]

    cur.execute("DELETE FROM user_genres WHERE user_id = %s", (db_user_id,))
    execute_values(cur, "INSERT INTO user_genres (user_id, genre_name) VALUES %s", genre_data)

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Top genres stored successfully!"})



@routes_bp.route("/user-top-genres-show")
def show_top_genres():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_genres;")
    result = cur.fetchall()

    user_genres = [{"user_id": row[0], "genre_id": row[1]} for row in result]

    return jsonify(result)
