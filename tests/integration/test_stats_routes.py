import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from app.main import app


@pytest.mark.integration
class TestStatsRoutes:
    @pytest.fixture
    async def client(self):
        # Create a test client for the FastAPI app
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture(autouse=True)
    def mock_db(self, monkeypatch):
        # Mock the MongoDB connection
        mock_db = MagicMock()
        mock_counts = MagicMock()
        
        # Setup aggregate to return mock count results
        hourly_stats = [
            {
                "_id": {
                    "hour": datetime(2023, 1, 1, 10, 0),
                    "camera_id": "camera1",
                    "conveyor_id": "conveyor1"
                },
                "count": 42,
                "average_confidence": 0.85
            },
            {
                "_id": {
                    "hour": datetime(2023, 1, 1, 11, 0),
                    "camera_id": "camera1",
                    "conveyor_id": "conveyor1"
                },
                "count": 37,
                "average_confidence": 0.82
            }
        ]
        
        daily_stats = [
            {
                "_id": {
                    "date": datetime(2023, 1, 1),
                    "camera_id": "camera1",
                    "conveyor_id": "conveyor1"
                },
                "count": 580,
                "average_confidence": 0.83
            },
            {
                "_id": {
                    "date": datetime(2023, 1, 2),
                    "camera_id": "camera1",
                    "conveyor_id": "conveyor1"
                },
                "count": 612,
                "average_confidence": 0.84
            }
        ]
        
        # Configure the mock to return different results for different pipeline configurations
        def mock_aggregate(pipeline):
            if any("$dateToString" in str(stage) and "%H" in str(stage) for stage in pipeline):
                return hourly_stats
            else:
                return daily_stats
        
        mock_counts.aggregate.side_effect = mock_aggregate
        
        # Assign collections to the mock database
        mock_db.counts = mock_counts
        mock_db.cameras = MagicMock()
        
        # Mock the database connection
        async def mock_get_database():
            return mock_db
        
        # Apply the mock to stats endpoints
        monkeypatch.setattr("app.api.v1.endpoints.stats.get_database", mock_get_database)
        
        return mock_db
    
    async def test_get_hourly_stats(self, client, mock_db):
        # Create query parameters for hourly stats
        params = {
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-01-01T23:59:59",
            "camera_id": "camera1",
            "conveyor_id": "conveyor1"
        }
        
        # Make the request
        response = await client.get(
            "/api/v1/stats/hourly",
            params=params
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "hourly_stats" in result
        assert len(result["hourly_stats"]) == 2
        
        # Verify the stats content
        stats = result["hourly_stats"]
        assert stats[0]["hour"] is not None
        assert stats[0]["count"] == 42
        assert stats[0]["camera_id"] == "camera1"
        assert stats[0]["conveyor_id"] == "conveyor1"
        
        # Verify database calls
        mock_db.counts.aggregate.assert_called_once()
    
    async def test_get_daily_stats(self, client, mock_db):
        # Create query parameters for daily stats
        params = {
            "start_date": "2023-01-01",
            "end_date": "2023-01-07",
            "camera_id": "camera1",
            "conveyor_id": "conveyor1"
        }
        
        # Make the request
        response = await client.get(
            "/api/v1/stats/daily",
            params=params
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "daily_stats" in result
        assert len(result["daily_stats"]) == 2
        
        # Verify the stats content
        stats = result["daily_stats"]
        assert stats[0]["date"] is not None
        assert stats[0]["count"] == 580
        assert stats[0]["camera_id"] == "camera1"
        assert stats[0]["conveyor_id"] == "conveyor1"
        
        # Verify database calls
        mock_db.counts.aggregate.assert_called_once()
    
    async def test_get_camera_stats(self, client, mock_db):
        # Mock the aggregate result for camera stats
        camera_stats = [
            {
                "_id": "camera1",
                "total_count": 1200,
                "average_confidence": 0.85
            },
            {
                "_id": "camera2",
                "total_count": 980,
                "average_confidence": 0.82
            }
        ]
        mock_db.counts.aggregate.return_value = camera_stats
        
        # Create query parameters
        params = {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        # Make the request
        response = await client.get(
            "/api/v1/stats/cameras",
            params=params
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "camera_stats" in result
        assert len(result["camera_stats"]) == 2
        
        # Verify the stats content
        stats = result["camera_stats"]
        assert stats[0]["camera_id"] == "camera1"
        assert stats[0]["total_count"] == 1200
        assert stats[0]["average_confidence"] == 0.85
        
        # Verify database calls
        mock_db.counts.aggregate.assert_called_once()
    
    async def test_get_conveyor_stats(self, client, mock_db):
        # Mock the aggregate result for conveyor stats
        conveyor_stats = [
            {
                "_id": "conveyor1",
                "total_count": 1500,
                "average_confidence": 0.83
            },
            {
                "_id": "conveyor2",
                "total_count": 1100,
                "average_confidence": 0.81
            }
        ]
        mock_db.counts.aggregate.return_value = conveyor_stats
        
        # Create query parameters
        params = {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        # Make the request
        response = await client.get(
            "/api/v1/stats/conveyors",
            params=params
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "conveyor_stats" in result
        assert len(result["conveyor_stats"]) == 2
        
        # Verify the stats content
        stats = result["conveyor_stats"]
        assert stats[0]["conveyor_id"] == "conveyor1"
        assert stats[0]["total_count"] == 1500
        assert stats[0]["average_confidence"] == 0.83
        
        # Verify database calls
        mock_db.counts.aggregate.assert_called_once()
