#importing libraries
from flask import Flask, render_template, request, jsonify
import os
import wave
import pyaudio
import threading



received_text= 'No data...'

recording = False  # Initialize the recording flag
audio_frames = []
audio_filenames = []

CHUNK = 1024
nombre_enregistremet =0

app = Flask(__name__)

def recognize_speech(nom_fichier):
    try:
        import speech_recognition as sr

        with sr.AudioFile(nom_fichier) as source:
            recognizer = sr.Recognizer()
            audio_data = recognizer.record(source)

        text_output = recognizer.recognize_google(audio_data)
        print("Transcript:", text_output)  # Print the recognized speech to the console
        return text_output
    except ImportError:
        print("Please install the 'speech_recognition' library to perform speech recognition.")
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Déclarez un drapeau pour indiquer si la logique est en cours d'exécution
logic_running = False
# Créez un verrou
logic_lock = threading.Lock()

def run_main_logic():
    global logic_running
    global  received_text
    while audio_filenames:

        # Vérifiez si la logique est déjà en cours d'exécution
        with logic_lock:
            if logic_running:
                print("La logique est déjà en cours d'exécution.")
                return

            # Marquez la logique comme en cours d'exécution
            logic_running = True
        try :
            filename = audio_filenames.pop(0)
            print("fichier supprimé de la liste ", filename)
            text_output = recognize_speech(f"static/{filename}")
            received_text = text_output
            print(received_text)
            if ((received_text is None )):
                received_text = "Could not understand data"
            os.remove(f"static/{filename}")

        finally:
            # Marquez la logique comme terminée, même en cas d'exception
            logic_running = False





@app.route('/')
def index():
    return render_template('index.html',received_text=received_text)
@app.route('/get_received_text')
def get_received_text():
    return jsonify(received_text)
@app.route('/upload', methods=['POST'])
def upload_file():
    global nombre_enregistremet

    UPLOAD_FOLDER = 'static'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if 'audio' not in request.files:
        return jsonify({"message": "No file part"})

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({"message": "No selected file"})

    if audio_file:
        nombre_enregistremet = nombre_enregistremet + 1
        filename = f'audio_{nombre_enregistremet}.wav'
        audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        unique_filename = f'audio_{nombre_enregistremet}.wav'
        print(unique_filename)
        audio_filenames.append(unique_filename)
        print("list des audio", audio_filenames)
        run_main_logic()

        return jsonify({"message": "File uploaded successfully"})


@app.route('/record', methods=['POST'])
def record_audio():
    global recording
    global audio_frames
    global audio_filenames
    global nombre_enregistremet
    if request.json.get('action') == 'start':
        recording = True
        nombre_enregistremet = nombre_enregistremet+1
        audio_frames = []
        if not os.path.exists('static'):
            os.makedirs('static')
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNK)
        # Générez un nom de fichier unique pour cette session d'enregistrement
        unique_filename = f'audio_{nombre_enregistremet}.wav'
        print(unique_filename)
        audio_filenames.append(unique_filename)
        print("list des audio",audio_filenames)
        while True:
            data= stream.read(1024)
            audio_frames.append(data)
            if not recording:
                break
        stream.stop_stream()
        stream.close()
        p.terminate()
        audio_file = os.path.join('static', unique_filename)

        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))
        run_main_logic()

        return jsonify({"message": "Recording stopped and saved as audio.wav"})

    if request.json.get('action') == 'stop':
        recording = False
        return jsonify({"message": "Recording stopped"})


if __name__ == '__main__':
    app.run(host="ip_adress",port=8028)