import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import json
from bson import ObjectId

from app.main import app
from app.services.detector import DetectionResult


# Mock ObjectId for testing
class MockObjectId(str):
    def __init__(self, id_str=None):
        self.id_str = id_str or "60c72b2b5e8e29c9c9c5e7a5"
    
    def __str__(self):
        return self.id_str


@pytest.mark.integration
class TestTrackRoutes:
    @pytest.fixture
    async def client(self):
        # Create a test client for the FastAPI app
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture(autouse=True)
    def mock_db(self, monkeypatch):
        # Mock the MongoDB connection
        mock_db = MagicMock()
        mock_uploads = MagicMock()
        mock_tracks = MagicMock()
        mock_counts = MagicMock()
        
        # Setup find_one to return a mock upload document
        mock_upload_doc = {
            "_id": MockObjectId(),
            "filename": "test.jpg",
            "file_path": "/uploads/test.jpg",
            "file_type": "image",
            "camera_id": "camera1",
            "conveyor_id": "conveyor1",
            "upload_time": "2023-01-01T00:00:00",
            "metadata": {}
        }
        mock_uploads.find_one.return_value = mock_upload_doc
        
        # Setup insert_one to return a mock result with an inserted_id
        mock_result = MagicMock()
        mock_result.inserted_id = MockObjectId()
        mock_tracks.insert_one.return_value = mock_result
        mock_counts.insert_one.return_value = mock_result
        
        # Assign collections to the mock database
        mock_db.uploads = mock_uploads
        mock_db.tracks = mock_tracks
        mock_db.counts = mock_counts
        
        # Mock the database connection
        async def mock_get_database():
            return mock_db
        
        # Apply the mock to track endpoints
        monkeypatch.setattr("app.api.v1.endpoints.track.get_database", mock_get_database)
        
        return mock_db
    
    @patch("app.services.detector.DetectorService.detect_objects")
    @patch("app.services.tracker.TrackerService.update")
    @patch("app.services.counter.CounterService.update")
    @patch("cv2.imread")
    async def test_track_image(self, mock_imread, mock_counter_update, mock_tracker_update, mock_detect_objects, client, mock_db):
        # Mock opencv imread to return a valid image
        mock_image = MagicMock()
        mock_imread.return_value = mock_image
        
        # Mock detector to return a detection result
        mock_detection = DetectionResult(bboxes=[[10, 10, 50, 50]], scores=[0.9], class_ids=[1])
        mock_detect_objects.return_value = mock_detection
        
        # Mock tracker to return tracks
        mock_tracks = {"track1": {"bbox": [10, 10, 50, 50], "timestamp": 1.0, "camera_id": "camera1"}}
        mock_tracker_update.return_value = mock_tracks
        
        # Mock counter to return a count result
        mock_count_result = MagicMock()
        mock_count_result.count = 1
        mock_count_result.crossed_objects = [{"track_id": "track1", "timestamp": 1.0}]
        mock_counter_update.return_value = mock_count_result
        
        # Create request data
        data = {
            "file_id": "60c72b2b5e8e29c9c9c5e7a5",
            "detector_config": {
                "confidence_threshold": 0.5,
                "nms_threshold": 0.4
            },
            "tracker_config": {
                "max_time_diff": 1.0
            },
            "counter_config": {
                "line_position": 100,
                "count_direction": "positive"
            }
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/track/image",
            json=data
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "tracking_id" in result
        assert "count" in result
        assert result["count"] == 1
        
        # Verify database calls
        mock_db.uploads.find_one.assert_called_once()
        mock_db.tracks.insert_one.assert_called_once()
        mock_db.counts.insert_one.assert_called_once()
        
    @patch("app.api.v1.endpoints.track.process_tracking")
    async def test_track_batch(self, mock_process_tracking, client, mock_db):
        # Mock the background task processing function
        mock_process_tracking.return_value = None
        
        # Create request data
        data = {
            "file_ids": ["60c72b2b5e8e29c9c9c5e7a5", "60c72b2b5e8e29c9c9c5e7a6"],
            "detector_config": {
                "confidence_threshold": 0.5,
                "nms_threshold": 0.4
            },
            "tracker_config": {
                "max_time_diff": 1.0
            },
            "counter_config": {
                "line_position": 100,
                "count_direction": "positive"
            }
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/track/batch",
            json=data
        )
        
        # Check response
        assert response.status_code == 202
        result = response.json()
        assert result["success"] is True
        assert "message" in result
        assert "Processing tracking for 2 files in the background" in result["message"]
        
        # Verify the background task was launched
        mock_process_tracking.assert_called_once()
        
    @patch("app.api.v1.endpoints.track.process_video_tracking")
    async def test_track_video(self, mock_process_video_tracking, client, mock_db):
        # Mock the background task processing function
        mock_process_video_tracking.return_value = None
        
        # Create request data
        data = {
            "file_id": "60c72b2b5e8e29c9c9c5e7a5",
            "detector_config": {
                "confidence_threshold": 0.5,
                "nms_threshold": 0.4,
                "sample_rate": 5  # Process every 5th frame
            },
            "tracker_config": {
                "max_time_diff": 1.0
            },
            "counter_config": {
                "line_position": 100,
                "count_direction": "positive"
            }
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/track/video",
            json=data
        )
        
        # Check response
        assert response.status_code == 202
        result = response.json()
        assert result["success"] is True
        assert "message" in result
        assert "Processing video tracking in the background" in result["message"]
        
        # Verify the background task was launched
        mock_process_video_tracking.assert_called_once()
