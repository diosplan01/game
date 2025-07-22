import serial
import threading
import time
from config import SERIAL_PORT, BAUD_RATE, NOTE_TIMEOUT

class SerialReader:
    def __init__(self):
        self.ser = None
        self.teclas = [False] * 4
        self.ultimo_pulso = [0] * 4
        self.hilo = None
        self.corriendo = False

    def start(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
            self.corriendo = True
            self.hilo = threading.Thread(target=self.leer_serial, daemon=True)
            self.hilo.start()
            print(f"Puerto serie {SERIAL_PORT} abierto correctamente.")
        except serial.SerialException:
            print(f"No se pudo abrir el puerto serie {SERIAL_PORT}.")
            self.ser = None

    def stop(self):
        self.corriendo = False
        if self.hilo:
            self.hilo.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Puerto serie {SERIAL_PORT} cerrado.")

    def leer_serial(self):
        while self.corriendo:
            if self.ser and self.ser.in_waiting:
                try:
                    data = self.ser.readline().decode().strip()
                    if data.isdigit():
                        i = int(data)
                        if 0 <= i < len(self.teclas):
                            self.teclas[i] = True
                            self.ultimo_pulso[i] = time.time()
                except Exception as e:
                    print(f"Error al leer del puerto serie: {e}")
            time.sleep(0.01)

    def get_key_states(self):
        ahora = time.time()
        for i in range(4):
            if self.teclas[i] and (ahora - self.ultimo_pulso[i]) > NOTE_TIMEOUT:
                self.teclas[i] = False
        return self.teclas

if __name__ == '__main__':
    # Ejemplo de uso
    reader = SerialReader()
    reader.start()
    try:
        while True:
            teclas = reader.get_key_states()
            if any(teclas):
                print(f"Estado de las teclas: {teclas}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        reader.stop()
        print("Programa terminado.")
