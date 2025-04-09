from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from core.db import get_db 
from models.file import FileUpdate, FileResponse
from app.config import COLLECTION_NAME

router = APIRouter(tags=["files"])

def get_db():
    """Dependency to get database client"""
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable"
        )
    return db

@router.get("/files")
async def list_files(db=Depends(get_db)):
    """List all files in the database"""
    try:
        docs = db.collection(COLLECTION_NAME).stream()
        files = [doc.to_dict() for doc in docs]
        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/files/{file_id}")
async def get_file(file_id: str, db=Depends(get_db)):
    """Get a specific file by ID"""
    try:
        doc = db.collection(COLLECTION_NAME).document(file_id).get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return doc.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/files/{file_id}")
async def update_file(file_id: str, data: FileUpdate, db=Depends(get_db)):
    """Update a file's metadata"""
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(file_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        update_data = data.dict_with_values()
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        doc_ref.update(update_data)

        updated_doc = doc_ref.get()
        
        return updated_doc.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/files/{file_id}", response_model=FileResponse)
async def delete_file(file_id: str, db=Depends(get_db)):
    """Delete a file's metadata"""
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(file_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        doc_ref.delete()
        
        return {"message": f"File {file_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )