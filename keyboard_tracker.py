import time

class KeyboardTracker:
    """
    Handles tracking of keypress timestamps within a sliding window.
    """
    def __init__(self):
        self.timestamps = []
        self.is_monitoring = False
        self.last_keypress_time = 0
        self.smoothed_speed = 0.0 # Store smoothed speed for stability

    def start(self):
        """Resets data and starts monitoring."""
        self.timestamps = []
        self.is_monitoring = True
        self.last_keypress_time = time.time()
        self.smoothed_speed = 0.0

    def stop(self):
        """Stops monitoring and clears data."""
        self.is_monitoring = False
        self.timestamps = []
        self.smoothed_speed = 0.0

    def record_character(self):
        """Records the timestamp of a new keypress."""
        if self.is_monitoring:
            current_time = time.time()
            self.timestamps.append(current_time)
            self.last_keypress_time = current_time

    def get_kps(self):
        """
        Calculates KPS using a 5-second sliding window and smoothing.
        Detects idle state if no typing for > 3 seconds.
        """
        if not self.is_monitoring:
            return 0.0

        current_time = time.time()
        
        # 5. Detect when the user stops typing (Idle detection > 3s)
        if current_time - self.last_keypress_time > 3.0:
            self.timestamps = [] # Clear window if idle
            self.smoothed_speed = 0.0
            return 0.0

        # 1. Sliding window: Only keep timestamps from the last 5 seconds
        self.timestamps = [t for t in self.timestamps if current_time - t <= 5.0]
        
        # Current raw speed: number_of_keys_in_last_5_seconds / 5
        raw_speed = len(self.timestamps) / 5.0
        
        # 2. Smoothing logic: smoothed_speed = (previous * 0.7) + (current * 0.3)
        # This prevents sudden jumps in the UI
        self.smoothed_speed = (self.smoothed_speed * 0.7) + (raw_speed * 0.3)
        
        return self.smoothed_speed
