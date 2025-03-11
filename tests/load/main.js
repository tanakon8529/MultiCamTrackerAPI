import { sleep, group } from 'k6';
import { options } from './k6_config.js';

// Import individual test scripts
import statsTests from './stats_endpoints.js';
import cameraTests from './camera_endpoints.js';
import trackTests from './track_endpoints.js';
import uploadTests from './upload_endpoints.js';

export { options };

export default function() {
  // Run all test groups in sequence
  
  group('Upload Endpoints Tests', () => {
    uploadTests();
    sleep(2);
  });
  
  group('Track Endpoints Tests', () => {
    trackTests();
    sleep(2);
  });
  
  group('Stats Endpoints Tests', () => {
    statsTests();
    sleep(2);
  });
  
  group('Camera Endpoints Tests', () => {
    cameraTests();
    sleep(2);
  });
}
