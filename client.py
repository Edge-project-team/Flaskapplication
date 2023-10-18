import socket
import os
import pickle
import threading
import time

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 9611
CHUNK = 1024
socket_address = (host_ip, port)

# Port pour l'envoi du texte
text_port = 9612
partie=""
connected_once = False  # Drapeau pour contrôler la connexion unique
connected_text = False
identifiant=0
audio_file=""
def connect_audio_to_server():
    global connected_once
    global  audio_file
    print("connected_recive_audio",connected_once)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(socket_address)
        connected_once = True
        print("CLIENT CONNECTED TO recive audio", socket_address)
        return client_socket
    except Exception as e:
        print(f"Error during connection to the server: {e}")
        return None
def connect_text_to_server():
    global connected_text
    print("connected_text",connected_text)
    try:
        text_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        text_socket.connect((host_ip, text_port))
        connected_text = True
        print("CLIENT CONNECTED TO SEND TEXT ", socket_address)
        return text_socket
    except Exception as e:
        print(f"Error during connection to the server: {e}")
        return None

def receive_audio(client_socket):
    global identifiant;
    global partie ;
    try:
        frames = client_socket.recv(4 * 1024)
        format, channels, rate = pickle.loads(frames)

        audio_data = b''

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            audio_data += data
        partie = audio_data[-6:].decode()
        print(partie)

        audio_data = audio_data[:-6]
        if not os.path.exists('client1'):
            os.makedirs('client1')
        unique_filename=f'received_audio_part{identifiant}.wav'
        audio_file = os.path.join('client1', unique_filename)
        with open(audio_file, 'wb') as received_audio_file:
            received_audio_file.write(audio_data)

        print('Audio received and saved as received_audio.wav')

    except Exception as e:
        print(f"Error during audio reception: {e}")


def main():
     global connected_once
     global connected_text
     global identifiant
     global partie
     global audio_file
     while True:
         if not connected_once :  # Reconnectez le client uniquement si l'enregistrement est actif
             client_socket = connect_audio_to_server()
             if client_socket:
                # Start a thread to receive audio from the server
                audio_thread = threading.Thread(target=receive_audio, args=(client_socket,))
                audio_thread.start()
                while not audio_thread.is_alive():
                    time.sleep(1)  # Attendre que le thread audio commence

                audio_thread.join()
                client_socket.close()
                while not connected_text:
                    text_socket = connect_text_to_server()
                    if text_socket:
                        # Perform speech recognition on the received audio
                        text_output = recognize_speech(f'client1/received_audio_part{identifiant}.wav')
                        identifiant = identifiant + 1
                        if (text_output is None):
                             text_output =""

                        text_send=partie+text_output
                        print(f'Text sent to server:{partie}', text_output)
                        text_socket.send(text_send.encode())
                        connected_text = False
                        text_socket.close()
                        break
                        # Supprimez le fichier
                        os.remove(audio_file)
             connected_once= False



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


if __name__ == "__main__":
    main()