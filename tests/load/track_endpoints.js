import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { options, API_PATHS, TEST_DATA, formatUrl, checkStatus, BASE_URL } from './k6_config.js';

export default function() {
  group('Track API Endpoints', () => {
    // Test track image endpoint
    group('POST Track Image', () => {
      const url = `${BASE_URL}${API_PATHS.TRACK_IMAGE}`;
      const payload = JSON.stringify({
        file_id: TEST_DATA.FILE_ID,
        detector_config: {
          confidence_threshold: 0.5,
          nms_threshold: 0.4
        },
        tracker_config: {
          max_time_diff: 1.0
        },
        counter_config: {
          line_position: 100,
          count_direction: 'positive'
        }
      });
      
      const params = {
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      const response = http.post(url, payload, params);
      
      // This might return 200 or 404 if the file_id doesn't exist
      check(response, {
        'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      });
      
      if (response.status === 200) {
        check(response, {
          'has success property': (r) => JSON.parse(r.body).success === true,
          'has tracking_id property': (r) => JSON.parse(r.body).tracking_id !== undefined,
        });
      }
      
      sleep(1);
    });
    
    // Test track batch endpoint
    group('POST Track Batch', () => {
      const url = `${BASE_URL}${API_PATHS.TRACK_BATCH}`;
      const payload = JSON.stringify({
        file_ids: TEST_DATA.FILE_IDS,
        detector_config: {
          confidence_threshold: 0.5,
          nms_threshold: 0.4
        },
        tracker_config: {
          max_time_diff: 1.0
        },
        counter_config: {
          line_position: 100,
          count_direction: 'positive'
        }
      });
      
      const params = {
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      const response = http.post(url, payload, params);
      
      // This should return 202 because it's a background task
      check(response, {
        'status is 202': (r) => r.status === 202,
        'has success property': (r) => JSON.parse(r.body).success === true,
        'has message property': (r) => JSON.parse(r.body).message !== undefined,
      });
      
      sleep(1);
    });
    
    // Test track video endpoint
    group('POST Track Video', () => {
      const url = `${BASE_URL}${API_PATHS.TRACK_VIDEO}`;
      const payload = JSON.stringify({
        file_id: TEST_DATA.FILE_ID,
        detector_config: {
          confidence_threshold: 0.5,
          nms_threshold: 0.4,
          sample_rate: 5
        },
        tracker_config: {
          max_time_diff: 1.0
        },
        counter_config: {
          line_position: 100,
          count_direction: 'positive'
        }
      });
      
      const params = {
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      const response = http.post(url, payload, params);
      
      // This should return 202 because it's a background task
      check(response, {
        'status is 202 or 404': (r) => r.status === 202 || r.status === 404,
      });
      
      if (response.status === 202) {
        check(response, {
          'has success property': (r) => JSON.parse(r.body).success === true,
          'has message property': (r) => JSON.parse(r.body).message !== undefined,
        });
      }
      
      sleep(1);
    });
  });
}
