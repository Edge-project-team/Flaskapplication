# Audio Transcription Flask Application
This Flask application allows users to record an audio speech through a web interface. The audio is then divided and distributed to multiple clients for transcription. The transcribed text is displayed in the interface.
# Installation
git clone <repository_url>
# Install the required dependencies using pip:
pip install -r requirements.txt
# adress 
change your correspanding host adress in server code (line 244 ) and in client code (line 7)  
# Client code
In the client-side code, three clients receive the audio speech data from the server. Each client processes this audio data to transcribe it into text and then sends the transcribed text back to the server.*
# Server code 
The server receives the audio input from the interface user. It then divides the audio into parts and distributes these parts to the connected clients. Each client processes its respective audio part and transcribes it into text. The server collects the results from each client and concatenates them to prepare the transcribed text, which will be displayed in the interface.
# run server code 
python server.py
# run client code
python client.py
# Open the application in a web browser.
# usage 
Ensure you provide an English audio sample in .wav format if the user intends to upload a file for processing.

Record an audio speech using the provided interface.

The audio will be transcribed and the text will be displayed in the interface.


# Demo


![image](https://github.com/Edge-project-team/Flaskapplication/assets/106774025/ab6e48bc-43ee-466d-8968-406e343cbd11)


![image](https://github.com/Edge-project-team/Flaskapplication/assets/106774025/89c07232-8344-43b3-9e8b-948613595f94)

# Difference between monoversion and distributed version 
The mono version is quicker to develop, but it can face scalability issues and relies on a stable internet connection for efficient speech recognition. 

On the other hand, the distributed version offers improved performance scalability and reduced wait times. However, it demands more time initially for development and deployment setup due to its complexity and coordination needs. It's important to note that the distributed version also requires a reliable internet connection, but it effectively addresses performance requirements.
