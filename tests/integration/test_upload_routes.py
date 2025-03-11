import pytest
import io
import os
from fastapi import FastAPI
from httpx import AsyncClient
import numpy as np
import cv2
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.database import get_database


@pytest.mark.integration
class TestUploadRoutes:
    @pytest.fixture
    async def client(self):
        # Create a test client for the FastAPI app
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture(autouse=True)
    def mock_db(self, monkeypatch):
        # Mock the MongoDB connection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.uploads = mock_collection
        mock_db.cameras = MagicMock()
        mock_db.conveyors = MagicMock()
        
        # Setup insert_one to return an inserted_id
        mock_result = MagicMock()
        mock_result.inserted_id = "test_id"
        mock_collection.insert_one.return_value = mock_result
        
        # Mock the database connection
        async def mock_get_database():
            return mock_db
        
        monkeypatch.setattr("app.api.v1.endpoints.upload.get_database", mock_get_database)
        return mock_db
    
    @patch("app.services.file_validator.FileValidator.validate_image")
    async def test_upload_image(self, mock_validate_image, client, mock_db):
        # Mock the file validator to return success
        mock_validate_image.return_value = (True, None)
        
        # Create a test image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img_bytes = cv2.imencode('.jpg', img)
        
        # Create form data with the image
        files = {
            "file": ("test.jpg", img_bytes.tobytes(), "image/jpeg")
        }
        form_data = {
            "camera_id": "camera1",
            "conveyor_id": "conveyor1"
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/upload/image",
            files=files,
            data=form_data
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "file_id" in data
        assert data["file_id"] == "test_id"
        
        # Verify DB calls
        mock_db.uploads.insert_one.assert_called_once()
        
    @patch("app.services.file_validator.FileValidator.validate_image")
    async def test_upload_image_invalid(self, mock_validate_image, client):
        # Mock the file validator to return failure
        mock_validate_image.return_value = (False, "Invalid image")
        
        # Create a test image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img_bytes = cv2.imencode('.jpg', img)
        
        # Create form data with the image
        files = {
            "file": ("test.jpg", img_bytes.tobytes(), "image/jpeg")
        }
        form_data = {
            "camera_id": "camera1",
            "conveyor_id": "conveyor1"
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/upload/image",
            files=files,
            data=form_data
        )
        
        # Check response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Invalid image"
        
    @patch("app.services.file_validator.FileValidator.validate_video")
    async def test_upload_video(self, mock_validate_video, client, mock_db):
        # Mock the file validator to return success
        mock_validate_video.return_value = (True, None)
        
        # Create a dummy video file content
        video_content = b'dummy video content'
        
        # Create form data with the video
        files = {
            "file": ("test.mp4", video_content, "video/mp4")
        }
        form_data = {
            "camera_id": "camera1",
            "conveyor_id": "conveyor1"
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/upload/video",
            files=files,
            data=form_data
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "file_id" in data
        assert data["file_id"] == "test_id"
        
        # Verify DB calls
        mock_db.uploads.insert_one.assert_called_once()
        
    @patch("app.services.file_validator.FileValidator.validate_video")
    async def test_upload_multiple_images(self, mock_validate_video, client, mock_db):
        # Mock the file validator to return success
        mock_validate_video.return_value = (True, None)
        
        # Create two test images
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img1_bytes = cv2.imencode('.jpg', img1)
        
        img2 = np.zeros((200, 200, 3), dtype=np.uint8)
        _, img2_bytes = cv2.imencode('.jpg', img2)
        
        # Create form data with multiple images
        files = [
            ("files", ("test1.jpg", img1_bytes.tobytes(), "image/jpeg")),
            ("files", ("test2.jpg", img2_bytes.tobytes(), "image/jpeg"))
        ]
        form_data = {
            "camera_id": "camera1",
            "conveyor_id": "conveyor1"
        }
        
        # Make the request
        response = await client.post(
            "/api/v1/upload/batch",
            files=files,
            data=form_data
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "file_ids" in data
        assert isinstance(data["file_ids"], list)
        assert len(data["file_ids"]) == 2
        
        # Verify DB calls (should be called twice, once for each file)
        assert mock_db.uploads.insert_one.call_count == 2
