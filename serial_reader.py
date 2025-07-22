import serial
import threading
import time
from config import SERIAL_PORT, BAUD_RATE

class SerialReader:
    """
    This class handles the serial communication with the ESP32.
    It runs in a separate thread to avoid blocking the main game loop.
    """
    def __init__(self):
        self.ser = None
        self.teclas = [False] * 4
        self.last_teclas = [False] * 4
        self.hilo = None
        self.corriendo = False

    def start(self):
        """
        Starts the serial reader thread.
        """
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
            self.corriendo = True
            self.hilo = threading.Thread(target=self.leer_serial, daemon=True)
            self.hilo.start()
            print(f"Puerto serie {SERIAL_PORT} abierto correctamente.")
        except serial.SerialException:
            print(f"No se pudo abrir el puerto serie {SERIAL_PORT}.")
            self.ser = None

    def stop(self):
        """
        Stops the serial reader thread.
        """
        self.corriendo = False
        if self.hilo:
            self.hilo.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Puerto serie {SERIAL_PORT} cerrado.")

    def leer_serial(self):
        """
        Reads data from the serial port and updates the key states.
        """
        while self.corriendo:
            if self.ser and self.ser.in_waiting:
                try:
                    data = self.ser.readline().decode().strip()
                    if data.isdigit():
                        i = int(data)
                        if 0 <= i < len(self.teclas):
                            self.teclas[i] = True
                except Exception as e:
                    print(f"Error al leer del puerto serie: {e}")
            else:
                # No data in buffer, so all keys are released
                self.teclas = [False] * 4
            time.sleep(0.01)

    def get_key_states(self):
        """
        Returns the current state of the keys.
        """
        return self.teclas

    def get_key_presses(self):
        """
        Returns a list of keys that have been pressed since the last time this method was called.
        This is used to detect single key presses and avoid repeated signals.
        """
        key_presses = []
        for i in range(len(self.teclas)):
            if self.teclas[i] and not self.last_teclas[i]:
                key_presses.append(i)
        self.last_teclas = list(self.teclas)
        return key_presses

if __name__ == '__main__':
    # Example usage
    reader = SerialReader()
    reader.start()
    try:
        while True:
            key_presses = reader.get_key_presses()
            if key_presses:
                print(f"Key presses: {key_presses}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        reader.stop()
        print("Program finished.")
