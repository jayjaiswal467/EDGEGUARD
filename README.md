# EDGEGUARD

## AI-Powered Adaptive Traffic & Emergency Response System

EdgeGuard is a hardware-in-the-loop traffic management system designed
to demonstrate adaptive traffic signal control and emergency vehicle
prioritization.

## Phase 1

Phase 1 focuses on building a physical four-way traffic intersection
controlled by an ESP32.

### Features

- ESP32-based traffic signal control
- Four physical traffic lights
- Traffic signal state machine
- Python traffic controller
- USB serial communication
- Adaptive green timing
- Simulated emergency priority

## Architecture

Laptop
↓
Python Controller
↓
USB Serial
↓
ESP32
↓
GPIO
↓
Traffic Lights

## Hardware

- ESP32 DevKit V1
- SP Electron MTL-5 traffic-light modules
- Breadboard
- Jumper wires

## Software

- C/C++
- Arduino IDE
- Python
- PySerial

## Project Status

Phase 1 — In Development

## Future Development

Phase 2 will extend the prototype with:

- Computer vision
- Vehicle detection
- Object tracking
- Traffic analytics
- Adaptive signal optimization
- Backend services
- React dashboard
- Traffic simulation
- RAG and AI operations copilot
