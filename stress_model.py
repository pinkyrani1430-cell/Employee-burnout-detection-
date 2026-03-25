class StressModel:
    """
    Determines stress level based on Typing Speed (KPS).
    Maps KPS directly to a progress percentage (0-100%).
    """
    @staticmethod
    def calculate_stress(kps):
        """
        Prediction Logic:
        1. Map KPS to Progress Percentage:
           - Max expected speed = 10 KPS
           - progress = (kps / 10) * 100 (capped at 100%)
        
        2. Determine Level and Color based on Progress:
           - 0% -> Idle
           - 0-30% -> Low Stress (Green)
           - 30-60% -> Medium Stress (Orange)
           - 60-100% -> High Stress (Red)
        """
        
        # Calculate progress percentage (0-100)
        # 10 KPS is considered the maximum for 100% bar
        progress = min((kps / 10.0) * 100, 100)
        
        # Case 1: Idle
        if progress == 0:
            return 0, "Idle", "#888888"

        # Case 2: Low Stress (0-30%)
        if progress <= 30:
            return int(progress), "Low Stress", "#4CAF50"
            
        # Case 3: Medium Stress (30-60%)
        elif progress <= 60:
            return int(progress), "Medium Stress", "#FF9800"
            
        # Case 4: High Stress (60-100%)
        else:
            return int(progress), "High Stress", "#F44336"
