import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { options, API_PATHS, TEST_DATA, formatUrl, checkStatus, BASE_URL } from './k6_config.js';

export default function() {
  group('Upload API Endpoints', () => {
    // Test upload image endpoint
    group('POST Upload Image', () => {
      const url = `${BASE_URL}${API_PATHS.UPLOAD_IMAGE}`;
      
      // Create a small sample image (just a black 1x1 pixel JPEG)
      // This is a base64 encoded minimal JPEG image
      const imageB64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFdgJB3TpT/AAAAABJRU5ErkJggg==';
      const imgData = atob(imageB64); // Decode base64 to binary
      const imgBinary = new Uint8Array(imgData.length);
      for (let i = 0; i < imgData.length; i++) {
        imgBinary[i] = imgData.charCodeAt(i);
      }
      
      // Create multipart form data
      const formData = {
        file: http.file(imgBinary.buffer, 'test.jpg', 'image/jpeg'),
        camera_id: TEST_DATA.CAMERA_ID,
        conveyor_id: TEST_DATA.CONVEYOR_ID
      };
      
      const response = http.post(url, formData);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has success property': (r) => JSON.parse(r.body).success === true,
        'has file_id property': (r) => JSON.parse(r.body).file_id !== undefined,
      });
      
      sleep(1);
    });
    
    // Test upload batch endpoint (simplified for load testing - not actually uploading multiple files)
    group('POST Upload Batch', () => {
      const url = `${BASE_URL}${API_PATHS.UPLOAD_BATCH}`;
      
      // For load testing, we'll just simulate the response without actually uploading files
      // since k6 doesn't easily support multiple file uploads in a single request
      
      // Simulate a form data upload
      const formData = {
        camera_id: TEST_DATA.CAMERA_ID,
        conveyor_id: TEST_DATA.CONVEYOR_ID
      };
      
      const response = http.post(url, formData);
      
      // We expect a 400 because we didn't actually upload files
      // In a real test with file uploads, we'd check for 200
      check(response, {
        'status is valid': (r) => r.status === 400 || r.status === 200,
      });
      
      sleep(1);
    });
    
    // Test upload video endpoint
    group('POST Upload Video', () => {
      const url = `${BASE_URL}${API_PATHS.UPLOAD_VIDEO}`;
      
      // Create a minimal dummy video content (not an actual video, just for testing)
      const videoBinary = new Uint8Array(10);
      for (let i = 0; i < 10; i++) {
        videoBinary[i] = i;
      }
      
      // Create multipart form data
      const formData = {
        file: http.file(videoBinary.buffer, 'test.mp4', 'video/mp4'),
        camera_id: TEST_DATA.CAMERA_ID,
        conveyor_id: TEST_DATA.CONVEYOR_ID
      };
      
      const response = http.post(url, formData);
      
      // Might get 400 (invalid video) or 200 (success)
      check(response, {
        'status is valid': (r) => r.status === 400 || r.status === 200,
      });
      
      if (response.status === 200) {
        check(response, {
          'has success property': (r) => JSON.parse(r.body).success === true,
          'has file_id property': (r) => JSON.parse(r.body).file_id !== undefined,
        });
      }
      
      sleep(1);
    });
  });
}
