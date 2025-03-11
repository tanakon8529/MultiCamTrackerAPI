#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Environment variables
VENV_DIR="venv"
DOCKER_CONTAINERS=("mongodb" "api")

# Print banner
echo -e "${BLUE}"
echo "====================================================="
echo "        MultiCamTrackerAPI - Test Runner              "
echo "====================================================="
echo -e "${NC}"

# Setup function for virtual environment and dependencies
setup_environment() {
  echo -e "${YELLOW}Setting up test environment...${NC}"
  
  # Detect Python version
  python_version=$(python --version 2>&1 | awk '{print $2}')
  echo -e "${YELLOW}Using Python version: ${python_version}${NC}"
  
  # Remove existing virtual environment if it exists
  if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf "$VENV_DIR"
  fi
  
  # Create virtual environment
  echo -e "${YELLOW}Creating fresh virtual environment...${NC}"
  python -m venv $VENV_DIR
  
  # Check if venv was created successfully
  if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo -e "${RED}Error: Failed to create virtual environment.${NC}"
    echo -e "${YELLOW}Continuing without virtual environment. Tests may fail.${NC}"
    return 1
  fi
  
  # Activate virtual environment
  echo -e "${YELLOW}Activating virtual environment...${NC}"
  source $VENV_DIR/bin/activate
  
  # Verify activation
  if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Failed to activate virtual environment.${NC}"
    echo -e "${YELLOW}Continuing without virtual environment. Tests may fail.${NC}"
    return 1
  fi
  
  # Upgrade pip
  echo -e "${YELLOW}Upgrading pip...${NC}"
  pip install --upgrade pip
  
  echo -e "${YELLOW}Installing critical test dependencies...${NC}"
  # Install pytest first to ensure it's available
  pip install pytest pytest-asyncio pytest-cov || {
    echo -e "${RED}Failed to install pytest. Tests will not run.${NC}"
    return 1
  }
  
  echo -e "${YELLOW}Installing core dependencies...${NC}"
  # Install numpy with compatible version
  if [[ $python_version == 3.12* ]]; then
    pip install numpy==1.26.0 || echo -e "${RED}Warning: Failed to install numpy.${NC}"
  else
    pip install numpy==1.24.2 || echo -e "${RED}Warning: Failed to install numpy.${NC}"
  fi
  
  # Install critical dependencies one by one
  echo -e "${YELLOW}Installing key packages...${NC}"
  pip install opencv-python || echo -e "${RED}Warning: Failed to install opencv-python.${NC}"
  
  # Handle the Pydantic compatibility issue with Python 3.12
  if [[ $python_version == 3.12* ]]; then
    echo -e "${YELLOW}Using Python 3.12, installing compatible package versions...${NC}"
    # For Python 3.12 compatibility we need to use more recent Pydantic and FastAPI
    pip install pydantic==2.5.2 || echo -e "${RED}Warning: Failed to install pydantic.${NC}"
    # Install pydantic-settings for Python 3.12
    pip install pydantic-settings==2.1.0 || echo -e "${RED}Warning: Failed to install pydantic-settings.${NC}"
    pip install fastapi==0.108.0 || echo -e "${RED}Warning: Failed to install fastapi.${NC}"
    # Installing other FastAPI dependencies that work with Python 3.12
    pip install starlette==0.31.1 || echo -e "${RED}Warning: Failed to install starlette.${NC}"
    pip install uvicorn==0.24.0 || echo -e "${RED}Warning: Failed to install uvicorn.${NC}"
  else
    # Use the specific versions originally in the requirements for older Python
    pip install pydantic==1.10.7 || echo -e "${RED}Warning: Failed to install pydantic.${NC}"
    pip install fastapi==0.95.0 || echo -e "${RED}Warning: Failed to install fastapi.${NC}" 
    pip install uvicorn==0.21.1 || echo -e "${RED}Warning: Failed to install uvicorn.${NC}"
  fi
  
  # Install MongoDB-related packages
  echo -e "${YELLOW}Installing database dependencies...${NC}"
  pip install pymongo==4.3.3 || echo -e "${RED}Warning: Failed to install pymongo.${NC}"
  pip install motor==3.1.1 || echo -e "${RED}Warning: Failed to install motor.${NC}"
  pip install mongomock==4.1.2 || echo -e "${RED}Warning: Failed to install mongomock.${NC}"
  
  # Install web-related packages
  echo -e "${YELLOW}Installing web dependencies...${NC}"
  pip install httpx==0.24.0 || echo -e "${RED}Warning: Failed to install httpx.${NC}"
  pip install python-multipart==0.0.6 || echo -e "${RED}Warning: Failed to install python-multipart.${NC}"
  pip install aiofiles==23.1.0 || echo -e "${RED}Warning: Failed to install aiofiles.${NC}"
  pip install email-validator==2.0.0 || echo -e "${RED}Warning: Failed to install email-validator.${NC}"
  
  # Create compatibility patch for older code with newer Pydantic if necessary
  if [[ $python_version == 3.12* ]]; then
    echo -e "${YELLOW}Creating compatibility layer for Pydantic v2 with v1 code...${NC}"
    mkdir -p "$VENV_DIR/lib/python$python_version/site-packages/compat"
    cat > "$VENV_DIR/lib/python$python_version/site-packages/compat/pydantic_v1.py" << EOF
# Compatibility layer for code written for Pydantic v1 but running with Pydantic v2
from typing import Any, Dict, Type, TypeVar, Optional, Union, get_type_hints
import sys
import inspect
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, create_model

class BaseModel(PydanticBaseModel):
    """Compatibility wrapper for Pydantic v1 code running on v2"""
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert to dict - compatibility with v1"""
        exclude_none = kwargs.pop("exclude_none", False)
        result = self.model_dump(*args, **kwargs)
        if exclude_none:
            return {k: v for k, v in result.items() if v is not None}
        return result
EOF

    # Add compatibility import to PYTHONPATH for tests
    echo -e "# Add compatibility layer" >> "$VENV_DIR/bin/activate"
    echo -e "export PYTHONPATH=\"$VENV_DIR/lib/python$python_version/site-packages/compat:\$PYTHONPATH\"" >> "$VENV_DIR/bin/activate"
    source "$VENV_DIR/bin/activate"
  fi

  # Verify our test environment
  echo -e "${YELLOW}Verifying test environment...${NC}"
  python -c "import pytest; import numpy; import cv2; import fastapi; import pydantic; print('Core dependencies verified successfully!')" || {
    echo -e "${RED}Warning: Some core dependencies could not be imported.${NC}"
    echo -e "${RED}Tests may fail due to missing or incompatible packages.${NC}"
  }
  
  echo -e "${GREEN}Environment setup complete.${NC}"
}

# Function to run start.sh
run_startup_script() {
  echo -e "${YELLOW}Running startup script...${NC}"
  
  # Check if start.sh exists and is executable
  if [ -f "./start.sh" ]; then
    # Make start.sh executable if it's not already
    if [ ! -x "./start.sh" ]; then
      chmod +x ./start.sh
    fi
    
    # Run the start script
    ./start.sh
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Startup script completed successfully.${NC}"
    else
      echo -e "${RED}Startup script failed with exit code: $?${NC}"
      echo -e "${YELLOW}Continuing with tests anyway...${NC}"
    fi
  else
    echo -e "${RED}Startup script ./start.sh not found.${NC}"
    echo -e "${YELLOW}Creating Docker containers manually...${NC}"
    
    # Create containers manually as fallback
    docker-compose up -d
  fi
  
  # Wait for services to be ready
  echo -e "${YELLOW}Waiting for services to be ready...${NC}"
  sleep 5
}

# Function to clean up Docker resources
cleanup_docker() {
  echo -e "${YELLOW}Cleaning up Docker resources...${NC}"
  
  # Stop and remove containers
  docker-compose down
  
  # Remove images if requested
  if [ "$1" = "full" ]; then
    echo -e "${YELLOW}Removing Docker images...${NC}"
    docker rmi $(docker images -q 'multicamtrackerapi_*') 2>/dev/null || true
  fi
  
  echo -e "${GREEN}Cleanup complete.${NC}"
}

# Function to deactivate virtual environment
cleanup_venv() {
  if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Deactivating virtual environment...${NC}"
    deactivate 2>/dev/null || true
  fi
}

# Trap function to ensure cleanup on exit
cleanup_on_exit() {
  echo -e "${YELLOW}Performing cleanup...${NC}"
  cleanup_docker
  cleanup_venv
  echo -e "${GREEN}All resources cleaned up.${NC}"
}

# Register cleanup function to run on script exit
trap cleanup_on_exit EXIT

# Function to show menu and get user choice with timeout
show_menu() {
  echo -e "${GREEN}Choose a test option:${NC}"
  echo "1) Run all unit tests"
  echo "2) Run all integration tests"
  echo "3) Run specific test file"
  echo "4) Run load tests with k6"
  echo "5) Run all tests (unit + integration)"
  echo "6) Exit"
  
  # Initialize choice with default option
  choice=5  # Default to run all tests
  
  # Set up countdown
  echo -e "${YELLOW}Automatically running all tests in 5 seconds...${NC}"
  echo -n "Enter your choice (1-6): "
  
  # Read with timeout using read command with -t option
  read -t 5 user_choice
  
  # If user entered something and it's a valid number
  if [[ -n "$user_choice" ]] && [[ "$user_choice" =~ ^[1-6]$ ]]; then
    choice=$user_choice
  else
    echo -e "\n${YELLOW}No input received within 5 seconds. Running all tests...${NC}"
  fi
  
  return $choice
}

# Function to run unit tests
run_unit_tests() {
  echo -e "${YELLOW}Running unit tests...${NC}"
  
  # Verify we're in a virtual environment
  if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Not running in a virtual environment. Tests may fail.${NC}"
    return 1
  fi
  
  # Check if pytest is available
  if ! python -m pytest --version >/dev/null 2>&1; then
    echo -e "${RED}Error: pytest is not installed. Installing it now...${NC}"
    pip install pytest
  fi
  
  python -m pytest tests/unit -v
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Unit tests completed successfully.${NC}"
  else
    ERROR_CODE=$?
    echo -e "${RED}Unit tests failed with exit code: ${ERROR_CODE}${NC}"
    echo -e "${RED}Check the test output above for specific assertion failures or errors.${NC}"
    echo -e "${YELLOW}Run specific test files individually for more detailed debugging.${NC}"
  fi
}

# Function to run integration tests
run_integration_tests() {
  echo -e "${YELLOW}Running integration tests...${NC}"
  
  # Verify we're in a virtual environment
  if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Not running in a virtual environment. Tests may fail.${NC}"
    return 1
  fi
  
  # Check if pytest is available
  if ! python -m pytest --version >/dev/null 2>&1; then
    echo -e "${RED}Error: pytest is not installed. Installing it now...${NC}"
    pip install pytest
  fi
  
  python -m pytest tests/integration -v
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Integration tests completed successfully.${NC}"
  else
    ERROR_CODE=$?
    echo -e "${RED}Integration tests failed with exit code: ${ERROR_CODE}${NC}"
    echo -e "${RED}Check the test output above for specific API route failures.${NC}"
    echo -e "${YELLOW}Common issues include:${NC}"
    echo -e "${YELLOW}- Mock database configuration errors${NC}"
    echo -e "${YELLOW}- API route parameter mismatches${NC}"
    echo -e "${YELLOW}- Assertion failures in response validation${NC}"
  fi
}

# Function to run specific test file
run_specific_test() {
  echo -e "${YELLOW}Available test files:${NC}"
  
  # Find all test files
  test_files=($(find tests -name "test_*.py"))
  
  # List all test files with numbers
  for i in "${!test_files[@]}"; do
    echo "$((i+1))) ${test_files[$i]}"
  done
  
  read -p "Enter the number of the test file to run: " file_number
  
  # Validate input
  if [[ "$file_number" =~ ^[0-9]+$ ]] && [ "$file_number" -ge 1 ] && [ "$file_number" -le "${#test_files[@]}" ]; then
    selected_file="${test_files[$((file_number-1))]}"
    echo -e "${YELLOW}Running test file: ${selected_file}${NC}"
    python -m pytest "$selected_file" -v
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Test completed successfully.${NC}"
    else
      ERROR_CODE=$?
      echo -e "${RED}Test failed with exit code: ${ERROR_CODE}${NC}"
      echo -e "${RED}Failure details:${NC}"
      echo -e "${YELLOW}- Check test assertions and expected values${NC}"
      echo -e "${YELLOW}- Verify any mock objects or fixtures are correctly configured${NC}"
      echo -e "${YELLOW}- Look for ImportError or AttributeError that may indicate code structure issues${NC}"
    fi
  else
    echo -e "${RED}Invalid selection.${NC}"
  fi
}

# Function to run load tests with k6
run_load_tests() {
  echo -e "${YELLOW}Available load test scripts:${NC}"
  
  # Find all k6 scripts
  k6_files=($(find tests/load -name "*.js" | grep -v "k6_config.js"))
  
  # List all k6 files with numbers
  for i in "${!k6_files[@]}"; do
    echo "$((i+1))) ${k6_files[$i]}"
  done
  
  echo "$((${#k6_files[@]}+1))) Run all load tests"
  
  read -p "Enter the number of the load test to run: " file_number
  
  # Check if k6 is installed
  if ! command -v k6 &> /dev/null; then
    echo -e "${RED}Error: k6 is not installed or not in your PATH.${NC}"
    echo -e "${YELLOW}Install k6 with Homebrew: brew install k6${NC}"
    echo -e "${YELLOW}Or visit https://k6.io/docs/getting-started/installation/ for other installation methods.${NC}"
    return 1
  fi
  
  # Validate input
  if [[ "$file_number" =~ ^[0-9]+$ ]]; then
    if [ "$file_number" -le "${#k6_files[@]}" ]; then
      # Run specific k6 test
      selected_file="${k6_files[$((file_number-1))]}"
      echo -e "${YELLOW}Running load test: ${selected_file}${NC}"
      k6 run "$selected_file"
    elif [ "$file_number" -eq "$((${#k6_files[@]}+1))" ]; then
      # Run all load tests
      echo -e "${YELLOW}Running all load tests with main.js${NC}"
      k6 run tests/load/main.js
    else
      echo -e "${RED}Invalid selection.${NC}"
      return 1
    fi
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Load test completed.${NC}"
    else
      ERROR_CODE=$?
      echo -e "${RED}Load test failed with exit code: ${ERROR_CODE}${NC}"
      echo -e "${RED}Common load test failures:${NC}"
      echo -e "${YELLOW}- API server not running or unreachable${NC}"
      echo -e "${YELLOW}- Endpoint configuration mismatches in k6_config.js${NC}"
      echo -e "${YELLOW}- Thresholds exceeded (response time, error rate)${NC}"
      echo -e "${YELLOW}- Missing dependencies or incorrect file paths${NC}"
    fi
  else
    echo -e "${RED}Invalid selection.${NC}"
    return 1
  fi
}

# Function to run all tests
run_all_tests() {
  echo -e "${YELLOW}Running all tests...${NC}"
  
  # Verify we're in a virtual environment
  if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Not running in a virtual environment. Tests may fail.${NC}"
    return 1
  fi
  
  # Check if pytest is available
  if ! python -m pytest --version >/dev/null 2>&1; then
    echo -e "${RED}Error: pytest is not installed. Installing it now...${NC}"
    pip install pytest
  fi
  
  python -m pytest
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests completed successfully.${NC}"
  else
    ERROR_CODE=$?
    echo -e "${RED}Some tests failed with exit code: ${ERROR_CODE}${NC}"
    echo -e "${RED}To identify specific failures:${NC}"
    echo -e "${YELLOW}- Run unit tests and integration tests separately${NC}"
    echo -e "${YELLOW}- Check output above for specific test case failures${NC}"
    echo -e "${YELLOW}- Run individual test files for more detailed information${NC}"
  fi
}

# Main program
main() {
  # Setup environment
  setup_environment
  
  # Run startup script
  run_startup_script
  
  # Main menu loop
  while true; do
    show_menu
    choice=$?
    echo ""
    
    case $choice in
      1)
        run_unit_tests
        ;;
      2)
        run_integration_tests
        ;;
      3)
        run_specific_test
        ;;
      4)
        run_load_tests
        ;;
      5)
        run_all_tests
        ;;
      6)
        echo -e "${GREEN}Exiting test runner.${NC}"
        exit 0
        ;;
      *)
        echo -e "${RED}Invalid choice. Please enter a number between 1 and 6.${NC}"
        ;;
    esac
    
    echo ""
    echo -e "${BLUE}=====================================================================${NC}"
  done
}

# Run the main program
main
