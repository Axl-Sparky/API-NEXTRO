from flask import Flask, jsonify, send_from_directory, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import random
import json
import lyricsgenius
from stalking.insta import insta_bp
from stalking.youtube import download_thumbnail
from info.weather import get_weather  # Import the weather function
from info.crypto import get_crypto    # Import the crypto function
from info.youtube import search_youtube_videos  # Import the YouTube search function
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB upload limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4', 'mov', 'avi'}

# Initialize Genius API
genius = lyricsgenius.Genius("UCPfLPaO-yEFTrzwgxsNgPN0JaZr8rUnWhLXjA4w5WmUP9rFp1ueGXPPcRqW6Jsa")

# Define directories for static files
VIDEO_DIRECTORY = os.path.join(os.getcwd(), 'videos', 'naruto')
IMAGE_DIRECTORY_IMAGE = os.path.join(os.getcwd(), 'images', 'image')
IMAGE_DIRECTORY_CAT = os.path.join(os.getcwd(), 'images', 'cat')
IMAGE_DIRECTORY_TSUNADE = os.path.join(os.getcwd(), 'images', 'tsunade')
NSFW_WAIFU_FILE = os.path.join(os.getcwd(), 'nsfw', 'waifu.json')
NSFW_NEKO_FILE = os.path.join(os.getcwd(), 'nsfw', 'neko.json')
CAT_FACT_FILE = os.path.join(os.getcwd(), 'chat', 'cat_fact.json')
DETAILS_FILE = os.path.join(os.getcwd(), 'chat', 'details.json')

# Load static files
video_files = os.listdir(VIDEO_DIRECTORY)
image_files_image = os.listdir(IMAGE_DIRECTORY_IMAGE)
image_files_cat = os.listdir(IMAGE_DIRECTORY_CAT)
image_files_tsunade = os.listdir(IMAGE_DIRECTORY_TSUNADE)

# Load cat facts
def load_cat_facts():
    with open(CAT_FACT_FILE, 'r') as f:
        cat_facts = json.load(f)
    return cat_facts['facts'] if 'facts' in cat_facts else []

CAT_FACTS = load_cat_facts()

# Load details
def load_details():
    with open(DETAILS_FILE, 'r') as f:
        details = json.load(f)
    return details

DETAILS = load_details()

# Load NSFW waifu data
def load_waifu_data():
    with open(NSFW_WAIFU_FILE, 'r') as f:
        waifu_data = json.load(f)
    return waifu_data

WAIFU_DATA = load_waifu_data()

# Load NSFW neko data
def load_neko_data():
    with open(NSFW_NEKO_FILE, 'r') as f:
        neko_data = json.load(f)
    return neko_data

NEKO_DATA = load_neko_data()

# Root route to render index.html
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Routes to serve random media and facts
@app.route('/naruto', methods=['GET'])
def serve_random_naruto_video():
    try:
        random_video = random.choice(video_files)
        return send_from_directory(VIDEO_DIRECTORY, random_video)
    except IndexError:
        return "No Naruto videos found", 404
    except Exception as e:
        return str(e), 500

@app.route('/image', methods=['GET'])
def serve_random_image_image():
    try:
        random_image = random.choice(image_files_image)
        return send_from_directory(IMAGE_DIRECTORY_IMAGE, random_image)
    except IndexError:
        return "No images found in 'image' directory", 404
    except Exception as e:
        return str(e), 500

@app.route('/cat', methods=['GET'])
def serve_random_image_cat():
    try:
        random_image = random.choice(image_files_cat)
        return send_from_directory(IMAGE_DIRECTORY_CAT, random_image)
    except IndexError:
        return "No images found in 'cat' directory", 404
    except Exception as e:
        return str(e), 500

@app.route('/tsunade', methods=['GET'])
def serve_random_image_tsunade():
    try:
        random_image = random.choice(image_files_tsunade)
        return send_from_directory(IMAGE_DIRECTORY_TSUNADE, random_image)
    except IndexError:
        return "No images found in 'tsunade' directory", 404
    except Exception as e:
        return str(e), 500

@app.route('/cat-fact', methods=['GET'])
def get_random_cat_fact():
    try:
        random_fact = random.choice(CAT_FACTS)
        return jsonify({"fact": random_fact})
    except IndexError:
        return "No cat facts found", 404
    except Exception as e:
        return str(e), 500

@app.route('/details/<category>', methods=['GET'])
def get_random_fact(category):
    try:
        if category in DETAILS:
            facts = DETAILS[category]
            random_fact = random.choice(facts)
            return jsonify({"fact": random_fact})
        else:
            return f"No facts found for category '{category}'", 404
    except IndexError:
        return f"No facts found for category '{category}'", 404
    except Exception as e:
        return str(e), 500
# YouTube thumbnail route
@app.route('/download_thumbnail', methods=['GET'])
def download_youtube_thumbnail():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    thumbnail_url, error = download_thumbnail(video_url)
    if error:
        return jsonify({'error': error}), 500

    return jsonify({'thumbnail_url': thumbnail_url})

# Route to serve random NSFW waifu data
@app.route('/nsfw/waifu', methods=['GET'])
def serve_random_nsfw_waifu():
    try:
        random_waifu = random.choice(WAIFU_DATA)['url']
        return jsonify({"url": random_waifu})
    except IndexError:
        return "No NSFW waifu data found", 404
    except Exception as e:
        return str(e), 500

# Route to serve random NSFW neko data
@app.route('/nsfw/neko', methods=['GET'])
def serve_random_nsfw_neko():
    try:
        random_neko = random.choice(NEKO_DATA)['url']
        return jsonify({"url": random_neko})
    except IndexError:
        return "No NSFW neko data found", 404
    except Exception as e:
        return str(e), 500

# Weather route
@app.route('/info/weather', methods=['GET'])
def info_weather():
    return get_weather()

# Crypto route
@app.route('/info/crypto', methods=['GET'])
def info_crypto():
    return get_crypto()

# Route to fetch song lyrics from Genius API
@app.route('/lyrics', methods=['GET'])
def get_lyrics():
    query = request.args.get('q')

    if not query:
        return jsonify({'error': 'Missing query parameter `q`'}), 400

    try:
        song = genius.search_song(query)
        if song:
            response = {
                'title': song.title,
                'artist': song.artist,
                'lyrics': song.lyrics
            }
            return jsonify(response)
        else:
            return jsonify({'error': 'Lyrics not found for the given query'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to search YouTube videos
@app.route('/youtube', methods=['GET'])
def search_youtube():
    query = request.args.get('search')

    if not query:
        return jsonify({'error': 'Missing search query parameter `search`'}), 400

    try:
        results, status_code = search_youtube_videos(query)
        if status_code == 200:
            return jsonify(results)
        else:
            return jsonify(results), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{file_extension}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        file_url = url_for('uploaded_file', filename=unique_filename, _external=True)
        return jsonify({"file_url": file_url}), 201
    return jsonify({"error": "Invalid file format"}), 400

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
# Register the Instagram blueprint
app.register_blueprint(insta_bp)

if __name__ == '__main__':
    app.run(debug=True)
