from flask import Flask, request, jsonify

app = Flask(__name__)

songs = {}  # Dictionary to store songs 
playlists = {}  # Dictionary to store playlists 
song_id_counter = 1 # Unique id incrementer
playlist_id_counter = 1 # Playlist id incrementer

# Helper function to generate a new song ID
def get_new_song_id():
    global song_id_counter
    song_id = song_id_counter # Current song ID 
    song_id_counter += 1 # Increase the counter for next inserted song
    return song_id # return new song ID

# Helper function to generate a new playlist ID
def get_new_playlist_id():
    global playlist_id_counter 
    playlist_id = playlist_id_counter # Get the current playlist ID
    playlist_id_counter += 1 # Increment the counter for next ID
    return playlist_id # Return the new playlist ID

# Route to create a new song
@app.route('/songs', methods=['POST'])
def create_song():
    data = request.json
    # Check if 'title' and 'artist' fields are present in the request
    if not data or 'title' not in data or 'artist' not in data:
        return jsonify({"error": "Missing required fields: title and artist"}), 400

    # Generate a new song ID and add the song
    song_id = get_new_song_id()
    songs[song_id] = {
        "id": song_id,
        "title": data['title'],
        "artist": data['artist'],
        "album": data.get('album', ""),
        "duration": data.get('duration', 0),
        "genre": data.get('genre', "")
    }
    # Return a success message with the created song's details
    return jsonify({"message": "Song created successfully", "song": songs[song_id]}), 201

# Route to update an existing song
@app.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    # Check if song is in dictionary
    if song_id not in songs:
        return jsonify({"error": "Song not found"}), 404

    data = request.json
    song = songs[song_id]
    
    # Update song details if provided
    song['title'] = data.get('title', song['title'])
    song['artist'] = data.get('artist', song['artist'])
    song['album'] = data.get('album', song['album'])
    song['duration'] = data.get('duration', song['duration'])
    song['genre'] = data.get('genre', song['genre'])

    return jsonify({"message": "Song updated successfully", "song": song}), 200

# Route to delete a song
@app.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    # Checks if song is in dictionary
    if song_id not in songs:
        return jsonify({"error": "Song not found"}), 404

    del songs[song_id] # Delete song from dictionary
    return jsonify({"message": "Song deleted successfully"}), 200

# Route to search/get a song by title, artist, or genre
@app.route('/songs/search', methods=['GET'])
def search_songs():
    song_id = request.args.get('id', type=int) # Get song id
    title = request.args.get('title', type=str) # Get song title
    artist = request.args.get('artist', type=str) # Get song artist
    genre = request.args.get('genre', type=str) # Get genre

    # If song id exists, search for the song by id
    if song_id:
        song = songs.get(song_id)
        if not song:
            return jsonify({"error": "Song not found"}), 404
        return jsonify(song), 200

    # If no song id exists, search songs based on the search criteria
    matching_songs = list(songs.values()) # Searches all songs

    # Search by title
    if title:
        matching_songs = [song for song in matching_songs if title.lower() in song['title'].lower()]
    # Search by artist
    if artist:
        matching_songs = [song for song in matching_songs if artist.lower() in song['artist'].lower()]
    # Search by genre
    if genre:
        matching_songs = [song for song in matching_songs if genre.lower() in song['genre'].lower()]

    return jsonify(matching_songs), 200

# Route to sort songs by a specific field
@app.route('/songs/sort', methods=['GET'])
def sort_songs():
    sort_by = request.args.get('sort_by', default='title', type=str)
    reverse = request.args.get('reverse', default='false', type=str).lower() == 'true'

    if sort_by not in ['title', 'artist', 'genre']:
        return jsonify({"error": "Invalid sort field. Must be one of: title, artist, genre"}), 400

    # Sort songs by provided field
    sorted_songs = sorted(songs.values(), key=lambda x: x.get(sort_by, ""), reverse=reverse)
    return jsonify(sorted_songs), 200

# Route to create a new playlist
@app.route('/playlists', methods=['POST'])
def create_playlist():
    data = request.json
    # Check if name is provided
    if not data or 'name' not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    # Generate new playlist id and add playlist to dictionary
    playlist_id = get_new_playlist_id()
    playlists[playlist_id] = {
        "id": playlist_id,
        "name": data['name'],
        "description": data.get('description', ""),
        "songs": []  # Initialize with an empty list of songs
    }
    return jsonify({"message": "Playlist created successfully", "playlist": playlists[playlist_id]}), 201

# Route to get a playlist by ID
@app.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = playlists.get(playlist_id) # Get playlist by id
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    return jsonify(playlist), 200

# Route to update a playlist
@app.route('/playlists/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    # Check if playlist is in dictionary
    if playlist_id not in playlists:
        return jsonify({"error": "Playlist not found"}), 404

    data = request.json
    playlist = playlists[playlist_id]
    
    # Update playlist details if provided
    playlist['name'] = data.get('name', playlist['name'])
    playlist['description'] = data.get('description', playlist['description'])
    playlist['songs'] = data.get('songs', playlist['songs'])

    return jsonify({"message": "Playlist updated successfully", "playlist": playlist}), 200

# Route to delete a playlist
@app.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    # Check if playlist in dictionary
    if playlist_id not in playlists:
        return jsonify({"error": "Playlist not found"}), 404

    del playlists[playlist_id] # Remove playlist from dictionary
    return jsonify({"message": "Playlist deleted successfully"}), 200

# Route to add a song to a playlist
@app.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['POST'])
def add_song_to_playlist(playlist_id, song_id):
    # Check if playlist and song in dictionary
    if playlist_id not in playlists:
        return jsonify({"error": "Playlist not found"}), 404
    if song_id not in songs:
        return jsonify({"error": "Song not found"}), 404

    playlist = playlists[playlist_id] # Get playlist
    # Check if song in playlist
    if song_id in playlist['songs']:
        return jsonify({"error": "Song already in playlist"}), 400

    playlist['songs'].append(song_id) # If not, add song to playlist
    return jsonify({"message": "Song added to playlist successfully", "playlist": playlist}), 200

# Route to remove a song from a playlist
@app.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    # Check if playlist and song in dictionary
    if playlist_id not in playlists:
        return jsonify({"error": "Playlist not found"}), 404
    if song_id not in songs:
        return jsonify({"error": "Song not found"}), 404

    playlist = playlists[playlist_id] # Get playlist
    # Check if song in playlist
    if song_id not in playlist['songs']:
        return jsonify({"error": "Song not in playlist"}), 400

    playlist['songs'].remove(song_id) # Remove song from playlist
    return jsonify({"message": "Song removed from playlist successfully", "playlist": playlist}), 200

if __name__ == '__main__':
    app.run(debug=True)