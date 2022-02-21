import threading
import pyaudio
import speech_recognition as sr
from threading import Thread, Semaphore
from math import ceil #2.0 = 2 | 2.1 = 3

TIME = 500 #millisecondi
FORMAT = pyaudio.paInt16
CHANNELS = 1 #numero di canali audio da usare
RATE = 44100 #numero di frame al secondo
CHUNK = 8192 #numero di frame per ogni buffer
CAPTION_SAMPLES_AMOUNT = 4 #numero di sample per ogni caption (indichiamo con sample un elemento del buffer audio)

class SpeechRecognition(Thread):
    def __init__(self, recorder):
        Thread.__init__(self)
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
        Thread.__init__(self)
        self.stream = pyaudio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK
                        )
        self.chunk_handler = chunk_handler
        self.recognizer = sr.Recognizer()
        self.chunk_buffer = []
        self.audio_bytes = b''
        self.sem = threading.Semaphore(0)

    def run(self):
        while True:
            audio_bytes = self.record()
            self.audio_bytes = audio_bytes
            self.chunk_handler(audio_bytes)
            self.chunk_buffer.append(audio_bytes)
    
    def record(self):
        buffer = []
        #https://stackoverflow.com/a/66628753
        frame_count = ceil(RATE*TIME/1000) #numero di frame da leggere
        for i in range(0, int(RATE / CHUNK * (TIME / 1000))):
            buffer.append(self.stream.read(CHUNK, exception_on_overflow=False))
            frame_count -= CHUNK
        if frame_count < CHUNK:
            buffer.append(self.stream.read(frame_count))
            self.sem.release()
        return b''.join(buffer)

class AudioPlayer(Thread):
    def __init__(self, pyaudio, recorder):
        Thread.__init__(self)
        self.recorder = recorder
        self.stream = pyaudio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK
                        )

    def run(self):
        while True:
            self.play()

    def play(self):
        self.stream.write(self.recorder.audio_bytes)
