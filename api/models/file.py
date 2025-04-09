from typing import Dict, Any, Optional 
from datetime import datetime
from pydantic import BaseModel, Field 


class FileMetadata(BaseModel):
    "File metadata model"
    file_id: str 
    file_name: str 
    bucket_name: str 
    content_type: str 
    size: int 
    timestamp: datetime 

class FileUpdate(BaseModel):
    """Model for updating file metadata"""
    file_name: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    
    def dict_with_values(self) -> Dict[str, Any]:
        """Return a dict with only non-None values"""
        return {k: v for k, v in self.dict().items() if v is not None}

class FileResponse(BaseModel):
    """Response model for file operations"""
    message: str