import speech_recognition as sr

class SpeechRecognition:
    def __init__(self):
        self.r = sr.Recognizer()
        self.source = sr.Microphone()

    def caption(self):
        with self.source as source:
            print("listening...")

            audio = self.r.listen(source)
            text = self.r.recognize_google(audio, language='it-IT')
            
            print("client said: " + text)
        


