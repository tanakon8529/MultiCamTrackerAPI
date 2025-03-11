import pytest
from app.services.counter import CounterService


@pytest.mark.unit
class TestCounterService:
    def setup_method(self):
        # Create a counting line at y=100, direction top-to-bottom (positive)
        self.counter = CounterService(
            line_position=100,
            count_direction="positive",
            camera_id="camera1",
            conveyor_id="conveyor1"
        )
        
    def test_init(self):
        assert self.counter is not None
        assert self.counter.line_position == 100
        assert self.counter.count_direction == "positive"
        assert self.counter.camera_id == "camera1"
        assert self.counter.conveyor_id == "conveyor1"
        assert self.counter.count == 0
        assert self.counter.track_history == {}
        
    def test_update_no_tracks(self):
        # Test with no tracks
        tracks = {}
        timestamp = 1.0
        
        result = self.counter.update(tracks, timestamp)
        
        assert result.count == 0
        assert result.crossed_objects == []
        
    def test_update_track_not_crossing(self):
        # Test with a track that doesn't cross the line
        tracks = {
            "track1": {
                "bbox": [10, 50, 50, 90],  # y position below the line
                "timestamp": 1.0,
                "camera_id": "camera1"
            }
        }
        
        result = self.counter.update(tracks, 1.0)
        
        # Track is registered but not counted yet
        assert result.count == 0
        assert result.crossed_objects == []
        assert len(self.counter.track_history) == 1
        assert "track1" in self.counter.track_history
        
    def test_update_track_crossing_positive(self):
        # Test with a track that crosses the line in the positive direction
        
        # First frame - object is above the line
        tracks1 = {
            "track1": {
                "bbox": [10, 50, 50, 90],  # y position below the line (above the counting line)
                "timestamp": 1.0,
                "camera_id": "camera1"
            }
        }
        
        result1 = self.counter.update(tracks1, 1.0)
        assert result1.count == 0
        assert result1.crossed_objects == []
        
        # Second frame - object crosses the line from top to bottom (positive direction)
        tracks2 = {
            "track1": {
                "bbox": [10, 110, 50, 150],  # y position now above the line (below the counting line)
                "timestamp": 1.5,
                "camera_id": "camera1"
            }
        }
        
        result2 = self.counter.update(tracks2, 1.5)
        
        # Track should be counted
        assert result2.count == 1
        assert len(result2.crossed_objects) == 1
        assert result2.crossed_objects[0]["track_id"] == "track1"
        assert result2.crossed_objects[0]["timestamp"] == 1.5
        assert result2.crossed_objects[0]["direction"] == "positive"
        
    def test_update_track_crossing_negative(self):
        # Create counter with negative direction
        counter = CounterService(
            line_position=100,
            count_direction="negative",
            camera_id="camera1",
            conveyor_id="conveyor1"
        )
        
        # First frame - object is below the line
        tracks1 = {
            "track1": {
                "bbox": [10, 110, 50, 150],  # y position above the line (below the counting line)
                "timestamp": 1.0,
                "camera_id": "camera1"
            }
        }
        
        result1 = counter.update(tracks1, 1.0)
        assert result1.count == 0
        assert result1.crossed_objects == []
        
        # Second frame - object crosses the line from bottom to top (negative direction)
        tracks2 = {
            "track1": {
                "bbox": [10, 50, 50, 90],  # y position now below the line (above the counting line)
                "timestamp": 1.5,
                "camera_id": "camera1"
            }
        }
        
        result2 = counter.update(tracks2, 1.5)
        
        # Track should be counted
        assert result2.count == 1
        assert len(result2.crossed_objects) == 1
        assert result2.crossed_objects[0]["track_id"] == "track1"
        assert result2.crossed_objects[0]["timestamp"] == 1.5
        assert result2.crossed_objects[0]["direction"] == "negative"
        
    def test_update_track_crossing_wrong_direction(self):
        # Test track crossing in the wrong direction (not counted)
        
        # First frame - object is below the line
        tracks1 = {
            "track1": {
                "bbox": [10, 110, 50, 150],  # y position above the line (below the counting line)
                "timestamp": 1.0,
                "camera_id": "camera1"
            }
        }
        
        result1 = self.counter.update(tracks1, 1.0)
        assert result1.count == 0
        assert result1.crossed_objects == []
        
        # Second frame - object crosses the line from bottom to top (negative direction)
        # But counter is only counting positive direction
        tracks2 = {
            "track1": {
                "bbox": [10, 50, 50, 90],  # y position now below the line (above the counting line)
                "timestamp": 1.5,
                "camera_id": "camera1"
            }
        }
        
        result2 = self.counter.update(tracks2, 1.5)
        
        # Track should not be counted (crossing in wrong direction)
        assert result2.count == 0
        assert result2.crossed_objects == []
        
    def test_update_multiple_tracks(self):
        # Test with multiple tracks, one crossing and one not
        
        # First frame
        tracks1 = {
            "track1": {
                "bbox": [10, 50, 50, 90],  # above the line
                "timestamp": 1.0,
                "camera_id": "camera1"
            },
            "track2": {
                "bbox": [100, 110, 150, 150],  # below the line
                "timestamp": 1.0,
                "camera_id": "camera1"
            }
        }
        
        result1 = self.counter.update(tracks1, 1.0)
        assert result1.count == 0
        assert result1.crossed_objects == []
        
        # Second frame - track1 crosses down, track2 stays below
        tracks2 = {
            "track1": {
                "bbox": [10, 110, 50, 150],  # now below the line
                "timestamp": 1.5,
                "camera_id": "camera1"
            },
            "track2": {
                "bbox": [110, 120, 160, 160],  # still below the line
                "timestamp": 1.5,
                "camera_id": "camera1"
            }
        }
        
        result2 = self.counter.update(tracks2, 1.5)
        
        # Only track1 should be counted
        assert result2.count == 1
        assert len(result2.crossed_objects) == 1
        assert result2.crossed_objects[0]["track_id"] == "track1"
