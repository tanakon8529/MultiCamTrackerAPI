import pytest
import numpy as np
from app.services.tracker import TrackerService
from app.services.detector import DetectionResult


@pytest.mark.unit
class TestTrackerService:
    def setup_method(self):
        self.tracker = TrackerService(max_time_diff=1.0)
        
    def test_init(self):
        assert self.tracker is not None
        assert self.tracker.max_time_diff == 1.0
        assert self.tracker.tracks == {}
        
    def test_update_empty_detections(self):
        # Test with empty detections
        detection = DetectionResult(
            bboxes=[],
            scores=[],
            class_ids=[]
        )
        
        timestamp = 1.0
        camera_id = "camera1"
        
        tracks = self.tracker.update(detection, timestamp, camera_id)
        
        # Should return empty dict
        assert len(tracks) == 0
        
    def test_update_with_detections(self):
        # Test with some detections
        detection = DetectionResult(
            bboxes=[[10, 10, 50, 50], [100, 100, 150, 150]],
            scores=[0.9, 0.8],
            class_ids=[1, 1]
        )
        
        timestamp = 1.0
        camera_id = "camera1"
        
        tracks = self.tracker.update(detection, timestamp, camera_id)
        
        # Should have created two tracks
        assert len(tracks) == 2
        
        # Check that the track IDs exist
        track_ids = list(tracks.keys())
        assert len(track_ids) == 2
        
        # Check that tracks contain the correct data
        for track_id, track in tracks.items():
            assert track['camera_id'] == camera_id
            assert track['timestamp'] == timestamp
            assert 'bbox' in track
            assert 'score' in track
            assert 'class_id' in track
            
    def test_track_continuity(self):
        # Test that tracks maintain continuity over time
        # First update
        detection1 = DetectionResult(
            bboxes=[[10, 10, 50, 50]],
            scores=[0.9],
            class_ids=[1]
        )
        
        tracks1 = self.tracker.update(detection1, 1.0, "camera1")
        assert len(tracks1) == 1
        track_id = list(tracks1.keys())[0]
        
        # Second update with the object moved slightly
        detection2 = DetectionResult(
            bboxes=[[15, 15, 55, 55]],  # Moved slightly
            scores=[0.9],
            class_ids=[1]
        )
        
        tracks2 = self.tracker.update(detection2, 1.5, "camera1")
        assert len(tracks2) == 1
        
        # The track ID should remain the same
        assert list(tracks2.keys())[0] == track_id
        
    def test_track_timeout(self):
        # Test that tracks expire after max_time_diff
        # First update
        detection1 = DetectionResult(
            bboxes=[[10, 10, 50, 50]],
            scores=[0.9],
            class_ids=[1]
        )
        
        tracks1 = self.tracker.update(detection1, 1.0, "camera1")
        track_id = list(tracks1.keys())[0]
        
        # Second update after max_time_diff
        detection2 = DetectionResult(
            bboxes=[[15, 15, 55, 55]],  # Moved slightly
            scores=[0.9],
            class_ids=[1]
        )
        
        # Update with a timestamp beyond max_time_diff
        tracks2 = self.tracker.update(detection2, 3.0, "camera1")  # 2.0 seconds later, > max_time_diff of 1.0
        
        # A new track ID should be assigned
        assert list(tracks2.keys())[0] != track_id
