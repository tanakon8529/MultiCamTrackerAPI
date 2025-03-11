import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import json
from bson import ObjectId

from app.main import app


# Mock ObjectId for testing
class MockObjectId(str):
    def __init__(self, id_str=None):
        self.id_str = id_str or "60c72b2b5e8e29c9c9c5e7a5"
    
    def __str__(self):
        return self.id_str


@pytest.mark.integration
class TestCameraRoutes:
    @pytest.fixture
    async def client(self):
        # Create a test client for the FastAPI app
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture(autouse=True)
    def mock_db(self, monkeypatch):
        # Mock the MongoDB connection
        mock_db = MagicMock()
        mock_cameras = MagicMock()
        mock_conveyors = MagicMock()
        
        # Setup camera collection mock data
        mock_camera = {
            "_id": MockObjectId("camera123"),
            "name": "Test Camera",
            "location": "Factory Floor 1",
            "description": "Test camera for integration tests",
            "configuration": {
                "ip": "192.168.1.100",
                "port": 8080
            }
        }
        
        # Setup conveyor collection mock data
        mock_conveyor = {
            "_id": MockObjectId("conveyor123"),
            "name": "Test Conveyor",
            "location": "Factory Floor 1",
            "description": "Test conveyor for integration tests",
            "speed": 1.5,
            "direction": "left-to-right"
        }
        
        # Setup find methods to return lists
        mock_cameras.find.return_value = [mock_camera]
        mock_conveyors.find.return_value = [mock_conveyor]
        
        # Setup find_one to return a single document
        mock_cameras.find_one.return_value = mock_camera
        mock_conveyors.find_one.return_value = mock_conveyor
        
        # Setup insert_one to return a mock result with an inserted_id
        mock_result = MagicMock()
        mock_result.inserted_id = MockObjectId()
        mock_cameras.insert_one.return_value = mock_result
        mock_conveyors.insert_one.return_value = mock_result
        
        # Setup update_one to return a mock result
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_cameras.update_one.return_value = mock_update_result
        mock_conveyors.update_one.return_value = mock_update_result
        
        # Setup delete_one to return a mock result
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1
        mock_cameras.delete_one.return_value = mock_delete_result
        mock_conveyors.delete_one.return_value = mock_delete_result
        
        # Assign collections to the mock database
        mock_db.cameras = mock_cameras
        mock_db.conveyors = mock_conveyors
        
        # Mock the database connection
        async def mock_get_database():
            return mock_db
        
        # Apply the mock to camera endpoints
        monkeypatch.setattr("app.api.v1.endpoints.cameras.get_database", mock_get_database)
        
        return mock_db
    
    async def test_get_cameras(self, client, mock_db):
        # Make the request to get all cameras
        response = await client.get("/api/v1/cameras/")
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "cameras" in result
        assert len(result["cameras"]) == 1
        
        # Verify the camera data
        camera = result["cameras"][0]
        assert camera["name"] == "Test Camera"
        assert camera["location"] == "Factory Floor 1"
        
        # Verify database calls
        mock_db.cameras.find.assert_called_once()
    
    async def test_get_camera_by_id(self, client, mock_db):
        # Make the request to get a specific camera
        response = await client.get("/api/v1/cameras/camera123")
        
        # Check response
        assert response.status_code == 200
        camera = response.json()
        assert camera["name"] == "Test Camera"
        assert camera["location"] == "Factory Floor 1"
        
        # Verify database calls
        mock_db.cameras.find_one.assert_called_once()
    
    async def test_create_camera(self, client, mock_db):
        # Create camera data
        camera_data = {
            "name": "New Test Camera",
            "location": "Factory Floor 2",
            "description": "A new test camera",
            "configuration": {
                "ip": "192.168.1.101",
                "port": 8080
            }
        }
        
        # Make the request to create a camera
        response = await client.post(
            "/api/v1/cameras/",
            json=camera_data
        )
        
        # Check response
        assert response.status_code == 201
        result = response.json()
        assert result["success"] is True
        assert "camera_id" in result
        
        # Verify database calls
        mock_db.cameras.insert_one.assert_called_once()
    
    async def test_update_camera(self, client, mock_db):
        # Create update data
        update_data = {
            "name": "Updated Test Camera",
            "location": "Factory Floor 1",
            "description": "Updated test camera"
        }
        
        # Make the request to update a camera
        response = await client.put(
            "/api/v1/cameras/camera123",
            json=update_data
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["modified_count"] == 1
        
        # Verify database calls
        mock_db.cameras.update_one.assert_called_once()
    
    async def test_delete_camera(self, client, mock_db):
        # Make the request to delete a camera
        response = await client.delete("/api/v1/cameras/camera123")
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["deleted_count"] == 1
        
        # Verify database calls
        mock_db.cameras.delete_one.assert_called_once()
    
    async def test_get_conveyors(self, client, mock_db):
        # Make the request to get all conveyors
        response = await client.get("/api/v1/conveyors/")
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "conveyors" in result
        assert len(result["conveyors"]) == 1
        
        # Verify the conveyor data
        conveyor = result["conveyors"][0]
        assert conveyor["name"] == "Test Conveyor"
        assert conveyor["location"] == "Factory Floor 1"
        
        # Verify database calls
        mock_db.conveyors.find.assert_called_once()
    
    async def test_get_conveyor_by_id(self, client, mock_db):
        # Make the request to get a specific conveyor
        response = await client.get("/api/v1/conveyors/conveyor123")
        
        # Check response
        assert response.status_code == 200
        conveyor = response.json()
        assert conveyor["name"] == "Test Conveyor"
        assert conveyor["location"] == "Factory Floor 1"
        
        # Verify database calls
        mock_db.conveyors.find_one.assert_called_once()
    
    async def test_create_conveyor(self, client, mock_db):
        # Create conveyor data
        conveyor_data = {
            "name": "New Test Conveyor",
            "location": "Factory Floor 2",
            "description": "A new test conveyor",
            "speed": 2.0,
            "direction": "right-to-left"
        }
        
        # Make the request to create a conveyor
        response = await client.post(
            "/api/v1/conveyors/",
            json=conveyor_data
        )
        
        # Check response
        assert response.status_code == 201
        result = response.json()
        assert result["success"] is True
        assert "conveyor_id" in result
        
        # Verify database calls
        mock_db.conveyors.insert_one.assert_called_once()
    
    async def test_update_conveyor(self, client, mock_db):
        # Create update data
        update_data = {
            "name": "Updated Test Conveyor",
            "location": "Factory Floor 1",
            "speed": 2.5
        }
        
        # Make the request to update a conveyor
        response = await client.put(
            "/api/v1/conveyors/conveyor123",
            json=update_data
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["modified_count"] == 1
        
        # Verify database calls
        mock_db.conveyors.update_one.assert_called_once()
    
    async def test_delete_conveyor(self, client, mock_db):
        # Make the request to delete a conveyor
        response = await client.delete("/api/v1/conveyors/conveyor123")
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["deleted_count"] == 1
        
        # Verify database calls
        mock_db.conveyors.delete_one.assert_called_once()
