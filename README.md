# EDGEGUARD

## AI-Powered Adaptive Traffic & Emergency Response System

EDGEGUARD is a hardware-in-the-loop intelligent traffic management system that combines **computer vision, adaptive traffic logic, deterministic safety control, serial communication, and embedded hardware** to demonstrate real-time adaptive traffic signal control.

The system analyzes live camera footage using **YOLOv8 and OpenCV**, estimates traffic density across four directions, determines the direction requiring priority, calculates adaptive green-light duration, validates signal transitions through a deterministic state machine, and communicates the resulting commands to an **ESP32** for physical traffic-light control.

> **Core principle:** AI is used for perception and traffic estimation. It does not directly control the traffic lights. All hardware actions pass through deterministic safety logic before reaching the ESP32.

---

## Project Status

**Current Phase:** Phase 1 — Hardware-in-the-Loop Adaptive Traffic Control  
**Status:** In Development

### Current Progress

| Component | Status |
|---|---|
| OpenCV camera input | ✅ Implemented |
| YOLOv8 vehicle detection | ✅ Implemented |
| Vehicle class filtering | ✅ Implemented |
| N/S/E/W ROI detection | ✅ Implemented |
| Directional vehicle counting | ✅ Implemented |
| NS/EW traffic aggregation | ✅ Implemented |
| Traffic priority calculation | ✅ Implemented |
| Adaptive green timing | ✅ Implemented |
| Perception watchdog | ✅ Implemented |
| Deterministic traffic state machine | ✅ Implemented |
| Invalid transition protection | ✅ Implemented |
| Python serial communication layer | ✅ Implemented |
| Heartbeat transmission logic | ✅ Implemented |
| PC-side integration test | ✅ Passed |
| ESP32 firmware | 🔄 Pending |
| Physical GPIO control | 🔄 Pending |
| MTL-5 hardware integration | 🔄 Pending |
| Physical traffic-light testing | 🔄 Pending |
| Emergency priority module | 🔄 Pending |
| Performance benchmark module | 🔄 Pending |

---

# 1. System Overview

EDGEGUARD follows the pipeline:

```text
                    CAMERA
                       │
                       ▼
              ┌─────────────────┐
              │     OpenCV      │
              │ Frame Capture   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     YOLOv8      │
              │ Vehicle Detection│
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  ROI Direction  │
              │   Classification│
              └────────┬────────┘
                       │
                 N / S / E / W
                       │
                       ▼
              ┌─────────────────┐
              │ Traffic Logic   │
              │ Priority + Time │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Safety State    │
              │    Machine      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Serial / USB    │
              │  Communication  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │      ESP32      │
              │  GPIO Control   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    MTL-5        │
              │ Traffic Signals │
              └─────────────────┘
