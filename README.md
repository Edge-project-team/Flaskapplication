# Audio Transcription Flask Application
This Flask application allows users to record an audio speech through a web interface. The audio is then divided and distributed to multiple clients for transcription. The transcribed text is displayed in the interface.
# Installation
git clone <repository_url>
Install the required dependencies using pip:
pip install -r requirements.txt

# Client code
In the client-side code, three clients receive the audio speech data from the server. Each client processes this audio data to transcribe it into text and then sends the transcribed text back to the server.*
# Server code 
The server receives the audio input from the interface user. It then divides the audio into parts and distributes these parts to the connected clients. Each client processes its respective audio part and transcribes it into text. The server collects the results from each client and concatenates them to prepare the transcribed text, which will be displayed in the interface.
# run the application 
python server.py
python client.py
Open the application in a web browser.

Record an audio speech using the provided interface.

The audio will be transcribed and the text will be displayed in the interface.


![image](https://github.com/Edge-project-team/Flaskapplication/assets/106774025/025c58fb-6b78-44e6-9d48-9c9418faa7f9)


![image](https://github.com/Edge-project-team/Flaskapplication/assets/106774025/ab6e48bc-43ee-466d-8968-406e343cbd11)


![image](https://github.com/Edge-project-team/Flaskapplication/assets/106774025/89c07232-8344-43b3-9e8b-948613595f94)
