# MultiCamTrackerAPI

A robust and scalable API system for tracking objects on conveyor belts using multiple cameras in a factory setting. This system efficiently detects, tracks, and counts objects passing on conveyor belts with high accuracy and minimal latency.

[![Build Status](https://github.com/tanakon8529/MultiCamTrackerAPI/actions/workflows/test.yml/badge.svg)](https://github.com/tanakon8529/MultiCamTrackerAPI/actions/workflows/test.yml)
[![Deploy Status](https://github.com/tanakon8529/MultiCamTrackerAPI/actions/workflows/deploy.yml/badge.svg)](https://github.com/tanakon8529/MultiCamTrackerAPI/actions/workflows/deploy.yml)

## 🚀 Features

- **Real-time Processing**: Fast, efficient object detection and tracking
- **Multi-Camera Support**: Seamless integration of multiple camera feeds
- **Intelligent Tracking**: Advanced algorithms for consistent object tracking
- **Line-Crossing Detection**: Accurately count objects crossing defined boundaries
- **Robust API**: RESTful API built with FastAPI for easy integration
- **Persistence**: MongoDB for efficient data storage and retrieval
- **Scalable**: Containerized with Docker for easy deployment and scaling
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Cloud-Ready**: Optimized for AWS deployment (ECR/ECS)

## 🔧 Technical Architecture

### Core Components
- **Detector Service**: Processes image frames to detect objects using computer vision
- **Tracker Service**: Maintains object identity across consecutive frames
- **Counter Service**: Analyzes tracks to count objects crossing predefined lines
- **Database Service**: Manages data persistence in MongoDB
- **API Gateway**: Handles HTTP requests and orchestrates service interactions

### Technology Stack
- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Computer Vision**: OpenCV, NumPy
- **Database**: MongoDB, Motor (async driver)
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Cloud**: AWS (ECR, ECS)

## 📋 Requirements

- Python 3.12+
- Docker & Docker Compose
- MongoDB 5.0+
- AWS CLI (for production deployment)

## 💻 Installation & Setup

### Quick Start (Recommended)
```bash
# Clone the repository
git clone https://github.com/tanakon8529/MultiCamTrackerAPI.git
cd MultiCamTrackerAPI

# Make the startup script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

The `start.sh` script automatically:
- Creates an `.env` file from `.env.example` if needed
- Creates the necessary `uploads` directory
- Builds and starts Docker containers
- Provides status information and URLs to access the API

### Local Development
```bash
# Clone the repository
git clone https://github.com/tanakon8529/MultiCamTrackerAPI.git
cd MultiCamTrackerAPI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
uvicorn app.main:app --reload
```

### Docker Deployment
```bash
# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment to AWS
The project includes GitHub Actions workflows for automated deployment:

1. Build and push images to Amazon ECR
2. Deploy to Amazon ECS
3. Perform automated releases with semantic versioning

See `.github/workflows/` directory for detailed configuration.

## 🧪 Testing

### Quick Testing (Recommended)
```bash
# Make the test script executable
chmod +x run_tests.sh

# Run the test script
./run_tests.sh
```

The `run_tests.sh` script provides an interactive menu for testing:
1. Run unit tests only
2. Run integration tests only
3. Run a specific test file
4. Run load tests with k6
5. Run all tests (unit + integration)

The script automatically:
- Sets up a Python virtual environment
- Installs all necessary dependencies with version compatibility
- Starts required Docker containers
- Runs the selected tests
- Provides detailed error information when tests fail
- Cleans up resources when done

### Manual Testing
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run with coverage report
pytest --cov=app

# Run specific test files
pytest tests/unit/test_detector.py
```

## 📚 API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Camera Management
- `GET /api/v1/cameras` - List all configured cameras
- `POST /api/v1/cameras` - Register a new camera
- `GET /api/v1/cameras/{camera_id}` - Get camera details
- `PUT /api/v1/cameras/{camera_id}` - Update camera configuration
- `DELETE /api/v1/cameras/{camera_id}` - Remove a camera

#### Tracking Operations
- `POST /api/v1/upload` - Upload images or video for processing
- `POST /api/v1/track` - Process and track objects
- `GET /api/v1/track/{track_id}` - Get details for a specific tracking session

#### Analytics
- `GET /api/v1/stats` - Get object counting statistics
- `GET /api/v1/stats/daily` - Get daily aggregated counts
- `GET /api/v1/stats/by-camera/{camera_id}` - Get statistics for a specific camera

## 🛠️ Development

### Project Structure
```
MultiCamTrackerAPI/
├── app/                    # Application code
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── main.py             # Application entry point
├── tests/                  # Test suites
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── load/               # Load tests
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker build configuration
└── requirements.txt        # Python dependencies
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes using conventional commits
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Acknowledgments

- OpenCV community for computer vision tools
- FastAPI team for the excellent API framework