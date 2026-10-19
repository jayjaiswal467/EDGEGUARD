
import time
import cv2
import numpy as np
from ultralytics import YOLO

from traffic_logic import get_traffic_decision
from controller import TrafficController, TrafficState
from serial_comm import SerialCommunicator


# ==================== CONFIGURATION ====================

SERIAL_PORT = "COM3"
BAUD_RATE = 115200
CAMERA_INDEX = 0
MODEL_PATH = "yolov8n.pt"

CONFIDENCE_THRESHOLD = 0.10
INFERENCE_TIMEOUT = 5.0

YELLOW_DURATION = 2.0
ALL_RED_DURATION = 1.0

# COCO vehicle class IDs: car, motorcycle, bus, truck
VEHICLE_CLASSES = {2, 3, 5, 7}

# =======================================================


def point_in_roi(point, roi):
    """Return True if a point lies inside or on an ROI polygon."""
    return cv2.pointPolygonTest(
        roi, (float(point[0]), float(point[1])), False
    ) >= 0


def create_rois(width, height):
    """
    Create four non-overlapping image regions.

    These are initial screen regions, not calibrated road lanes.
    Adjust them to match your camera's actual view.
    """
    mid_x = width // 2
    mid_y = height // 2

    rois = {
        "N": np.array([
            [0, 0], [mid_x, 0], [mid_x, mid_y], [0, mid_y]
        ], dtype=np.int32),

        "E": np.array([
            [mid_x, 0], [width - 1, 0],
            [width - 1, mid_y], [mid_x, mid_y]
        ], dtype=np.int32),

        "S": np.array([
            [mid_x, mid_y], [width - 1, mid_y],
            [width - 1, height - 1], [mid_x, height - 1]
        ], dtype=np.int32),

        "W": np.array([
            [0, mid_y], [mid_x, mid_y],
            [mid_x, height - 1], [0, height - 1]
        ], dtype=np.int32),
    }

    return rois


def count_vehicles(results, rois):
    """Count detected vehicle bounding-box centers in each region."""
    counts = {"N": 0, "S": 0, "E": 0, "W": 0}
    detections = []

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            if class_id not in VEHICLE_CLASSES:
                continue

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

            # The regions do not overlap, so each center is counted once.
            for direction, roi in rois.items():
                if point_in_roi(center, roi):
                    counts[direction] += 1
                    detections.append(
                        (int(x1), int(y1), int(x2), int(y2),
                         center, direction, confidence, class_id)
                    )
                    break

    return counts, detections


def state_command(state):
    """Convert a controller state to a serial command."""
    valid_commands = {
        "NS_GREEN", "NS_YELLOW",
        "EW_GREEN", "EW_YELLOW", "ALL_RED"
    }

    command = str(state)

    if command not in valid_commands:
        raise ValueError(f"Unsupported controller state: {command}")

    return command


def green_duration_for(priority, decision):
    """Get the adaptive green duration for the selected road axis."""
    if priority == "NS":
        return float(decision["ns_green"])

    if priority == "EW":
        return float(decision["ew_green"])

    # If there is no traffic, use the minimum green duration.
    return float(decision["ns_green"])


def main():
    esp32 = None
    camera = None
    model = None
    last_decision = None

    try:
        print("[EDGEGUARD] Loading YOLO model...")
        model = YOLO(MODEL_PATH)

        print(f"[EDGEGUARD] Connecting to ESP32 on {SERIAL_PORT}...")
        esp32 = SerialCommunicator(SERIAL_PORT)
        esp32.connect()

        # Allow the ESP32 to reset after opening the serial port.
        time.sleep(2)
        esp32.start_heartbeat()

        # Establish a known initial signal state.
        esp32.send_command("ALL_RED")
        print("[SAFETY] ALL_RED commanded")

        camera = cv2.VideoCapture(CAMERA_INDEX)

        if not camera.isOpened():
            raise RuntimeError(
                f"Could not open camera index {CAMERA_INDEX}"
            )

        # Request a moderate frame size for inference.
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        controller = TrafficController()
        current_state = "ALL_RED"
        state_started_at = time.monotonic()
        state_duration = ALL_RED_DURATION

        print("[EDGEGUARD] Adaptive hardware controller running.")
        print("[EDGEGUARD] Press Q in the video window to stop.")

        while True:
            ok, frame = camera.read()

            if not ok or frame is None:
                raise RuntimeError("Camera frame read failed")

            inference_started_at = time.monotonic()
            results = model.predict(frame, verbose=False)
            inference_time = time.monotonic() - inference_started_at

            if inference_time > INFERENCE_TIMEOUT:
                raise RuntimeError(
                    f"Inference took {inference_time:.2f}s; "
                    "requesting safe shutdown"
                )

            height, width = frame.shape[:2]
            rois = create_rois(width, height)

            counts, detections = count_vehicles(results, rois)

            last_decision = get_traffic_decision(
                counts["N"],
                counts["S"],
                counts["E"],
                counts["W"],
            )

            # Determine whether the current phase has finished.
            now = time.monotonic()
            elapsed = now - state_started_at

            if elapsed >= state_duration:
                if current_state in ("NS_GREEN", "EW_GREEN"):
                    # Green ends with yellow.
                    next_state = controller.apply_priority(
                        last_decision["priority"]
                    )
                    state_duration = YELLOW_DURATION

                elif current_state in ("NS_YELLOW", "EW_YELLOW"):
                    # Yellow ends with ALL_RED.
                    next_state = controller.apply_priority(
                        last_decision["priority"]
                    )
                    state_duration = ALL_RED_DURATION

                else:
                    # Select the next direction only from ALL_RED.
                    priority = last_decision["priority"]

                    if priority == "EQUAL":
                        # The controller chooses the opposite direction
                        # from its last green direction when tied.
                        priority = "EQUAL"

                    next_state = controller.apply_priority(priority)

                    if next_state in ("NS_GREEN", "EW_GREEN"):
                        state_duration = green_duration_for(
                            priority, last_decision
                        )
                    else:
                        state_duration = ALL_RED_DURATION

                next_state = state_command(next_state)

                if next_state != current_state:
                    esp32.send_command(next_state)
                    print(
                        f"[CONTROLLER] {current_state} -> {next_state} "
                        f"({state_duration:.1f}s)"
                    )

                current_state = next_state
                state_started_at = time.monotonic()

            # Draw the four regions.
            roi_colors = {
                "N": (255, 100, 0),
                "S": (0, 200, 255),
                "E": (0, 255, 0),
                "W": (255, 0, 255),
            }

            for direction, roi in rois.items():
                cv2.polylines(
                    frame, [roi], True,
                    roi_colors[direction], 2
                )

            # Draw detections.
            for (x1, y1, x2, y2, center,
                 direction, confidence, class_id) in detections:

                cv2.rectangle(
                    frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                )
                cv2.circle(frame, center, 4, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    f"{direction} {confidence:.2f}",
                    (x1, max(20, y1 - 7)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2
                )

            # Display live counts and controller decision.
            lines = [
                f"N: {counts['N']}   S: {counts['S']}",
                f"E: {counts['E']}   W: {counts['W']}",
                f"NS total: {last_decision['ns_total']}",
                f"EW total: {last_decision['ew_total']}",
                f"Priority: {last_decision['priority']}",
                f"State: {current_state}",
                f"NS green: {last_decision['ns_green']}s",
                f"EW green: {last_decision['ew_green']}s",
                f"Inference: {inference_time:.2f}s",
            ]

            y = 25
            for line in lines:
                cv2.putText(
                    frame, line, (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58, (255, 255, 255), 2
                )
                y += 25

            cv2.imshow("EDGEGUARD - Adaptive Traffic Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[EDGEGUARD] Stop requested by user.")
                break

    except KeyboardInterrupt:
        print("\n[EDGEGUARD] Interrupted by user.")

    except Exception as error:
        print(f"\n[ERROR] {error}")

    finally:
        # Best-effort safe command; this cannot work if USB communication
        # is already lost. The ESP32 currently has no heartbeat timeout.
        if esp32 is not None:
            try:
                esp32.send_command("ALL_RED")
                print("[SAFETY] ALL_RED command sent during shutdown.")
            except Exception as error:
                print(f"[WARNING] Could not send ALL_RED: {error}")

        if camera is not None:
            camera.release()

        cv2.destroyAllWindows()

        if esp32 is not None:
            esp32.close()

        print("[EDGEGUARD] Shutdown complete.")


if __name__ == "__main__":
    main()
