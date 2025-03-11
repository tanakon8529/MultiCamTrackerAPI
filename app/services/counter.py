import numpy as np
from typing import List, Dict, Any, Set, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class Counter:
    """
    Counter module for counting objects that cross a line.
    
    As specified in the requirements:
    - Input: Takes a list of object positions with IDs from a single camera
    - Output: Counts objects that cross a specified line
    - Accuracy depends on updates being in chronological order
    """
    
    def __init__(self, crossing_line: Dict[str, float], direction: str = "any"):
        """
        Initialize the counter.
        
        Args:
            crossing_line (Dict[str, float]): Line used for counting
                Format: {"x1": float, "y1": float, "x2": float, "y2": float}
            direction (str): Direction to count
                Options: "any" (count all crossings), 
                         "positive" (count only positive crossings),
                         "negative" (count only negative crossings)
        """
        self.crossing_line = crossing_line
        self.line_start = np.array([crossing_line["x1"], crossing_line["y1"]])
        self.line_end = np.array([crossing_line["x2"], crossing_line["y2"]])
        self.direction = direction
        
        # Calculate line vector and normal
        self.line_vector = self.line_end - self.line_start
        self.line_normal = np.array([-self.line_vector[1], self.line_vector[0]])
        
        # Normalize the normal vector
        norm = np.linalg.norm(self.line_normal)
        if norm > 0:
            self.line_normal = self.line_normal / norm
        
        # Track object positions and crossing status
        self.object_positions = {}  # Maps object ID to last known position
        self.counted_objects = set()  # Set of object IDs that have been counted
        self.crossing_timestamps = []  # List of timestamps when objects crossed
        self.counts_by_timestamp = []  # List of counts at each update
        self.total_count = 0
    
    def get_counts(self) -> Dict[str, Any]:
        """
        Get current counts.
        
        Returns:
            Dict[str, Any]: Dictionary with current count information
        """
        return {
            "total_count": self.total_count,
            "timestamp": datetime.now(),
            "counted_objects": list(self.counted_objects)
        }
    
    def get_total_count(self) -> int:
        """
        Get the total count.
        
        Returns:
            int: Total number of objects counted
        """
        return self.total_count
    
    def update(self, objects: List[Dict[str, Any]]) -> int:
        """
        Update counter with a new set of tracked objects.
        
        Args:
            objects (List[Dict[str, Any]]): List of tracked objects with IDs
            
        Returns:
            int: Number of new objects counted in this update
        """
        if not objects:
            return 0
        
        # Sort objects by timestamp to ensure chronological order
        objects = sorted(objects, key=lambda x: x["timestamp"])
        
        # Get timestamp for this update
        timestamp = objects[0]["timestamp"]
        
        # Track new crossings
        new_crossings = []
        
        for obj in objects:
            obj_id = obj["id"]
            
            # Get object center position
            position = np.array([
                obj["x"] + obj["width"] / 2,
                obj["y"] + obj["height"] / 2
            ])
            
            # If this is a new object, just store its position
            if obj_id not in self.object_positions:
                self.object_positions[obj_id] = position
                continue
            
            # Get previous position
            prev_position = self.object_positions[obj_id]
            
            # Check if object has crossed the line
            if self._has_crossed_line(prev_position, position):
                # Determine crossing direction
                direction = self._get_crossing_direction(prev_position, position)
                
                # Count only if direction matches our counting direction
                if (self.direction == "any" or 
                    (self.direction == "positive" and direction > 0) or
                    (self.direction == "negative" and direction < 0)):
                    
                    # Only count each object once
                    if obj_id not in self.counted_objects:
                        self.counted_objects.add(obj_id)
                        self.total_count += 1
                        
                        # Record crossing
                        new_crossings.append({
                            "object_id": obj_id,
                            "timestamp": timestamp,
                            "direction": "positive" if direction > 0 else "negative"
                        })
            
            # Update object position
            self.object_positions[obj_id] = position
        
        # Record counts for this update
        if new_crossings:
            self.crossing_timestamps.extend(new_crossings)
            
            # Add to counts by timestamp
            self.counts_by_timestamp.append({
                "timestamp": timestamp,
                "count": len(new_crossings),
                "direction": self.direction,
                "object_ids": [c["object_id"] for c in new_crossings]
            })
        
        return len(new_crossings)
    
    def _has_crossed_line(self, prev_pos: np.ndarray, curr_pos: np.ndarray) -> bool:
        """
        Check if an object has crossed the line between two positions.
        
        Uses line segment intersection calculation.
        
        Args:
            prev_pos (np.ndarray): Previous position
            curr_pos (np.ndarray): Current position
            
        Returns:
            bool: True if the object has crossed the line
        """
        # Create line segments
        object_vector = curr_pos - prev_pos
        
        # Check for intersection using vector cross product
        v1 = prev_pos - self.line_start
        v2 = curr_pos - self.line_start
        v3 = self.line_end - self.line_start
        
        # Calculate cross products
        cross1 = np.cross(v1, v3)
        cross2 = np.cross(v2, v3)
        
        # If cross products have different signs, the object path crosses the line
        if cross1 * cross2 <= 0:
            # Now check if the intersection is within the line segment
            v4 = prev_pos - curr_pos
            v5 = prev_pos - self.line_start
            v6 = prev_pos - self.line_end
            
            cross3 = np.cross(v5, v4)
            cross4 = np.cross(v6, v4)
            
            # If cross products have different signs, intersection is within the line segment
            return cross3 * cross4 <= 0
        
        return False
    
    def _get_crossing_direction(self, prev_pos: np.ndarray, curr_pos: np.ndarray) -> float:
        """
        Determine the direction of crossing.
        
        Args:
            prev_pos (np.ndarray): Previous position
            curr_pos (np.ndarray): Current position
            
        Returns:
            float: Positive for one direction, negative for the other
        """
        # Calculate dot product with normal vector
        movement_vector = curr_pos - prev_pos
        direction = np.dot(movement_vector, self.line_normal)
        
        return direction

@dataclass
class CountResult:
    """
    Result of a counter update operation.
    """
    count: int
    crossed_objects: List[Dict[str, Any]]

class CounterService:
    """
    Service wrapper for the Counter class to make it compatible with the tests.
    
    Provides an interface expected by the test suite.
    """
    
    def __init__(self, line_position: int, count_direction: str, camera_id: str, conveyor_id: str):
        """
        Initialize the counter service.
        
        Args:
            line_position (int): Y-coordinate of the counting line
            count_direction (str): Direction to count ("positive", "negative", "any")
            camera_id (str): ID of the camera
            conveyor_id (str): ID of the conveyor
        """
        self.line_position = line_position
        self.count_direction = count_direction
        self.camera_id = camera_id
        self.conveyor_id = conveyor_id
        self.count = 0
        self.track_history = {}
        
        # Create a horizontal counting line
        self.counter = Counter(
            crossing_line={
                "x1": 0,
                "y1": line_position,
                "x2": 1000,  # Arbitrary large width
                "y2": line_position
            },
            direction=count_direction
        )
    
    def update(self, tracks: Dict[str, Dict[str, Any]], timestamp: float) -> CountResult:
        """
        Update counter with tracked objects and check for line crossings.
        
        Args:
            tracks (Dict[str, Dict[str, Any]]): Current tracked objects
            timestamp (float): Current timestamp
            
        Returns:
            CountResult: Results of the update, including count and crossed objects
        """
        # Convert tracks to format expected by Counter
        counter_objects = []
        crossed_objects = []
        
        for track_id, track_data in tracks.items():
            # Extract bbox in [x, y, width, height] format from track_data
            bbox = track_data["bbox"]  # Expects [x1, y1, x2, y2]
            
            # Convert [x1, y1, x2, y2] to [x, y, width, height]
            x = bbox[0]
            y = bbox[1]
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            # Store previous position if it exists
            prev_position = None
            if track_id in self.track_history:
                prev_position = self.track_history[track_id]["position"]
            
            # Store current position for next update
            self.track_history[track_id] = {
                "position": (y + height / 2),  # Use center y-coordinate
                "timestamp": timestamp
            }
            
            # Check for line crossing
            if prev_position is not None:
                current_position = y + height / 2
                
                # Determine if track crossed the line
                crossed = False
                direction = ""
                
                if prev_position <= self.line_position and current_position > self.line_position:
                    # Crossed from above to below (positive direction)
                    crossed = True
                    direction = "positive"
                elif prev_position >= self.line_position and current_position < self.line_position:
                    # Crossed from below to above (negative direction)
                    crossed = True
                    direction = "negative"
                
                # Count if crossed in the correct direction
                if crossed and (self.count_direction == "any" or direction == self.count_direction):
                    self.count += 1
                    crossed_objects.append({
                        "track_id": track_id,
                        "timestamp": timestamp,
                        "direction": direction,
                        "camera_id": self.camera_id,
                        "conveyor_id": self.conveyor_id
                    })
            
            # Prepare object for counter
            counter_objects.append({
                "id": track_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "timestamp": timestamp
            })
        
        # Update the underlying counter (not used directly for tests, but maintains compatibility)
        if counter_objects:
            self.counter.update(counter_objects)
        
        # Return count result
        return CountResult(
            count=self.count,
            crossed_objects=crossed_objects
        )
