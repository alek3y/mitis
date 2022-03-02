import threading
import pyaudio
import speech_recognition as sr
import pygame
import time
from threading import Thread, Semaphore

FORMAT = pyaudio.paInt16
CHANNELS = 1 # numero di canali audio da usare
RATE = 44100 # numero di frame al secondo
CHUNK = 512 # numero di frame per ogni buffer
CAPTION_SAMPLES_AMOUNT = 200 # numero di sample per ogni caption (indichiamo con sample un elemento del buffer audio)
MAX_CLIENTS = 50 # numero massimo di client che possono essere connessi

pygame.mixer.init(frequency=RATE, channels=CHANNELS)
pygame.mixer.set_num_channels(MAX_CLIENTS)

class AudioHandler(Thread):
    def __init__(self, chunk_handler):
        Thread.__init__(self, daemon=True)
        self.pyaudio = pyaudio.PyAudio()
        self.chunk_handler = chunk_handler
        self.recognizer = sr.Recognizer()
        self.chunk_buffer = []
        self.audio_bytes = b''
        self.sem = threading.Semaphore(0)
        self.muted = False

    def run(self):
        self.stream = self.pyaudio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK
                        )
        while True:
            audio_bytes = self.record()
            if not self.muted:
                self.audio_bytes = audio_bytes
                self.chunk_handler(audio_bytes)
                self.chunk_buffer.append(audio_bytes)
                self.sem.release()
    
    def record(self):
        return self.stream.read(CHUNK, exception_on_overflow=False)

    def mute(self):
        self.muted = not self.muted


class AudioPlayer(Thread):
    def __init__(self, buffer):
        Thread.__init__(self, daemon=True)
        self.buffer = buffer
        self.running = True

    def run(self):
        while self.running:
            audio_bytes = self.buffer.get()
            self.play(audio_bytes)
            time.sleep(1/RATE * CHUNK) # si assicura che non vengano riprodotti chunk uno sopra l'altro, trovando quanto tempo ci mette a riprodurre un chunk

    def play(self, audio_bytes):
        sound = pygame.mixer.Sound(buffer=audio_bytes)
        sound.play()
    
    def stop(self):
        self.running = False


class SpeechRecognition(Thread):
    def __init__(self, recorder, caption_handler):
        Thread.__init__(self, daemon=True)
        self.caption_handler = caption_handler
        self.recognizer = sr.Recognizer()
        self.recorder = recorder
        
    def run(self):
        while True:
            for i in range(CAPTION_SAMPLES_AMOUNT):
                self.recorder.sem.acquire()
            caption_audio_bytes = b''.join(self.recorder.chunk_buffer) # 200 chunk joinati
            text = self.caption(caption_audio_bytes)
            self.caption_handler(text)
            self.recorder.chunk_buffer.clear()

    def caption(self, audio):
        audio_data = sr.AudioData(audio, RATE, 2) # Byte -> AudioData
        try:
            text = self.recognizer.recognize_google(audio_data=audio_data, language='it-IT')
        except sr.UnknownValueError:
            text = ""
        return text