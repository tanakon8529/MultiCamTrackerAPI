# MultiCamTrackerAPI

A robust API system for tracking objects on conveyor belts using multiple cameras in a factory setting. This system detects, tracks, and counts objects passing on conveyor belts.

## Features
- Multiple camera integration
- Object detection and tracking
- Object counting based on line-crossing events
- REST API with FastAPI
- MongoDB for data storage
- Dockerized deployment

## Technical Components
- **Detector**: Processes image frames to detect objects
- **Tracker**: Follows objects across consecutive frames
- **Counter**: Counts objects crossing predefined lines
- **Database**: Stores tracking and counting data

## Requirements
- Python 3.8+
- Docker & Docker Compose
- MongoDB
- FastAPI

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/MultiCamTrackerAPI.git
cd MultiCamTrackerAPI

# Run with Docker Compose
docker-compose up -d
```

## API Endpoints
- `/api/v1/upload`: Upload images or video for processing
- `/api/v1/track`: Process and track objects
- `/api/v1/stats`: Get statistics on object counts
- `/api/v1/cameras`: Manage camera configurations

## License
See the LICENSE file for details.