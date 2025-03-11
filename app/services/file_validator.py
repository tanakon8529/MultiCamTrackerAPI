from fastapi import UploadFile
import imghdr
import os
import logging
from typing import List, Tuple, Set, BinaryIO, Optional

logger = logging.getLogger(__name__)

# Valid image and video extensions
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
VALID_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']

async def validate_image(file: UploadFile) -> bool:
    """
    Validate that the file is an image.
    
    Args:
        file (UploadFile): The file to validate
        
    Returns:
        bool: True if file is a valid image, False otherwise
    """
    # Check extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in VALID_IMAGE_EXTENSIONS:
        logger.warning(f"Invalid image extension: {ext}")
        return False
    
    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    # Use imghdr to check file type
    image_type = imghdr.what(None, h=content)
    
    if image_type is None:
        logger.warning(f"File {file.filename} is not a valid image")
        return False
    
    return True

async def validate_video(file: UploadFile) -> bool:
    """
    Validate that the file is a video.
    
    Args:
        file (UploadFile): The file to validate
        
    Returns:
        bool: True if file is a valid video, False otherwise
    """
    # Check extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in VALID_VIDEO_EXTENSIONS:
        logger.warning(f"Invalid video extension: {ext}")
        return False
    
    # For videos, we primarily rely on file extension
    # A more comprehensive check would involve analyzing file headers
    # or trying to open it with a video library
    
    return True

async def validate_files(files: List[UploadFile], file_type: str = 'image') -> bool:
    """
    Validate a list of files.
    
    Args:
        files (List[UploadFile]): The files to validate
        file_type (str): The expected file type ('image' or 'video')
        
    Returns:
        bool: True if all files are valid, False otherwise
    """
    for file in files:
        if file_type == 'image':
            if not await validate_image(file):
                return False
        elif file_type == 'video':
            if not await validate_video(file):
                return False
    
    return True

class FileValidator:
    """
    File validation service class to validate file uploads.
    Implements the interface expected by the test suite.
    """
    
    def __init__(self):
        """Initialize the file validator with allowed extensions."""
        # Define allowed extensions as both list (for order in error messages) and set (for fast lookups)
        self._allowed_image_extensions_list = [".jpg", ".jpeg", ".png"]
        self._allowed_video_extensions_list = [".mp4", ".avi", ".mov"]
        
        # For compatibility with tests that expect sets
        self.ALLOWED_IMAGE_EXTENSIONS = set(self._allowed_image_extensions_list)
        self.ALLOWED_VIDEO_EXTENSIONS = set(self._allowed_video_extensions_list)
    
    def is_valid_image_extension(self, filename: str) -> bool:
        """
        Check if the filename has a valid image extension.
        
        Args:
            filename (str): The filename to validate
            
        Returns:
            bool: True if extension is valid, False otherwise
        """
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.ALLOWED_IMAGE_EXTENSIONS
    
    def is_valid_video_extension(self, filename: str) -> bool:
        """
        Check if the filename has a valid video extension.
        
        Args:
            filename (str): The filename to validate
            
        Returns:
            bool: True if extension is valid, False otherwise
        """
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.ALLOWED_VIDEO_EXTENSIONS
    
    def validate_image_content(self, file_content: BinaryIO) -> Tuple[bool, Optional[str]]:
        """
        Validate the content of an image file.
        
        Args:
            file_content (BinaryIO): The file content to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Save current position
            current_pos = file_content.tell()
            
            # Go to beginning of file
            file_content.seek(0)
            
            # Read the content
            content = file_content.read()
            
            # Restore position
            file_content.seek(current_pos)
            
            # Check if content is an image
            if not content or imghdr.what(None, h=content) is None:
                return False, "Invalid image content"
                
            return True, None
        except Exception as e:
            logger.error(f"Error validating image content: {str(e)}")
            return False, f"Error validating image: {str(e)}"
    
    async def validate_image(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate an image file (extension and content).
        
        Args:
            file (UploadFile): The file to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Check extension
        if not self.is_valid_image_extension(file.filename):
            allowed_ext = ", ".join(self._allowed_image_extensions_list)
            return False, f"Invalid file extension. Allowed extensions: {allowed_ext}"
        
        # Read content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Create a file-like object from the content
        import io
        file_io = io.BytesIO(content)
        
        # Validate content
        valid, error = self.validate_image_content(file_io)
        if not valid:
            return False, error
        
        return True, None
    
    async def validate_video(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate a video file (extension only).
        
        Args:
            file (UploadFile): The file to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Check extension
        if not self.is_valid_video_extension(file.filename):
            allowed_ext = ", ".join(self._allowed_video_extensions_list)
            return False, f"Invalid file extension. Allowed extensions: {allowed_ext}"
        
        # For videos, we primarily rely on file extension
        # A more comprehensive check would involve analyzing file headers
        # or trying to open it with a video library
        
        return True, None
    
    async def validate_files(self, files: List[UploadFile], file_type: str = 'image') -> Tuple[bool, Optional[str]]:
        """
        Validate a list of files.
        
        Args:
            files (List[UploadFile]): The files to validate
            file_type (str): The expected file type ('image' or 'video')
            
        Returns:
            Tuple[bool, Optional[str]]: (all_valid, error_message)
        """
        for file in files:
            if file_type == 'image':
                valid, error = await self.validate_image(file)
                if not valid:
                    return False, f"Invalid file {file.filename}: {error}"
            elif file_type == 'video':
                valid, error = await self.validate_video(file)
                if not valid:
                    return False, f"Invalid file {file.filename}: {error}"
            else:
                return False, f"Unsupported file type: {file_type}"
        
        return True, None
