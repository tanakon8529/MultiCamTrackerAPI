export const options = {
  // Shared options for all load tests
  
  // Define stages for ramping up and down the load
  stages: [
    { duration: '30s', target: 10 }, // Ramp up to 10 users over 30 seconds
    { duration: '1m', target: 10 },  // Stay at 10 users for 1 minute
    { duration: '30s', target: 0 },  // Ramp down to 0 users over 30 seconds
  ],
  
  // Thresholds for test success
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],     // Less than 10% of requests should fail
  },
  
  // Default options for all HTTP requests
  noConnectionReuse: false,
  userAgent: 'K6LoadTest/1.0',
};

// Base URL for the API
export const BASE_URL = 'http://localhost:8000';

// Common API paths
export const API_PATHS = {
  UPLOAD_IMAGE: '/api/v1/upload/image',
  UPLOAD_VIDEO: '/api/v1/upload/video',
  UPLOAD_BATCH: '/api/v1/upload/batch',
  TRACK_IMAGE: '/api/v1/track/image',
  TRACK_VIDEO: '/api/v1/track/video',
  TRACK_BATCH: '/api/v1/track/batch',
  STATS_HOURLY: '/api/v1/stats/hourly',
  STATS_DAILY: '/api/v1/stats/daily',
  STATS_CAMERAS: '/api/v1/stats/cameras',
  STATS_CONVEYORS: '/api/v1/stats/conveyors',
  CAMERAS: '/api/v1/cameras',
  CONVEYORS: '/api/v1/conveyors',
};

// Test data for requests
export const TEST_DATA = {
  CAMERA_ID: 'camera1',
  CONVEYOR_ID: 'conveyor1',
  FILE_ID: '60c72b2b5e8e29c9c9c5e7a5',
  FILE_IDS: ['60c72b2b5e8e29c9c9c5e7a5', '60c72b2b5e8e29c9c9c5e7a6'],
  START_DATE: '2023-01-01T00:00:00',
  END_DATE: '2023-01-07T23:59:59',
};

// Helper function to format URLs with query parameters
export function formatUrl(path, params = {}) {
  const url = new URL(BASE_URL + path);
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      url.searchParams.append(key, value);
    }
  });
  
  return url.toString();
}

// Helper to check response status
export function checkStatus(response, expectedStatus = 200) {
  if (response.status !== expectedStatus) {
    console.error(`Expected status ${expectedStatus} but got ${response.status}`);
    console.error(`Response body: ${response.body}`);
  }
  return response.status === expectedStatus;
}
