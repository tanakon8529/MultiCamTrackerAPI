import numpy as np
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class Tracker:
    """
    Tracker module for object tracking.
    
    As specified in the requirements:
    - Input: Takes two consecutive sets of object positions
    - Output: Assigns consistent IDs to objects across frames
    - Accuracy depends on:
        1. Time difference between frames (should be < 1 second)
        2. Order of updates (must be chronological)
    """
    
    def __init__(self, max_time_diff: float = 1.0, max_distance: float = 100.0):
        """
        Initialize the tracker.
        
        Args:
            max_time_diff (float): Maximum allowed time difference between frames (in seconds)
            max_distance (float): Maximum allowed distance for object matching
        """
        self.max_time_diff = max_time_diff
        self.max_distance = max_distance
        self.tracked_objects = []
        self.last_timestamp = None
        self.next_id = 0
        self.track_history = {}  # Maps track_id to list of positions
    
    def get_tracked_objects(self) -> List[Dict[str, Any]]:
        """
        Get the current set of tracked objects.
        
        Returns:
            List[Dict[str, Any]]: List of tracked objects with consistent IDs
        """
        return self.tracked_objects
    
    def update(self, detections_t1: Dict[str, Any], detections_t2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Update tracker with two consecutive sets of detections.
        
        Args:
            detections_t1 (Dict[str, Any]): First set of detections
            detections_t2 (Dict[str, Any]): Second set of detections
            
        Returns:
            List[Dict[str, Any]]: Updated tracked objects
        """
        # Extract timestamps and check time difference
        timestamp_t1 = detections_t1["timestamp"]
        timestamp_t2 = detections_t2["timestamp"]
        
        time_diff = (timestamp_t2 - timestamp_t1).total_seconds()
        
        # Check if timestamps are in order
        if self.last_timestamp is not None:
            if timestamp_t1 < self.last_timestamp:
                logger.warning(f"Out-of-order update: {timestamp_t1} < {self.last_timestamp}")
                # Continue anyway, but results may be less accurate
        
        # Check time difference
        if time_diff > self.max_time_diff or time_diff < 0:
            logger.warning(f"Time difference ({time_diff} seconds) exceeds limit or is negative")
            # Continue anyway, but results may be less accurate
        
        # Extract objects
        objects_t1 = detections_t1["objects"]
        objects_t2 = detections_t2["objects"]
        
        # If this is the first update, assign new IDs to all objects
        if not self.tracked_objects:
            self._initialize_tracks(objects_t1, timestamp_t1)
        
        # Match objects between frames
        self._match_objects(objects_t2, timestamp_t2)
        
        # Update last timestamp
        self.last_timestamp = timestamp_t2
        
        return self.tracked_objects
    
    def _initialize_tracks(self, objects: List[Dict[str, Any]], timestamp: datetime) -> None:
        """
        Initialize tracker with first set of objects.
        
        Args:
            objects (List[Dict[str, Any]]): First set of objects
            timestamp (datetime): Timestamp
        """
        self.tracked_objects = []
        
        for obj in objects:
            track_id = f"track_{self.next_id}"
            self.next_id += 1
            
            tracked_obj = {
                "id": track_id,
                "x": obj["x"],
                "y": obj["y"],
                "width": obj["width"],
                "height": obj["height"],
                "confidence": obj["confidence"],
                "class_id": obj.get("class_id"),
                "timestamp": timestamp
            }
            
            self.tracked_objects.append(tracked_obj)
            
            # Initialize track history
            self.track_history[track_id] = [tracked_obj]
    
    def _match_objects(self, objects: List[Dict[str, Any]], timestamp: datetime) -> None:
        """
        Match objects between frames using simple distance-based matching.
        
        In a real implementation, this would be more sophisticated, using
        techniques like Kalman filtering, Hungarian algorithm, etc.
        
        Args:
            objects (List[Dict[str, Any]]): New set of objects
            timestamp (datetime): Timestamp
        """
        if not self.tracked_objects:
            self._initialize_tracks(objects, timestamp)
            return
        
        # Create arrays of positions for efficient calculation
        prev_positions = np.array([
            [obj["x"] + obj["width"] / 2, obj["y"] + obj["height"] / 2]
            for obj in self.tracked_objects
        ])
        
        curr_positions = np.array([
            [obj["x"] + obj["width"] / 2, obj["y"] + obj["height"] / 2]
            for obj in objects
        ])
        
        # If no objects in either frame, return
        if len(prev_positions) == 0 or len(curr_positions) == 0:
            self.tracked_objects = []
            return
        
        # Calculate distance matrix
        distance_matrix = np.zeros((len(prev_positions), len(curr_positions)))
        
        for i in range(len(prev_positions)):
            for j in range(len(curr_positions)):
                distance_matrix[i, j] = np.linalg.norm(prev_positions[i] - curr_positions[j])
        
        # Match objects based on minimum distance
        matched_indices = []
        unmatched_objects = []
        
        # Simple greedy matching
        while distance_matrix.size > 0 and distance_matrix.min() < self.max_distance:
            i, j = np.unravel_index(distance_matrix.argmin(), distance_matrix.shape)
            
            # Add match
            matched_indices.append((i, j))
            
            # Mark as matched by setting distance to infinity
            distance_matrix[i, :] = float('inf')
            distance_matrix[:, j] = float('inf')
        
        # Create new tracked objects
        new_tracked_objects = []
        
        # Update matched objects
        for prev_idx, curr_idx in matched_indices:
            prev_obj = self.tracked_objects[prev_idx]
            curr_obj = objects[curr_idx]
            
            # Update position with new detection
            updated_obj = {
                "id": prev_obj["id"],
                "x": curr_obj["x"],
                "y": curr_obj["y"],
                "width": curr_obj["width"],
                "height": curr_obj["height"],
                "confidence": curr_obj["confidence"],
                "class_id": curr_obj.get("class_id"),
                "timestamp": timestamp
            }
            
            new_tracked_objects.append(updated_obj)
            
            # Update track history
            self.track_history[prev_obj["id"]].append(updated_obj)
        
        # Add unmatched new detections as new tracks
        unmatched_curr_indices = set(range(len(objects))) - set(curr_idx for _, curr_idx in matched_indices)
        
        for idx in unmatched_curr_indices:
            obj = objects[idx]
            
            track_id = f"track_{self.next_id}"
            self.next_id += 1
            
            new_obj = {
                "id": track_id,
                "x": obj["x"],
                "y": obj["y"],
                "width": obj["width"],
                "height": obj["height"],
                "confidence": obj["confidence"],
                "class_id": obj.get("class_id"),
                "timestamp": timestamp
            }
            
            new_tracked_objects.append(new_obj)
            
            # Initialize track history
            self.track_history[track_id] = [new_obj]
        
        self.tracked_objects = new_tracked_objects


# Add the TrackerService class to fix compatibility with the tests
from dataclasses import dataclass

@dataclass
class DetectionResult:
    bboxes: List[List[float]]
    scores: List[float]
    class_ids: List[int]


class TrackerService:
    """
    Service wrapper for the Tracker class to make it compatible with the tests.
    Provides an interface that matches the test expectations.
    """
    
    def __init__(self, max_time_diff: float = 1.0):
        """
        Initialize the tracker service.
        
        Args:
            max_time_diff (float): Maximum allowed time difference between frames (in seconds)
        """
        self.max_time_diff = max_time_diff
        self.tracks = {}  # Dictionary to store tracks by ID
        self.next_id = 0
    
    def update(self, detection: DetectionResult, timestamp: float, camera_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Update tracks with new detections.
        
        Args:
            detection (DetectionResult): Detection results containing bboxes, scores, and class_ids
            timestamp (float): Current timestamp
            camera_id (str): ID of the camera
            
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of tracks indexed by track ID
        """
        # If we have no bboxes, return empty tracks
        if len(detection.bboxes) == 0:
            return {}
        
        # Convert detections to the format expected by our tracker
        new_tracks = {}
        
        # Process each detection
        for i, (bbox, score, class_id) in enumerate(zip(detection.bboxes, detection.scores, detection.class_ids)):
            # Check if this detection matches any existing track
            matched = False
            
            # For simplicity, use a basic matching strategy based on IoU
            for track_id, track in list(self.tracks.items()):
                # Only consider tracks from the same camera
                if track['camera_id'] != camera_id:
                    continue
                
                # Check if timestamp difference is within threshold
                if timestamp - track['timestamp'] > self.max_time_diff:
                    # Track is too old, remove it
                    del self.tracks[track_id]
                    continue
                
                # Check if boxes overlap (simple IoU check)
                if self._calculate_iou(bbox, track['bbox']) > 0.5:
                    # Update the track
                    self.tracks[track_id] = {
                        'bbox': bbox,
                        'score': score,
                        'class_id': class_id,
                        'camera_id': camera_id,
                        'timestamp': timestamp
                    }
                    new_tracks[track_id] = self.tracks[track_id]
                    matched = True
                    break
            
            # If no match found, create a new track
            if not matched:
                track_id = f"track_{self.next_id}"
                self.next_id += 1
                
                self.tracks[track_id] = {
                    'bbox': bbox,
                    'score': score,
                    'class_id': class_id,
                    'camera_id': camera_id,
                    'timestamp': timestamp
                }
                new_tracks[track_id] = self.tracks[track_id]
        
        return new_tracks
    
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            bbox1 (List[float]): First bounding box [x1, y1, x2, y2]
            bbox2 (List[float]): Second bounding box [x1, y1, x2, y2]
            
        Returns:
            float: IoU value between 0 and 1
        """
        # Calculate intersection area
        x_left = max(bbox1[0], bbox2[0])
        y_top = max(bbox1[1], bbox2[1])
        x_right = min(bbox1[2], bbox2[2])
        y_bottom = min(bbox1[3], bbox2[3])
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union area
        bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union_area = bbox1_area + bbox2_area - intersection_area
        
        # Return IoU
        return intersection_area / union_area if union_area > 0 else 0.0
