// ==========================================
// EDGEGUARD ESP32 FIRMWARE
// ==========================================

// We will assign the actual GPIO pins
// after checking the physical MTL-5 modules.

// Example placeholders
int NORTH_RED = 25;
int NORTH_YELLOW = 26;
int NORTH_GREEN = 27;

int SOUTH_RED = 14;
int SOUTH_YELLOW = 12;
int SOUTH_GREEN = 13;

int EAST_RED = 32;
int EAST_YELLOW = 33;
int EAST_GREEN = 23;

int WEST_RED = 19;
int WEST_YELLOW = 18;
int WEST_GREEN = 5;


// ==========================================
// SETUP
// ==========================================

void setup() {

  Serial.begin(115200);

  // North
  pinMode(NORTH_RED, OUTPUT);
  pinMode(NORTH_YELLOW, OUTPUT);
  pinMode(NORTH_GREEN, OUTPUT);

  // South
  pinMode(SOUTH_RED, OUTPUT);
  pinMode(SOUTH_YELLOW, OUTPUT);
  pinMode(SOUTH_GREEN, OUTPUT);

  // East
  pinMode(EAST_RED, OUTPUT);
  pinMode(EAST_YELLOW, OUTPUT);
  pinMode(EAST_GREEN, OUTPUT);

  // West
  pinMode(WEST_RED, OUTPUT);
  pinMode(WEST_YELLOW, OUTPUT);
  pinMode(WEST_GREEN, OUTPUT);

  // Start in safe state
  allRed();

  Serial.println("EDGEGUARD ESP32 READY");
}


// ==========================================
// LOOP
// ==========================================

void loop() {

  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');

    command.trim();

    if (command == "NS_GREEN") {
      nsGreen();
    }

    else if (command == "NS_YELLOW") {
      nsYellow();
    }

    else if (command == "EW_GREEN") {
      ewGreen();
    }

    else if (command == "EW_YELLOW") {
      ewYellow();
    }

    else if (command == "ALL_RED") {
      allRed();
    }

    else {
      Serial.println("UNKNOWN COMMAND");
    }
  }
}


// ==========================================
// NORTH-SOUTH GREEN
// ==========================================

void nsGreen() {

  allRed();

  digitalWrite(NORTH_RED, LOW);
  digitalWrite(NORTH_GREEN, HIGH);

  digitalWrite(SOUTH_RED, LOW);
  digitalWrite(SOUTH_GREEN, HIGH);

  Serial.println("NS_GREEN");
}


// ==========================================
// NORTH-SOUTH YELLOW
// ==========================================

void nsYellow() {

  allRed();

  digitalWrite(NORTH_YELLOW, HIGH);
  digitalWrite(SOUTH_YELLOW, HIGH);

  Serial.println("NS_YELLOW");
}


// ==========================================
// EAST-WEST GREEN
// ==========================================

void ewGreen() {

  allRed();

  digitalWrite(EAST_RED, LOW);
  digitalWrite(EAST_GREEN, HIGH);

  digitalWrite(WEST_RED, LOW);
  digitalWrite(WEST_GREEN, HIGH);

  Serial.println("EW_GREEN");
}


// ==========================================
// EAST-WEST YELLOW
// ==========================================

void ewYellow() {

  allRed();

  digitalWrite(EAST_YELLOW, HIGH);
  digitalWrite(WEST_YELLOW, HIGH);

  Serial.println("EW_YELLOW");
}


// ==========================================
// ALL RED
// ==========================================

void allRed() {

  digitalWrite(NORTH_RED, HIGH);
  digitalWrite(NORTH_YELLOW, LOW);
  digitalWrite(NORTH_GREEN, LOW);

  digitalWrite(SOUTH_RED, HIGH);
  digitalWrite(SOUTH_YELLOW, LOW);
  digitalWrite(SOUTH_GREEN, LOW);

  digitalWrite(EAST_RED, HIGH);
  digitalWrite(EAST_YELLOW, LOW);
  digitalWrite(EAST_GREEN, LOW);

  digitalWrite(WEST_RED, HIGH);
  digitalWrite(WEST_YELLOW, LOW);
  digitalWrite(WEST_GREEN, LOW);

  Serial.println("ALL_RED");
}