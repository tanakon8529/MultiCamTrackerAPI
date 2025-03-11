import pytest
import io
import numpy as np
import cv2
from app.services.file_validator import FileValidator


@pytest.mark.unit
class TestFileValidator:
    def setup_method(self):
        self.validator = FileValidator()
        
    def test_init(self):
        assert self.validator is not None
        assert self.validator.ALLOWED_IMAGE_EXTENSIONS == {".jpg", ".jpeg", ".png"}
        assert self.validator.ALLOWED_VIDEO_EXTENSIONS == {".mp4", ".avi", ".mov"}
        
    def test_is_valid_image_extension(self):
        # Test valid image extensions
        assert self.validator.is_valid_image_extension("test.jpg") is True
        assert self.validator.is_valid_image_extension("test.jpeg") is True
        assert self.validator.is_valid_image_extension("test.png") is True
        
        # Test invalid image extensions
        assert self.validator.is_valid_image_extension("test.gif") is False
        assert self.validator.is_valid_image_extension("test.bmp") is False
        assert self.validator.is_valid_image_extension("test.txt") is False
        
    def test_is_valid_video_extension(self):
        # Test valid video extensions
        assert self.validator.is_valid_video_extension("test.mp4") is True
        assert self.validator.is_valid_video_extension("test.avi") is True
        assert self.validator.is_valid_video_extension("test.mov") is True
        
        # Test invalid video extensions
        assert self.validator.is_valid_video_extension("test.wmv") is False
        assert self.validator.is_valid_video_extension("test.mkv") is False
        assert self.validator.is_valid_video_extension("test.txt") is False
        
    def test_validate_image_content(self):
        # Create a valid image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img_bytes = cv2.imencode('.jpg', img)
        img_io = io.BytesIO(img_bytes)
        
        # Test valid image content
        result, _ = self.validator.validate_image_content(img_io)
        assert result is True
        
        # Test invalid image content (empty file)
        empty_io = io.BytesIO(b'')
        result, error = self.validator.validate_image_content(empty_io)
        assert result is False
        assert error == "Invalid image content"
        
        # Test invalid image content (text file)
        text_io = io.BytesIO(b'This is not an image')
        result, error = self.validator.validate_image_content(text_io)
        assert result is False
        assert error == "Invalid image content"
        
    @pytest.mark.asyncio
    async def test_validate_image(self):
        # Create a valid image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img_bytes = cv2.imencode('.jpg', img)
        
        # Create a mock UploadFile object
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.file = io.BytesIO(content)
                
            async def read(self):
                return self.file.getvalue()
                
            async def seek(self, position):
                self.file.seek(position)
        
        # Test valid image
        valid_file = MockUploadFile("test.jpg", img_bytes)
        result, _ = await self.validator.validate_image(valid_file)
        assert result is True
        
        # Test invalid extension
        invalid_ext_file = MockUploadFile("test.gif", img_bytes)
        result, error = await self.validator.validate_image(invalid_ext_file)
        assert result is False
        assert error == "Invalid file extension. Allowed extensions: .jpg, .jpeg, .png"
        
        # Test invalid content
        invalid_content_file = MockUploadFile("test.jpg", b'This is not an image')
        result, error = await self.validator.validate_image(invalid_content_file)
        assert result is False
        assert error == "Invalid image content"
