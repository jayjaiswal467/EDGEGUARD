
import time
from serial_comm import SerialCommunicator

PORT = "COM3"

esp32 = SerialCommunicator(PORT)

try:
    esp32.connect()

    # Allow the ESP32 to restart after opening serial
    time.sleep(2)

    print("\nTesting EDGEGUARD physical traffic light...\n")

    esp32.send_command("ALL_RED")
    time.sleep(2)

    esp32.send_command("NS_GREEN")
    time.sleep(3)

    esp32.send_command("NS_YELLOW")
    time.sleep(2)

    esp32.send_command("EW_GREEN")
    time.sleep(3)

    esp32.send_command("EW_YELLOW")
    time.sleep(2)

    esp32.send_command("ALL_RED")
    time.sleep(2)

    print("\nHardware command test completed.")

except Exception as error:
    print(f"\nHardware test failed: {error}")

finally:
    esp32.close()
