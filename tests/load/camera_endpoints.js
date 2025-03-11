import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { options, API_PATHS, TEST_DATA, formatUrl, checkStatus, BASE_URL } from './k6_config.js';

export default function() {
  group('Camera API Endpoints', () => {
    // Test get all cameras endpoint
    group('GET All Cameras', () => {
      const url = `${BASE_URL}${API_PATHS.CAMERAS}/`;
      const response = http.get(url);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has cameras property': (r) => JSON.parse(r.body).cameras !== undefined,
      });
      
      sleep(1);
    });
    
    // Test get specific camera endpoint
    group('GET Camera by ID', () => {
      const url = `${BASE_URL}${API_PATHS.CAMERAS}/camera1`;
      const response = http.get(url);
      
      // The response might be 200 or 404 depending on if camera1 exists
      check(response, {
        'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      });
      
      sleep(1);
    });
    
    // Test create camera endpoint
    group('POST Create Camera', () => {
      const url = `${BASE_URL}${API_PATHS.CAMERAS}/`;
      const payload = JSON.stringify({
        name: `Test Camera ${Math.floor(Math.random() * 1000)}`,
        location: 'Load Test Location',
        description: 'Camera created during load testing',
        configuration: {
          ip: '192.168.1.100',
          port: 8080
        }
      });
      
      const params = {
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      const response = http.post(url, payload, params);
      
      check(response, {
        'status is 201': (r) => r.status === 201,
        'has success property': (r) => JSON.parse(r.body).success === true,
        'has camera_id property': (r) => JSON.parse(r.body).camera_id !== undefined,
      });
      
      sleep(1);
    });
    
    // Test get all conveyors endpoint
    group('GET All Conveyors', () => {
      const url = `${BASE_URL}${API_PATHS.CONVEYORS}/`;
      const response = http.get(url);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has conveyors property': (r) => JSON.parse(r.body).conveyors !== undefined,
      });
      
      sleep(1);
    });
    
    // Test create conveyor endpoint
    group('POST Create Conveyor', () => {
      const url = `${BASE_URL}${API_PATHS.CONVEYORS}/`;
      const payload = JSON.stringify({
        name: `Test Conveyor ${Math.floor(Math.random() * 1000)}`,
        location: 'Load Test Location',
        description: 'Conveyor created during load testing',
        speed: 1.5,
        direction: 'left-to-right'
      });
      
      const params = {
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      const response = http.post(url, payload, params);
      
      check(response, {
        'status is 201': (r) => r.status === 201,
        'has success property': (r) => JSON.parse(r.body).success === true,
        'has conveyor_id property': (r) => JSON.parse(r.body).conveyor_id !== undefined,
      });
      
      sleep(1);
    });
  });
}
