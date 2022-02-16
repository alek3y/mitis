import pyaudio
import speech_recognition as sr

TIME = 3000 #millisecondi
FORMAT = pyaudio.paInt16
CHANNELS = 1 #numero di canali audio da usare
RATE = 44100 #numero di frame al secondo
CHUNK = 1024 #numero di frame per ogni buffer

class SpeechRecognition:
    def __init__(self):
        self.r = sr.Recognizer()
        self.source = sr.Microphone()
        self.p = pyaudio.PyAudio()
  

    #cattura la voce
    def caption(self, audio):
        audio_data = sr.AudioData(audio, RATE, 2) #Byte -> AudioData
        text = self.r.recognize_google(audio_data=audio_data, language='it-IT')
        print("client said: " + text)
    
    #registra l'audio e mette i bytes in una lista dove ogni elemento è un chunk
    def recorder(self):
        audio_bytes = []

        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK
                        )

        for i in range(0, int(44100 / CHUNK * (TIME / 1000))):
            audio_bytes.append(stream.read(CHUNK))

        #unisce i chunk
        joined_audio = b''.join(audio_bytes)
        return joined_audio
    
    def player(self, audio):
        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK
                        )

        #riproduce l'audio
        stream.write(audio)
