import cv2
import numpy as np
import time

from ultralytics import YOLO

from watchdog import PerceptionWatchdog
from traffic_logic import get_traffic_decision


# ============================================================
# EDGEGUARD - Vehicle Detection
# Phase 1
#
# Camera
#   ↓
# YOLOv8
#   ↓
# Vehicle Class Filtering
#   ↓
# N / S / E / W ROI Counting
#   ↓
# Traffic Logic
#   ↓
# Decision
#
# Watchdog protects the perception pipeline.
# ============================================================


# ------------------------------------------------------------
# YOLO MODEL
# ------------------------------------------------------------

model = YOLO("yolov8n.pt")


# ------------------------------------------------------------
# PERCEPTION WATCHDOG
# ------------------------------------------------------------

watchdog = PerceptionWatchdog(
    max_frame_age=2.0,
    max_inference_time=1.0
)


# ------------------------------------------------------------
# COCO VEHICLE CLASSES
# ------------------------------------------------------------

VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}


# ------------------------------------------------------------
# ROI HELPER
# ------------------------------------------------------------

def point_in_roi(point, roi):
    """
    Check whether a point lies inside a polygon ROI.
    """

    result = cv2.pointPolygonTest(
        roi,
        point,
        False
    )

    return result >= 0


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # CAMERA INITIALIZATION
    # --------------------------------------------------------

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("[CAMERA] ERROR: Unable to open camera")
        print("[WATCHDOG] FAULT: CAMERA_CONNECTION_FAILED")

        return

    print("[CAMERA] Camera connected")
    print("[YOLO] YOLOv8 loaded")
    print("[WATCHDOG] Perception watchdog active")


    # --------------------------------------------------------
    # GET CAMERA RESOLUTION
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print("[CAMERA] ERROR: Unable to read initial frame")

        cap.release()

        return

    height, width = frame.shape[:2]

    print(
        f"[CAMERA] Resolution: "
        f"{width} x {height}"
    )


    # ========================================================
    # DEFINE FOUR DIRECTIONAL ROIs
    # ========================================================

    # --------------------------------------------------------
    # NORTH
    # --------------------------------------------------------

    north_roi = np.array(
        [
            (int(width * 0.35), 0),
            (int(width * 0.65), 0),
            (int(width * 0.60), int(height * 0.35)),
            (int(width * 0.40), int(height * 0.35))
        ],
        dtype=np.int32
    )


    # --------------------------------------------------------
    # SOUTH
    # --------------------------------------------------------

    south_roi = np.array(
        [
            (int(width * 0.40), int(height * 0.65)),
            (int(width * 0.60), int(height * 0.65)),
            (int(width * 0.65), height),
            (int(width * 0.35), height)
        ],
        dtype=np.int32
    )


    # --------------------------------------------------------
    # WEST
    # --------------------------------------------------------

    west_roi = np.array(
        [
            (0, int(height * 0.35)),
            (int(width * 0.35), int(height * 0.40)),
            (int(width * 0.35), int(height * 0.60)),
            (0, int(height * 0.65))
        ],
        dtype=np.int32
    )


    # --------------------------------------------------------
    # EAST
    # --------------------------------------------------------

    east_roi = np.array(
        [
            (int(width * 0.65), int(height * 0.40)),
            (width, int(height * 0.35)),
            (width, int(height * 0.65)),
            (int(width * 0.65), int(height * 0.60))
        ],
        dtype=np.int32
    )


    # ========================================================
    # MAIN PERCEPTION LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # CAPTURE FRAME
        # ----------------------------------------------------

        ret, frame = cap.read()


        # ----------------------------------------------------
        # CAMERA FAILURE
        # ----------------------------------------------------

        if not ret:

            print(
                "[CAMERA] ERROR: "
                "Frame capture failed"
            )

            watchdog.check_frame(None)

            print(
                "[WATCHDOG] "
                "PERCEPTION FAILURE"
            )

            print(
                "[SAFETY] "
                "ALL_RED REQUESTED"
            )

            break


        # ----------------------------------------------------
        # WATCHDOG FRAME VALIDATION
        # ----------------------------------------------------

        if not watchdog.check_frame(frame):

            print(
                "[WATCHDOG] "
                "Invalid camera frame"
            )

            print(
                "[SAFETY] "
                "ALL_RED REQUESTED"
            )

            break


        # ====================================================
        # YOLO INFERENCE
        # ====================================================

        inference_start = time.perf_counter()

        results = model(
            frame,
            verbose=False
        )

        inference_time = (
            time.perf_counter()
            - inference_start
        )


        # ----------------------------------------------------
        # WATCHDOG INFERENCE CHECK
        # ----------------------------------------------------

        if not watchdog.check_inference(
            inference_time
        ):

            print(
                f"[WATCHDOG] "
                f"Inference timeout: "
                f"{inference_time:.3f}s"
            )

            print(
                "[SAFETY] "
                "ALL_RED REQUESTED"
            )

            break


        # ====================================================
        # DIRECTIONAL COUNTS
        # ====================================================

        counts = {
            "N": 0,
            "S": 0,
            "E": 0,
            "W": 0
        }


        # ====================================================
        # PROCESS YOLO DETECTIONS
        # ====================================================

        for result in results:

            if result.boxes is None:
                continue


            for box in result.boxes:

                # ------------------------------------------------
                # CLASS
                # ------------------------------------------------

                class_id = int(
                    box.cls[0]
                )


                # ------------------------------------------------
                # CONFIDENCE
                # ------------------------------------------------

                confidence = float(
                    box.conf[0]
                )


                # ------------------------------------------------
                # VEHICLE FILTER
                # ------------------------------------------------

                if class_id not in VEHICLE_CLASSES:
                    continue


                # ------------------------------------------------
                # CONFIDENCE FILTER
                # ------------------------------------------------

                if confidence < 0.5:
                    continue


                # ------------------------------------------------
                # BOUNDING BOX
                # ------------------------------------------------

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )


                # ------------------------------------------------
                # CENTER POINT
                # ------------------------------------------------

                center_x = (
                    x1 + x2
                ) // 2

                center_y = (
                    y1 + y2
                ) // 2

                center = (
                    center_x,
                    center_y
                )


                # =================================================
                # DIRECTION CLASSIFICATION
                # =================================================

                direction = None


                if point_in_roi(
                    center,
                    north_roi
                ):

                    counts["N"] += 1
                    direction = "N"


                elif point_in_roi(
                    center,
                    south_roi
                ):

                    counts["S"] += 1
                    direction = "S"


                elif point_in_roi(
                    center,
                    east_roi
                ):

                    counts["E"] += 1
                    direction = "E"


                elif point_in_roi(
                    center,
                    west_roi
                ):

                    counts["W"] += 1
                    direction = "W"


                # ------------------------------------------------
                # DRAW BOUNDING BOX
                # ------------------------------------------------

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


                # ------------------------------------------------
                # LABEL
                # ------------------------------------------------

                label = (
                    f"{VEHICLE_CLASSES[class_id]} "
                    f"{confidence:.2f}"
                )


                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(y1 - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )


                # ------------------------------------------------
                # CENTER POINT
                # ------------------------------------------------

                cv2.circle(
                    frame,
                    center,
                    5,
                    (255, 255, 255),
                    -1
                )


                # ------------------------------------------------
                # DIRECTION LABEL
                # ------------------------------------------------

                if direction is not None:

                    cv2.putText(
                        frame,
                        direction,
                        (
                            center_x + 5,
                            center_y
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )


        # ====================================================
        # WATCHDOG COUNT VALIDATION
        # ====================================================

        if not watchdog.check_counts(
            counts
        ):

            print(
                "[WATCHDOG] "
                "Invalid directional counts"
            )

            print(
                "[SAFETY] "
                "ALL_RED REQUESTED"
            )

            break


        # ====================================================
        # TRAFFIC INTELLIGENCE
        # ====================================================

        decision = get_traffic_decision(
            counts["N"],
            counts["S"],
            counts["E"],
            counts["W"]
        )


        # ----------------------------------------------------
        # TERMINAL OUTPUT
        # ----------------------------------------------------

        print(
            f"[TRAFFIC] "
            f"NS={decision['ns_total']} | "
            f"EW={decision['ew_total']} | "
            f"Priority={decision['priority']} | "
            f"NS Green={decision['ns_green']}s | "
            f"EW Green={decision['ew_green']}s"
        )


        # ====================================================
        # DRAW ROI POLYGONS
        # ====================================================

        cv2.polylines(
            frame,
            [north_roi],
            True,
            (255, 0, 0),
            2
        )

        cv2.polylines(
            frame,
            [south_roi],
            True,
            (0, 255, 0),
            2
        )

        cv2.polylines(
            frame,
            [east_roi],
            True,
            (0, 0, 255),
            2
        )

        cv2.polylines(
            frame,
            [west_roi],
            True,
            (0, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY COUNTS
        # ====================================================

        cv2.putText(
            frame,
            f"NORTH: {counts['N']}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )


        cv2.putText(
            frame,
            f"SOUTH: {counts['S']}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        cv2.putText(
            frame,
            f"EAST: {counts['E']}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


        cv2.putText(
            frame,
            f"WEST: {counts['W']}",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY TRAFFIC DECISION
        # ====================================================

        cv2.putText(
            frame,
            f"PRIORITY: {decision['priority']}",
            (20, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"NS GREEN: {decision['ns_green']}s",
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"EW GREEN: {decision['ew_green']}s",
            (20, 225),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # ====================================================
        # WATCHDOG STATUS
        # ====================================================

        watchdog_status = (
            "WATCHDOG: HEALTHY"
            if watchdog.is_healthy()
            else "WATCHDOG: FAULT"
        )


        cv2.putText(
            frame,
            watchdog_status,
            (20, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "EDGEGUARD - Vehicle Detection",
            frame
        )


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()

    cv2.destroyAllWindows()

    print(
        "[EDGEGUARD] "
        "Vehicle detection stopped"
    )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()