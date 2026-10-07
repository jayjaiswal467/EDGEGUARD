import time


class PerceptionWatchdog:
    def __init__(
        self,
        max_frame_age=2.0,
        max_inference_time=1.0,
        max_invalid_count=3
    ):
        self.max_frame_age = max_frame_age
        self.max_inference_time = max_inference_time
        self.max_invalid_count = max_invalid_count

        self.last_valid_frame_time = time.monotonic()
        self.invalid_count = 0
        self.fault_active = False
        self.last_fault = None

    def check_frame(self, frame):
        """
        Validate whether the camera frame is usable.
        """

        if frame is None:
            self._fault("CAMERA_FRAME_INVALID")
            return False

        if frame.size == 0:
            self._fault("CAMERA_FRAME_EMPTY")
            return False

        self.last_valid_frame_time = time.monotonic()
        return True

    def check_inference(self, inference_time):
        """
        Validate YOLO/OpenCV inference execution time.
        """

        if inference_time > self.max_inference_time:
            self._fault("INFERENCE_TIMEOUT")
            return False

        return True

    def check_counts(self, counts):
        """
        Validate directional vehicle counts.
        Expected:
        {
            "N": int,
            "S": int,
            "E": int,
            "W": int
        }
        """

        required = ["N", "S", "E", "W"]

        if not isinstance(counts, dict):
            self._fault("COUNT_DATA_INVALID")
            return False

        for direction in required:
            value = counts.get(direction)

            if not isinstance(value, int):
                self._fault("COUNT_DATA_INVALID")
                return False

            if value < 0:
                self._fault("NEGATIVE_COUNT")
                return False

        self.invalid_count = 0
        return True

    def check_stale_frame(self):
        """
        Detect a camera that has stopped producing valid frames.
        """

        frame_age = time.monotonic() - self.last_valid_frame_time

        if frame_age > self.max_frame_age:
            self._fault("STALE_CAMERA_FRAME")
            return False

        return True

    def is_healthy(self):
        """
        Overall perception health status.
        """

        return not self.fault_active

    def reset_fault(self):
        """
        Clear the active perception fault after recovery.
        """

        self.fault_active = False
        self.last_fault = None
        self.invalid_count = 0

    def _fault(self, reason):
        """
        Register a perception fault.
        """

        self.fault_active = True
        self.last_fault = reason

        print(f"[WATCHDOG] FAULT: {reason}")