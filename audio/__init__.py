import pyaudio
import speech_recognition as sr

TIME = 900 #milliseconds

class SpeechRecognition:
    def __init__(self):
        self.r = sr.Recognizer()
        self.source = sr.Microphone()
        self.p = pyaudio.PyAudio()

    #records voice and prints it out
    def caption(self):
        with self.source as source:
            print("listening...")

            audio = self.r.listen(source)
            text = self.r.recognize_google(audio, language='it-IT')
            
            print("client said: " + text)
    
    #records audio and puts audio bytes in a list 
    def recorder(self):
        global TIME
        FORMAT = pyaudio.paInt16
        CHANNELS = 1 #number of audio streams to use
        RATE = 44100 #number of frames per second
        CHUNK = 1024 #number of frames per buffer
        audio_bytes = []

        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK
                        )

        for i in range(0, int(44100 / CHUNK * (TIME / 1000))):
            audio_bytes.append(stream.read(CHUNK))

        return audio_bytes


        


