# # https://www.pythontutorial.net/tkinter/tkinter-hello-world/
# # https://www.pythontutorial.net/tkinter/tkinter-grid/
# # pip3 install ttkthemes
# # pip3 install pillow
# pip3 install imutils
# pip3 install opencv-python
# # keybinds: https://www.pythontutorial.net/tkinter/tkinter-event-binding/
# #TODO fixare bottone che si preme solo in focus
# #TODO placeCam con remove 
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from ttkthemes import ThemedTk
import io


FONT = ("Monospace", 11)
PLACEHOLDER = "Inserisci un messaggio... "
CAM_4_SIZE = (608, 342)
CAM_6_SIZE = (480, 270)
CAM_9_SIZE = (416, 243)
CAM_16_SIZE = (320, 180)
CAM_25_SIZE = (240, 135)
mic_status = False
cam_status = False
subtitles_status = False

class Gui:
	def __init__(self, roomJoiner):
		self.cams_container = None
		self.temp_client_list = []	#lista che conterrà le webcam temporanee durante la crezione della root
		self.cams = {}	#dizionario che conterrà le webcam dei client presenti
		self.roomJoiner = roomJoiner
		self.root = ThemedTk(theme = "breeze")	#finestra padre con tema breeze
		self.root.title("Mitis")
		width_screen = self.root.winfo_screenwidth()	# larghezza dello schermo
		heigth_screen = self.root.winfo_screenheight() # altezza dello schermo
		screen_size = str(width_screen) + "x" + str(heigth_screen)
		self.root.geometry(screen_size)
		self.root.minsize(800, 500)	#grandezza minima finestra

		self.dialog = ttk.Frame(self.root)
		dialog_text = ttk.Label(self.dialog, text = "inserisci codice stanza:", font = FONT)
		dialog_text.pack()
		room_code = tk.StringVar()
		self.input_entry= ttk.Entry(self.dialog, textvariable = room_code, font = FONT)
		self.input_entry.pack()
		self.submit = ttk.Button(self.dialog, text = "JOIN")
		self.submit.pack(pady = 5)
		self.submit.bind("<ButtonRelease>", lambda event:self.getJoinCode(event, room_code))
		self.error = ttk.Label(self.dialog, text = "", foreground = "red", font = FONT)
		self.error.pack()
		self.dialog.pack(expand = True)

	def micToggle(self, event, mute_button, mic_off, mic_on, input_source = "none"):
		global mic_status
		if(str(mute_button["state"]) != "disabled"):
			message = ttk.Label(self.root, font = FONT)
			print(input_source)	#debug
			print(event)	#debug
			if(mic_status):	#se il microfono è attivo
				mute_button.config(image = mic_off)	#cambia l'immagine
				mic_status = False	#setta il microfono come disattivo
				message.config(text = "listening no ")
			else:
				mute_button.config(image = mic_on)
				mic_status = True
				message.config(text = "listening yes")
			message.grid(column = 1, row = 1, sticky = "s")

	def camToggle(self, event, cam_button, cam_off, cam_on, input_source = "none"):
		global cam_status
		if(str(cam_button["state"]) != "disabled"):
			message = ttk.Label(self.root, font=FONT)
			print(input_source)	#debug
			print(event)	#debug
			if(cam_status):	#se la cam è attiva
				cam_button.config(image = cam_off)	#cambia l'immagine
				cam_status = False	#imposta la cam come disattivata
				message.config(text = "watching no ")
			else:
				cam_button.config(image = cam_on)
				cam_status = True
				message.config(text = "watching yes")
			message.grid(column = 1, row = 1, sticky = "sw")

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

	def clearTextbox(self, event, textbox, text):
		if (text.get() == PLACEHOLDER):
			textbox.delete(0, "end")	#elimina tutto il contenuto

	#invio del messaggio nella chat di testo
	def sendMessage(self, event, textbox, text):
		if (text.get() != PLACEHOLDER):	#quando viene premuto il bottone invia impedisce in inviare il placeholder
			#TODO invio del messaggio
			print(text.get())
		textbox.delete(0, "end")
		textbox.insert(0, PLACEHOLDER)

	def addPlaceholder(self, event, textbox, text):
		if (text.get() == ""):
			textbox.insert(0, PLACEHOLDER)

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

	#aggiorna l'immagine di una webcam
	def updateCam(self, client_id, new_image_frame):
		try:
			if(client_id in self.cams):
				new_image = Image.open(io.BytesIO(new_image_frame))
				new_image = new_image.resize(self.cam_size)
				new_frame = ImageTk.PhotoImage(image = new_image)
				self.cams[client_id].config(image = new_frame)
				self.cams[client_id].image = new_frame
		except KeyError as e:
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
		cam_number = len(self.cams)
		counter = 1	#counter per la gestione delle webcam centrate
		column_limit = 0	#ultima colonna scelta in base al numero di cam
		if (cam_number <= 4):
			self.cam_size = CAM_4_SIZE
			column_limit = 1
			center_3_cam = True
			center_5_cam = False

		elif (cam_number <= 6):
			self.cam_size = CAM_6_SIZE
			column_limit = 1
			center_3_cam = False
			center_5_cam = True
		
		elif(cam_number <= 9):
			self.cam_size = CAM_9_SIZE
			column_limit = 2

		elif(cam_number <= 16):
			self.cam_size = CAM_16_SIZE
			column_limit = 3
		
		elif(cam_number <= 25):
			self.cam_size = CAM_25_SIZE
			column_limit = 4

		for cam in self.cams:
			if ((cam_number == 3 or cam_number == 5) and column_number == 0 and (row_number == 1 or row_number == 2)):	#gestisce il caso in cui le webcan stanno centrate
				if(center_3_cam and counter == 3):	#webcam 3
					self.cams[cam].grid(column = column_number, row = row_number, columnspan = 2)
				elif(center_5_cam and counter == 5):	#webcam 5
					self.cams[cam].grid(column = column_number, row = row_number, columnspan = 2)
			else:
				self.cams[cam].grid(column = column_number, row = row_number, columnspan = 1)

			if (column_number == column_limit):
				row_number += 1
				column_number = 0
			else: column_number += 1
			counter += 1


	#crea il layout della finestra dopo che si è entrati in una stanza
	def createWindow(self):
		self.dialog.pack_forget()

		#creazione delle colonne e delle righe
		self.root.columnconfigure(0, weight = 1)
		self.root.columnconfigure(1, weight = 15)
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

		mute_button = ttk.Button(communication_tools, image = mic_off)
		mute_button.bind("<Control-m>", lambda event:self.micToggle(event, mute_button, mic_off, mic_on, "il microfono è stato mutato dalla shortcut"))	#shortcut: ctrl + m
		mute_button.bind("<ButtonRelease>", lambda event:self.micToggle(event, mute_button, mic_off, mic_on, "il microfono è stato mutato dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
		mute_button.focus()	#rende il bottone sotto focus di default (per far funzionare la shortcut il bottone deve essere in focus)
		mute_button.pack(side = "right", padx = 5)

		cam_button = ttk.Button(communication_tools, image = cam_off)
		cam_button.bind("<Control-w>", lambda event:self.camToggle(event, cam_button, cam_off, cam_on, "la webcam è stata mutata dalla shortcut"))	#shortcut: ctrl + m
		cam_button.bind("<ButtonRelease>", lambda event:self.camToggle(event, cam_button, cam_off, cam_on, "la webcam è stata mutata dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
		cam_button.pack()

		communication_tools.grid(column = 1, row = 1)

		send_message_wrapper = ttk.Frame(self.root)	#frame che contiene la entry del messaggio e il bottone di invio
		text = tk.StringVar()	#variabile dove andrà salvato il testo della entry
		textbox = ttk.Entry(send_message_wrapper, textvariable = text, width = 45, font = FONT)
		textbox.insert(0, PLACEHOLDER)	# inserire del testo che fungerà da placeholder
		textbox.bind("<FocusIn>", lambda event:self.clearTextbox(event, textbox, text))
		textbox.bind("<FocusOut>", lambda event:self.addPlaceholder(event, textbox, text))
		textbox.pack(side = "left", ipady = 3)

		send_button = ttk.Button(send_message_wrapper, image = self.send)
		send_button.bind("<ButtonRelease>", lambda event:self.sendMessage(event, textbox, text))
		send_button.pack(padx = 5, pady = 1)
		send_message_wrapper.grid(column = 2, row = 1, sticky = "ne")

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
		# ttk.Label(self.root).grid(column = 0, row = 0, rowspan = 2, sticky="ewns")
		# # ttk.Label(self.root, text = "cam zone", background = "red", foreground = "white").grid(column = 1, row = 0, sticky="ewns")
		# ttk.Label(self.root).grid(column = 2, row = 0, sticky="ewns")
		# ttk.Label(self.root).grid(column = 1, row = 1, sticky="ewns")
		# ttk.Label(self.root).grid(column = 2, row = 1, sticky="ewns")
