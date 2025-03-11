import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { options, API_PATHS, TEST_DATA, formatUrl, checkStatus, BASE_URL } from './k6_config.js';

export default function() {
  group('Stats API Endpoints', () => {
    // Test hourly stats endpoint
    group('GET Hourly Stats', () => {
      const params = {
        start_date: TEST_DATA.START_DATE,
        end_date: TEST_DATA.END_DATE,
        camera_id: TEST_DATA.CAMERA_ID,
        conveyor_id: TEST_DATA.CONVEYOR_ID
      };
      
      const url = formatUrl(API_PATHS.STATS_HOURLY, params);
      const response = http.get(url);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has hourly_stats property': (r) => JSON.parse(r.body).hourly_stats !== undefined,
      });
      
      sleep(1);
    });
    
    // Test daily stats endpoint
    group('GET Daily Stats', () => {
      const params = {
        start_date: TEST_DATA.START_DATE.split('T')[0], // Just the date part
        end_date: TEST_DATA.END_DATE.split('T')[0],     // Just the date part
        camera_id: TEST_DATA.CAMERA_ID,
        conveyor_id: TEST_DATA.CONVEYOR_ID
      };
      
      const url = formatUrl(API_PATHS.STATS_DAILY, params);
      const response = http.get(url);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has daily_stats property': (r) => JSON.parse(r.body).daily_stats !== undefined,
      });
      
      sleep(1);
    });
    
    // Test camera stats endpoint
    group('GET Camera Stats', () => {
      const params = {
        start_date: TEST_DATA.START_DATE.split('T')[0],
        end_date: TEST_DATA.END_DATE.split('T')[0]
      };
      
      const url = formatUrl(API_PATHS.STATS_CAMERAS, params);
      const response = http.get(url);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has camera_stats property': (r) => JSON.parse(r.body).camera_stats !== undefined,
      });
      
      sleep(1);
    });
    
    // Test conveyor stats endpoint
    group('GET Conveyor Stats', () => {
      const params = {
        start_date: TEST_DATA.START_DATE.split('T')[0],
        end_date: TEST_DATA.END_DATE.split('T')[0]
      };
      
      const url = formatUrl(API_PATHS.STATS_CONVEYORS, params);
      const response = http.get(url);
      
      check(response, {
        'status is 200': (r) => r.status === 200,
        'has conveyor_stats property': (r) => JSON.parse(r.body).conveyor_stats !== undefined,
      });
      
      sleep(1);
    });
  });
}
