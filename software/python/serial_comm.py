import time
import threading
import serial


class SerialCommunicator:

    BAUD_RATE = 115200

    VALID_COMMANDS = {
        "NS_GREEN",
        "NS_YELLOW",
        "EW_GREEN",
        "EW_YELLOW",
        "ALL_RED",
    }

    def __init__(self, port, baud_rate=BAUD_RATE, heartbeat_interval=1.0):
        self.port = port
        self.baud_rate = baud_rate
        self.heartbeat_interval = heartbeat_interval

        self.serial_connection = None

        self.heartbeat_thread = None
        self.heartbeat_running = False

    def connect(self):
        self.serial_connection = serial.Serial(
            self.port,
            self.baud_rate,
            timeout=1
        )

        print(
            f"[SERIAL] Connected to {self.port} "
            f"at {self.baud_rate} baud"
        )

    def send_command(self, command):

        if command not in self.VALID_COMMANDS:
            raise ValueError(
                f"Invalid command: {command}"
            )

        if self.serial_connection is None:
            raise RuntimeError(
                "Serial connection is not established"
            )

        message = command + "\n"

        self.serial_connection.write(
            message.encode("utf-8")
        )

        print(f"[SERIAL] Sent: {command}")

    def start_heartbeat(self):

        if self.serial_connection is None:
            raise RuntimeError(
                "Serial connection is not established"
            )

        if self.heartbeat_running:
            return

        self.heartbeat_running = True

        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        )

        self.heartbeat_thread.start()

        print("[SERIAL] Heartbeat started")

    def _heartbeat_loop(self):

        while self.heartbeat_running:

            try:
                self.serial_connection.write(
                    b"HEARTBEAT\n"
                )

            except Exception as error:

                print(
                    f"[SERIAL] Heartbeat error: {error}"
                )

                self.heartbeat_running = False
                break

            time.sleep(self.heartbeat_interval)

    def stop_heartbeat(self):

        self.heartbeat_running = False

        if self.heartbeat_thread is not None:
            self.heartbeat_thread.join(timeout=2)

        print("[SERIAL] Heartbeat stopped")

    def close(self):

        self.stop_heartbeat()

        if self.serial_connection is not None:
            self.serial_connection.close()
            self.serial_connection = None

        print("[SERIAL] Connection closed")


if __name__ == "__main__":

    print("EDGEGUARD Serial Communication Module")
    print("--------------------------------------")

    print("Baud rate:", SerialCommunicator.BAUD_RATE)

    print("\nValid commands:")

    for command in SerialCommunicator.VALID_COMMANDS:
        print("-", command)

    print("\nHeartbeat interval: 1 second")

    print("\nSerial module loaded successfully.")