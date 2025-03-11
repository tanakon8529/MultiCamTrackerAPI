import pytest
import numpy as np
from app.services.detector import DetectorService, DetectionResult


@pytest.mark.unit
class TestDetectorService:
    def setup_method(self):
        self.detector = DetectorService()
        
    def test_init(self):
        assert self.detector is not None
        
    def test_detect_objects_empty_image(self):
        # Test with empty image
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = self.detector.detect_objects(empty_image)
        
        assert isinstance(result, DetectionResult)
        assert len(result.bboxes) == 0
        assert len(result.scores) == 0
        assert len(result.class_ids) == 0
        
    def test_detect_objects_with_content(self):
        # Create an image with some content (simulating an object)
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        # Draw a rectangle that should be detected as an object
        image[50:150, 50:150] = 255  # White rectangle
        
        result = self.detector.detect_objects(image)
        
        assert isinstance(result, DetectionResult)
        # Since we're using a dummy detector, it should return at least one detection
        assert len(result.bboxes) > 0
        assert len(result.scores) == len(result.bboxes)
        assert len(result.class_ids) == len(result.bboxes)
        
        # Verify that all scores are between 0 and 1
        for score in result.scores:
            assert 0 <= score <= 1
            
    def test_detect_objects_with_batch(self):
        # Test batch processing
        batch_size = 3
        images = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(batch_size)]
        
        # Add content to one of the images
        images[1][30:70, 30:70] = 255
        
        results = self.detector.detect_objects_batch(images)
        
        assert len(results) == batch_size
        assert all(isinstance(result, DetectionResult) for result in results)
        
        # The empty images should have no detections while the one with content should have at least one
        assert len(results[0].bboxes) == 0
        assert len(results[1].bboxes) > 0
        assert len(results[2].bboxes) == 0
