
const int NORTH_R = 25, NORTH_Y = 26, NORTH_G = 27;
const int EAST_R  = 18, EAST_Y  = 19, EAST_G  = 21;
const int SOUTH_R = 22, SOUTH_Y = 23, SOUTH_G = 5;
const int WEST_R  = 13, WEST_Y  = 14, WEST_G  = 12;

const int RED_PINS[] = {NORTH_R, EAST_R, SOUTH_R, WEST_R};
const int YELLOW_PINS[] = {NORTH_Y, EAST_Y, SOUTH_Y, WEST_Y};
const int GREEN_PINS[] = {NORTH_G, EAST_G, SOUTH_G, WEST_G};

String command = "";
unsigned long lastHeartbeat = 0;
const unsigned long HEARTBEAT_TIMEOUT = 3000;
bool failsafeActive = false;

void allOff() {
  for (int pin : RED_PINS) digitalWrite(pin, LOW);
  for (int pin : YELLOW_PINS) digitalWrite(pin, LOW);
  for (int pin : GREEN_PINS) digitalWrite(pin, LOW);
}

void allRed() {
  allOff();
  for (int pin : RED_PINS) digitalWrite(pin, HIGH);
}

void setNSGreen() {
  allRed();
  digitalWrite(NORTH_R, LOW);
  digitalWrite(SOUTH_R, LOW);
  digitalWrite(NORTH_G, HIGH);
  digitalWrite(SOUTH_G, HIGH);
}

void setNSYellow() {
  allRed();
  digitalWrite(NORTH_R, LOW);
  digitalWrite(SOUTH_R, LOW);
  digitalWrite(NORTH_Y, HIGH);
  digitalWrite(SOUTH_Y, HIGH);
}

void setEWGreen() {
  allRed();
  digitalWrite(EAST_R, LOW);
  digitalWrite(WEST_R, LOW);
  digitalWrite(EAST_G, HIGH);
  digitalWrite(WEST_G, HIGH);
}

void setEWYellow() {
  allRed();
  digitalWrite(EAST_R, LOW);
  digitalWrite(WEST_R, LOW);
  digitalWrite(EAST_Y, HIGH);
  digitalWrite(WEST_Y, HIGH);
}

void setup() {
  Serial.begin(115200);

  for (int pin : RED_PINS) pinMode(pin, OUTPUT);
  for (int pin : YELLOW_PINS) pinMode(pin, OUTPUT);
  for (int pin : GREEN_PINS) pinMode(pin, OUTPUT);

  allRed();
  lastHeartbeat = millis();
  Serial.println("EDGEGUARD READY");
}

void loop() {
  while (Serial.available() > 0) {
    char incoming = Serial.read();

    if (incoming == '\n') {
      command.trim();

      if (command == "HEARTBEAT") {
        lastHeartbeat = millis();
        failsafeActive = false;
        Serial.println("ACK:HEARTBEAT");
      } else if (command.length() > 0) {
        if (millis() - lastHeartbeat > HEARTBEAT_TIMEOUT) {
          allRed();
          failsafeActive = true;
          Serial.println("ERROR: HEARTBEAT REQUIRED");
        } else if (command == "ALL_RED") {
          allRed();
          Serial.println("ACK:ALL_RED");
        } else if (command == "NS_GREEN") {
          setNSGreen();
          Serial.println("ACK:NS_GREEN");
        } else if (command == "NS_YELLOW") {
          setNSYellow();
          Serial.println("ACK:NS_YELLOW");
        } else if (command == "EW_GREEN") {
          setEWGreen();
          Serial.println("ACK:EW_GREEN");
        } else if (command == "EW_YELLOW") {
          setEWYellow();
          Serial.println("ACK:EW_YELLOW");
        } else {
          Serial.println("ERROR: UNKNOWN COMMAND");
        }
      }

      command = "";
    } else if (incoming != '\r') {
      command += incoming;
      if (command.length() > 40) {
        command = "";
        allRed();
        Serial.println("ERROR: COMMAND TOO LONG");
      }
    }
  }

  if (millis() - lastHeartbeat > HEARTBEAT_TIMEOUT) {
    allRed();
    if (!failsafeActive) {
      Serial.println("FAILSAFE: HEARTBEAT_LOST - ALL RED");
      failsafeActive = true;
    }
  }
}
