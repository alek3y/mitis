# # https://www.pythontutorial.net/tkinter/tkinter-hello-world/
# # https://www.pythontutorial.net/tkinter/tkinter-grid/
# # pip3 install ttkthemes
# # pip3 install pillow
# pip3 install imutils
# pip3 install opencv-python
# # keybinds: https://www.pythontutorial.net/tkinter/tkinter-event-binding/
# #TODO fixare bottone che si preme solo in focus
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from ttkthemes import ThemedTk
import io
import math


FONT = ("Monospace", 11)
PLACEHOLDER = "Inserisci un messaggio... "
mic_status = True
cam_status = True
subtitles_status = False

class Gui:
	def __init__(self, roomJoiner, messageHandler, muteHandler, camHandler):
		self.grid_size = 1	#numero di righe e di colonne delle cam (dato che è un quadrato: colonne = righe)
		self.counter_size = 1
		self.cams_container = None
		self.temp_client_list = []	#lista che conterrà le webcam temporanee durante la crezione della root
		self.cams = {}	#dizionario che conterrà le webcam dei client presenti
		self.roomJoiner = roomJoiner
		self.messageHandler = messageHandler
		self.muteHandler = muteHandler
		self.camHandler = camHandler
		self.root = ThemedTk(theme = "breeze")	#finestra padre con tema breeze
		self.root.title("Mitis")
		self.width_screen = self.root.winfo_screenwidth()	# larghezza dello schermo
		self.height_screen = self.root.winfo_screenheight() # altezza dello schermo
		self.root.geometry(f"{self.width_screen}x{self.height_screen}")
		self.root.minsize(704, 396)	#grandezza minima finestra
		self.actual_window_width = self.width_screen
		self.actual_window_height = self.height_screen

		self.dialog = ttk.Frame(self.root)
		dialog_text = ttk.Label(self.dialog, text = "inserisci codice stanza:", font = FONT)
		dialog_text.pack()
		room_code = tk.StringVar()
		self.input_entry= ttk.Entry(self.dialog, textvariable = room_code, font = FONT)
		self.input_entry.focus()
		self.input_entry.pack()
		self.key = tk.PhotoImage(file = "assets/key.png")
		self.submit = ttk.Button(self.dialog, image = self.key)
		self.root.bind("<Return>", lambda event:self.getJoinCode(event, room_code))
		self.submit.bind("<ButtonRelease>", lambda event:self.getJoinCode(event, room_code))
		self.submit.pack(pady = 5)
		self.error = ttk.Label(self.dialog, text = "", foreground = "red", font = FONT)
		self.error.pack()
		self.dialog.pack(expand = True)

	def resizeWindow(self, event):
		if event.widget == self.root:
			self.actual_window_height = event.height
			self.actual_window_width = event.width
			self.textbox["width"] = int(1/49 * event.width)
			self.text_chat["width"] = int(1/35 * event.width)
			self.text_chat["height"] = int(2/35 * event.height)
			self.text_chat.see("end")

	def micToggle(self, event, mute_button, mic_off, mic_on):
		global mic_status
		message = ttk.Label(self.root, font = FONT)
		if(mic_status):	#se il microfono è attivo
			mute_button.config(image = mic_off)	#cambia l'immagine
			mic_status = False	#setta il microfono come disattivo
			message.config(text = "listening no ")
		else:
			mute_button.config(image = mic_on)
			mic_status = True
			message.config(text = "listening yes")
		message.grid(column = 1, row = 1, sticky = "s")
		self.muteHandler()


	def camToggle(self, event, cam_button, cam_off, cam_on):
		global cam_status
		message = ttk.Label(self.root, font=FONT)
		if(cam_status):	#se la cam è attiva
			cam_button.config(image = cam_off)	#cambia l'immagine
			cam_status = False	#imposta la cam come disattivata
			message.config(text = "watching no ")
		else:
			cam_button.config(image = cam_on)
			cam_status = True
			message.config(text = "watching yes")
		message.grid(column = 1, row = 1, sticky = "sw")
		self.camHandler()

	def subtitlesToggle(self, event, subtitles_button, subtitles_off, subtitles_on):
		global subtitles_status
		if(str(subtitles_button["state"]) != "disabled"):
			message = ttk.Label(self.root, font = FONT)
			print(event)	#debug
			if(subtitles_status):
				subtitles_button.config(image = subtitles_off)
				subtitles_status = False
				message.config(text = "subtitles no ")
			else:
				subtitles_button.config(image = subtitles_on)
				subtitles_status = True
				message.config(text = "subtitles yes")
			message.grid(column = 0, row = 0, sticky = "se")

	def clearTextbox(self, event, text):
		if (text.get() == PLACEHOLDER):
			self.textbox.delete(0, "end")	#elimina tutto il contenuto

	def receiveMessage(self, name, message):
		self.text_chat.configure(state = 'normal')
		self.text_chat.insert("end", "<" + name + "> " + message + "\n")
		self.text_chat.configure(state = 'disabled')
		self.text_chat.see("end")

	#invio del messaggio nella chat di testo
	def sendMessage(self, event, text):
		if (text.get() != PLACEHOLDER and text.get()):	#quando viene premuto il bottone invia impedisce in inviare il placeholder o una stringa vuota
			self.messageHandler(text.get())
			self.text_chat.configure(state = 'normal')
			self.text_chat.insert("end", "<Tu> " + text.get() + "\n")
			self.text_chat.configure(state = 'disabled')
			self.text_chat.see("end")
			self.textbox.delete(0, "end")

	def addPlaceholder(self, event, text):
		if (not text.get()):
			self.textbox.insert(0, PLACEHOLDER)

	#invia il codice della stanza al server
	def getJoinCode(self, event, room_code):
		self.error.config(text = "")
		self.error.update()
		if (room_code.get() != "" and str(self.submit["state"]) != "disabled"):
			self.submit["state"] = "disabled"
			self.input_entry["state"] = "disabled"
			self.roomJoiner(room_code.get())

	#mostra un messaggio di errore nel caso non si riesca a unirsi ad una stanza
	def failJoin(self):
		self.error.config(text = "ERRORE: il server non risponde")
		self.submit["state"] = "enabled"
		self.input_entry["state"] = "enabled"

	# def computeSize(self):
	# 	self.cam_size = (int(math.ceil(16 * (40 - math.log(self.grid_size**2) * 6 - (self.width_screen / (self.actual_window_width/6))))),
	# 					int(math.ceil(9 * (40 - math.log(self.grid_size**2) * 6 - (self.height_screen / (self.actual_window_height/6))))))	#decide la grandezza delle webcam
		
	# 	temp_cams = list(self.cams.keys())
	# 	for cam in temp_cams:
	# 		hello = ImageTk.getimage(self.cams[cam].image)
	# 		hello = hello.resize(self.cam_size)
	# 		self.cams[cam].config(image = hello)
	# 		self.cams[cam].image = hello

	#aggiorna l'immagine di una webcam
	def updateCam(self, client_id, new_image_frame):
		self.cam_size = (int(math.ceil(16 * (40 - math.log(self.grid_size**2) * 6 - (self.width_screen / (self.actual_window_width/6))))),
						int(math.ceil(9 * (40 - math.log(self.grid_size**2) * 6 - (self.height_screen / (self.actual_window_height/6))))))	#decide la grandezza delle webcam
		try:
			if(client_id in self.cams):
				new_image = Image.open(io.BytesIO(new_image_frame))
				new_image = new_image.resize(self.cam_size)
				new_frame = ImageTk.PhotoImage(image = new_image)
				self.cams[client_id].config(image = new_frame)
				self.cams[client_id].image = new_frame
				self.computeSize()
		except RuntimeError as e:
			# print(e, "client eliminato durante il refresh dell'immagine")
			pass
		except AttributeError as e:
			pass
			# print(e, "byte dell'immagine non valdi")

	def addCam(self, client_id):
			if not self.cams_container:	#se la root non è pronta
				self.temp_client_list.append(client_id)	#salva il client appena collegato in una lista temporanea
			else:
				self.layoutCam(client_id)	#altrimenti disegna la webcam

	def layoutCam(self, client_id):
		self.cams[client_id] = ttk.Label(self.cams_container)
		self.placeCams()

	def removeCam(self, client_id):
		self.cams[client_id].grid_forget()
		self.cams.pop(client_id, None)
		self.placeCams()

	#metodo che riorganizza le posizioni delle webcam
	def placeCams(self):
		column_number = 0
		row_number = 0
		temp_cams = list(self.cams.keys())
		cam_number = len(temp_cams)
		if (cam_number > (self.grid_size**2)):
			self.grid_size += 1
			self.counter_size += 4.10
		elif (cam_number <= ((self.grid_size - 1)**2)):
			self.grid_size -= 1
			self.counter_size -= 4.10

		for cam in temp_cams:
			self.cams[cam].grid(column = column_number, row = row_number, columnspan = 1)

			if (column_number == (self.grid_size - 1)):
				row_number += 1
				column_number = 0
			else: column_number += 1

	#crea il layout della finestra dopo che si è entrati in una stanza
	def createWindow(self):
		self.dialog.pack_forget()

		#creazione delle colonne e delle righe
		self.root.columnconfigure(0, weight = 1)
		self.root.columnconfigure(1, weight = 17)
		self.root.columnconfigure(2, weight = 1)
		self.root.rowconfigure(0, weight = 10)
		self.root.rowconfigure(1, weight = 1)

		#creazione delle icone
		mic_off = tk.PhotoImage(file = "assets/mic_off.png")
		mic_on = tk.PhotoImage(file = "assets/mic.png")
		cam_off = tk.PhotoImage(file = "assets/cam_off.png")
		cam_on = tk.PhotoImage(file = "assets/cam.png")
		self.send = tk.PhotoImage(file = "assets/send_message.png")
		self.filters = tk.PhotoImage(file = "assets/filters.png")
		self.mask = tk.PhotoImage(file = "assets/mask.png")
		subtitles_off = tk.PhotoImage(file = "assets/subtitles_off.png")
		subtitles_on = tk.PhotoImage(file = "assets/subtitles.png")
		

		communication_tools = ttk.Frame(self.root)	#frame che contiene i bottoni per il mute e lo spegnimento della cam

		mute_button = ttk.Button(communication_tools, image = mic_on)
		mute_button.bind("<Control-m>", lambda event:self.micToggle(event, mute_button, mic_off, mic_on))	#shortcut: ctrl + m
		mute_button.bind("<ButtonRelease>", lambda event:self.micToggle(event, mute_button, mic_off, mic_on))	#chiama la funzione anche con il click del mouse quando rilasciato
		mute_button.focus()	#rende il bottone sotto focus di default (per far funzionare la shortcut il bottone deve essere in focus)
		mute_button.pack(side = "right", padx = 5, pady = 1)

		cam_button = ttk.Button(communication_tools, image = cam_on)
		cam_button.bind("<Control-w>", lambda event:self.camToggle(event, cam_button, cam_off, cam_on))	#shortcut: ctrl + m
		cam_button.bind("<ButtonRelease>", lambda event:self.camToggle(event, cam_button, cam_off, cam_on))	#chiama la funzione anche con il click del mouse quando rilasciato
		cam_button.pack(side = "right", pady = 1)

		communication_tools.grid(column = 1, row = 1)

		send_message_wrapper = ttk.Frame(self.root)	#frame che contiene la entry del messaggio e il bottone di invio
		text = tk.StringVar()	#variabile dove andrà salvato il testo della entry
		self.textbox = ttk.Entry(send_message_wrapper, textvariable = text, width = 39, font = ("Monospace", 10))
		self.textbox.insert(0, PLACEHOLDER)	# inserire del testo che fungerà da placeholder
		self.textbox.bind("<FocusIn>", lambda event:self.clearTextbox(event, text))
		self.textbox.bind("<FocusOut>", lambda event:self.addPlaceholder(event, text))
		self.textbox.pack(side = "left", ipady = 3)

		send_button = ttk.Button(send_message_wrapper, image = self.send)
		send_button.bind("<ButtonRelease>", lambda event:self.sendMessage(event, text))
		self.root.bind("<Return>", lambda event:self.sendMessage(event, text))
		send_button.pack(padx = 5, pady = 1)
		send_message_wrapper.grid(column = 2, row = 1, sticky = "e")

		tools = ttk.Frame(self.root)	#frame che contiene tutti i tools secondari

		filters_button= ttk.Button(tools, image = self.filters)
		mask_button= ttk.Button(tools, image = self.mask)
		subtitles_button= ttk.Button(tools, image = subtitles_off)
		subtitles_button.bind("<ButtonRelease>", lambda event:self.subtitlesToggle(event, subtitles_button, subtitles_off, subtitles_on))

		filters_button.pack(side = "top", pady = 10)
		mask_button.pack(side = "top")
		subtitles_button.pack(side = "top", pady = 10)

		tools.grid(column = 0, row = 0)

		self.cams_container = ttk.Frame(self.root)
		self.cams_container.grid(column = 1, row = 0)

		for i in self.temp_client_list:
			self.layoutCam(i)
		self.temp_client_list.clear()
		
		self.chat = ttk.Frame(self.root)

		self.text_chat = tk.Text(self.chat, width = 51, font = ("Monospace", 9), highlightthickness = 0, borderwidth = 0, height = 1/18 * self.height_screen)
		self.scrollbar = ttk.Scrollbar(self.chat, command = self.text_chat.yview, orient = "vertical")
		self.text_chat.configure(yscrollcommand = self.scrollbar.set)

		self.chat.columnconfigure(0, weight = 1)

		self.scrollbar.grid(column = 1, row = 0, sticky="sn")
		self.text_chat.configure(state = 'disabled')
		self.text_chat.grid(column = 0, row = 0, sticky="snew")

		self.chat.grid(column = 2, row = 0, sticky = "se")

		self.root.bind("<Configure>", self.resizeWindow)
		# ttk.Label(self.root).grid(column = 0, row = 0, rowspan = 2, sticky="ewns")
		# ttk.Label(self.root, text = "cam zone", background = "red", foreground = "white").grid(column = 1, row = 0, sticky="ewns")
		# ttk.Label(self.root, background = "red").grid(column = 2, row = 0, sticky="ewns")
		# ttk.Label(self.root).grid(column = 1, row = 1, sticky="ewns")
		# ttk.Label(self.root).grid(column = 2, row = 1, sticky="ewns")
