#importing libraries
from flask import Flask, render_template, request, jsonify
import os
import wave
import pyaudio
import socket
import threading
import pickle
import time
from pydub import AudioSegment


received_text= 'No data ...'

recording = False  # Initialize the recording flag
audio_frames = []
audio_filenames = []
client_text = ["", "", ""]
CHUNK = 1024
nombre_enregistremet =0
t2_threads = []
app = Flask(__name__)
def audio_stream(audio_part, audio_streaming_complete,audio_server_socket):
    filename = audio_filenames.pop(0)
    print("fichier supprimé de la liste ",filename)
    wf = wave.open(f"static/{filename}", 'rb')
    format = wf.getsampwidth()
    channels = wf.getnchannels()
    rate = wf.getframerate()
    frames = [format, channels, rate]

    audio_parts = 3
    try:
        while audio_part < audio_parts:
            client_socket, addr = audio_server_socket.accept()
            print('Accepted Connection from:', addr)
            if client_socket:
                client_socket.sendall(pickle.dumps(frames))
                time.sleep(1)
                temp_audio_file = os.path.join('temp_audio', f'part{audio_part}.wav').replace('\\', '_')
                print(temp_audio_file)
                part = AudioSegment.from_file(f"static/{filename}")
                part = part[audio_part * len(part) // 3: (audio_part + 1) * len(part) // 3]
                part.export(temp_audio_file, format="wav")
                with open(temp_audio_file, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    string_to_send = "part " + str(audio_part)
                    client_socket.sendall(audio_data + string_to_send.encode("utf-8"))

                print(f'Audio part {audio_part} closed')
                audio_part += 1
        # Fermez le fichier wave avant de le supprimer
        wf.close()
        # Supprimez le fichier
        os.remove(f"static/{filename}")
    except Exception as e:
        print(f"Erreur : {str(e)}")
    audio_streaming_complete.set()
def text_receive(client_socket):
    global received_text
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(f"Client a envoyé le texte : {data}")

            partie = data[:6]
            data = data[6:]
            print("chaima", partie)
            if partie == "part 0":
                client_text[0] = data
            elif partie == "part 1":
                client_text[1] = data
            elif partie == "part 2":
                client_text[2] = data
            else:
                print("Partie non reconnue :", partie)

            received_text = client_text[0]+"  " + client_text[1] + "  "+ client_text[2]
            print("len",len(received_text))
            if(len(received_text) == 4):
                received_text="Could not understand the audio"
        except Exception as e:
            print(f"Erreur lors de la réception du texte du client : {str(e)}")
            break
# Déclarez un drapeau pour indiquer si la logique est en cours d'exécution
logic_running = False
# Créez un verrou
logic_lock = threading.Lock()

def run_main_logic():
    global client_text
    global t2_threads
    global logic_running
    while audio_filenames:

        # Vérifiez si la logique est déjà en cours d'exécution
        with logic_lock:
            if logic_running:
                print("La logique est déjà en cours d'exécution.")
                return

            # Marquez la logique comme en cours d'exécution
            logic_running = True
        try :

                audio_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host_name = socket.gethostname()
                host_ip = socket.gethostbyname(host_name)
                print('HOST IP:', host_ip)
                audio_port = 9611
                socket_address = (host_ip, audio_port)
                print('Socket created')
                audio_server_socket.bind(socket_address)
                print('Socket audio bind complete')
                audio_server_socket.listen(5)
                print('audio_server_socket now listening')
                # Create the audio_streaming_complete flag outside of the threads
                audio_streaming_complete = threading.Event()

                # Start the audio server in a thread
                t1 = threading.Thread(target=audio_stream, args=(0, audio_streaming_complete,audio_server_socket))
                t1.start()
                # Wait for audio streaming to complete
                audio_streaming_complete.wait()
                t1.join()
                audio_server_socket.close()
                print ("audio_server_socket closed")
                print(t2_threads)
                if (len(t2_threads) == 0):
                        text_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        text_port = 9612
                        text_server_socket.bind((host_ip, text_port))
                        print('Socket text bind complete')
                        text_server_socket.listen(5)
                        print('text_server_socket now listening')
                        for i in range(3):
                            client_socket, addr = text_server_socket.accept()
                            print('Accepted Connection from:', addr)
                            if client_socket:
                                t2 = threading.Thread(target=text_receive, args=(client_socket,))
                                t2.start()
                                t2_threads.append(t2)

                        for t2_thread in t2_threads:
                            t2_thread.join()
                            # print("avant suprimé",t2_threads)
                            # t2_threads.pop(0)
                            # print("Aprés supprimé",t2_threads)
                        t2_threads = []
                        print("Tous les threads t2 ont été supprimés.")
                        text_server_socket.close()
                        print("text_server_socket closed")
                        print(client_text)
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
    app.run(host="adresse ip",port=8028)