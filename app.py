from flask import Flask, request, jsonify
from pytube import YouTube, exceptions as pytube_exceptions
import os
import uuid
import speech_recognition as sr
from pydub import AudioSegment
from flask_cors import CORS # Add this line

app = Flask(__name__)
CORS(app) # Add this line to enable CORS for all routes

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_yt_as_mp3(url):
    """
    Downloads the audio from a YouTube video and converts it to MP3.
    """
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            raise ValueError("No audio stream found for this YouTube video.")
        
        # Generate a unique filename to avoid conflicts
        filename = f"{uuid.uuid4()}.mp4"
        output_path = audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
        
        mp3_path = output_path.replace(".mp4", ".mp3")
        AudioSegment.from_file(output_path).export(mp3_path, format="mp3")
        
        os.remove(output_path) # Clean up the temporary mp4 file
        return mp3_path
    except pytube_exceptions.VideoUnavailable:
        raise ValueError("Video is unavailable or private.")
    except pytube_exceptions.RegexMatchError:
        raise ValueError("Invalid YouTube URL format.")
    except Exception as e:
        # Catch other pytube or file system errors during download/conversion
        raise RuntimeError(f"Error during YouTube download or conversion: {e}")

def transcribe_audio_to_text(audio_path):
    """
    Transcribes an audio file to text using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(audio_path)
        # SpeechRecognition often works better with WAV files, so convert temporarily
        wav_path = audio_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")
        
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        os.remove(wav_path) # Clean up the temporary wav file
        return text
    except sr.UnknownValueError:
        raise ValueError("Google Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        raise RuntimeError(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        # Catch other pydub or file system errors during transcription preparation
        raise RuntimeError(f"Error during audio processing for transcription: {e}")

@app.route("/")
def index():
    return jsonify({"message": "Welcome to the YouTube-to-Text API! Use /api/yt-to-text with a POST request."})

@app.route("/api/yt-to-text", methods=["POST"])
def yt_to_text():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL in request body."}), 400

    mp3_path = None # Initialize to None for cleanup in finally block
    try:
        mp3_path = download_yt_as_mp3(url)
        transcript = transcribe_audio_to_text(mp3_path)
        return jsonify({"text": transcript})
    except ValueError as e:
        # Specific errors like invalid URL, video unavailable, or transcription issues
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        # Errors related to external services or unexpected issues
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Catch any other unforeseen errors
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
    finally:
        # Ensure temporary mp3 file is removed even if an error occurs
        if mp3_path and os.path.exists(mp3_path):
            os.remove(mp3_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # IMPORTANT: debug=True should NOT be used in a production environment.
    # For production, use a production-ready WSGI server like Gunicorn or uWSGI.
    # Also, ensure 'ffmpeg' or 'libav' is installed on your system for pydub to work.
    app.run(host="0.0.0.0", port=port, debug=True)
