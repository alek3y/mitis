import threading
import pyaudio
import speech_recognition as sr
from threading import Thread, Semaphore
from math import ceil #2.0 = 2 | 2.1 = 3

TIME = 500 #millisecondi
FORMAT = pyaudio.paInt16
CHANNELS = 1 #numero di canali audio da usare
RATE = 44100 #numero di frame al secondo
CHUNK = 1024 #numero di frame per ogni buffer
CAPTION_SAMPLES_AMOUNT = 4 #numero di sample per ogni caption (indichiamo con sample un elemento del buffer audio)

class SpeechRecognition(Thread):
    def __init__(self, recorder):
        Thread.__init__(self, daemon=True)
        self.recognizer = sr.Recognizer()
        self.recorder = recorder
        
    def run(self):
        while True:
            for i in range(CAPTION_SAMPLES_AMOUNT):
                self.recorder.sem.acquire()
            caption_audio_bytes = b''.join(self.recorder.chunk_buffer) #4 chunk joinati
            text = self.caption(caption_audio_bytes)
            print("client said: " + str(text))
            self.recorder.chunk_buffer.clear()

    def caption(self, audio):
        audio_data = sr.AudioData(audio, RATE, 2) #Byte -> AudioData
        try:
            text = self.recognizer.recognize_google(audio_data=audio_data, language='it-IT')
        except sr.UnknownValueError:
            text = ""
        return text

class AudioHandler(Thread):
    def __init__(self, pyaudio, chunk_handler):
        Thread.__init__(self, daemon=True)
        self.pyaudio = pyaudio
        self.chunk_handler = chunk_handler
        self.recognizer = sr.Recognizer()
        self.chunk_buffer = []
        self.audio_bytes = b''
        self.sem = threading.Semaphore(0)

    def run(self):
        self.stream = self.pyaudio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK
                        )
        while True:
            audio_bytes = self.record()
            self.audio_bytes = audio_bytes
            self.chunk_handler(audio_bytes)
            self.chunk_buffer.append(audio_bytes)
            #self.sem.release()
    
    def record(self):
        return self.stream.read(CHUNK, exception_on_overflow=False)

class AudioPlayer:
    def __init__(self, pyaudio, audio_next):
        self.stream = pyaudio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=lambda _, chunk, time, status: audio_next(chunk)
                        )

    def play(self, audio_bytes):
        self.stream.write(audio_bytes)
