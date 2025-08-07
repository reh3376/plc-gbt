#!/usr/bin/env python3
"""
Simple File API Server for PLC-GBT File Explorer
Provides basic file operations for testing File Explorer functionality
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="PLC-GBT File API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock file system root (for testing)
MOCK_FILES_ROOT = Path("./mock_files")
MOCK_FILES_ROOT.mkdir(exist_ok=True)

# Response models
class FileItem(BaseModel):
    id: str
    name: str
    type: str  # 'file' or 'folder'
    path: str
    size: Optional[int] = None
    lastModified: Optional[datetime] = None
    isExpanded: Optional[bool] = False
    children: Optional[List['FileItem']] = None
    parentId: Optional[str] = None
    extension: Optional[str] = None
    mimeType: Optional[str] = None

class FileOperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[FileItem] = None
    error: Optional[str] = None

class FileListResponse(BaseModel):
    success: bool
    data: List[FileItem]
    message: str
    totalCount: int

# Request models  
class CreateFileRequest(BaseModel):
    name: str
    type: str
    parentPath: str
    content: Optional[str] = ""

# Mock data initialization
def init_mock_data():
    """Initialize mock file system with sample files"""
    plc_project_dir = MOCK_FILES_ROOT / "PLC Project"
    plc_project_dir.mkdir(exist_ok=True)
    
    # Create sample files
    (plc_project_dir / "main.acd").write_text("# Main ACD file content")
    (plc_project_dir / "export.l5x").write_text("<?xml version='1.0'?><RSLogix5000Content></RSLogix5000Content>")
    
    return plc_project_dir

def path_to_file_item(file_path: Path, parent_id: Optional[str] = None) -> FileItem:
    """Convert a file path to FileItem model"""
    stat = file_path.stat()
    is_file = file_path.is_file()
    
    file_item = FileItem(
        id=str(hash(str(file_path))),
        name=file_path.name,
        type="file" if is_file else "folder",
        path=str(file_path.relative_to(MOCK_FILES_ROOT)),
        size=stat.st_size if is_file else None,
        lastModified=datetime.fromtimestamp(stat.st_mtime),
        parentId=parent_id,
        extension=file_path.suffix if is_file else None,
        mimeType=get_mime_type(file_path) if is_file else None,
        isExpanded=False
    )
    
    # Add children for directories
    if file_path.is_dir():
        children = []
        for child_path in sorted(file_path.iterdir()):
            child_item = path_to_file_item(child_path, file_item.id)
            children.append(child_item)
        file_item.children = children
    
    return file_item

def get_mime_type(file_path: Path) -> str:
    """Get MIME type based on file extension"""
    extension = file_path.suffix.lower()
    mime_types = {
        '.acd': 'application/x-acd',
        '.l5x': 'application/xml',
        '.json': 'application/json',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.py': 'text/x-python',
        '.js': 'text/javascript',
        '.html': 'text/html',
        '.css': 'text/css'
    }
    return mime_types.get(extension, 'application/octet-stream')

# Initialize mock data on startup
init_mock_data()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "File API is running"}

@app.get("/api/v1/files", response_model=FileListResponse)
async def get_files():
    """Get file tree structure"""
    try:
        files = []
        for item in sorted(MOCK_FILES_ROOT.iterdir()):
            if item.name.startswith('.'):
                continue
            file_item = path_to_file_item(item)
            files.append(file_item)
        
        return FileListResponse(
            success=True,
            data=files,
            message=f"Loaded {len(files)} files",
            totalCount=len(files)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/files", response_model=FileOperationResponse)
async def create_file(request: CreateFileRequest):
    """Create a new file or folder"""
    try:
        # Sanitize parent path
        parent_path = MOCK_FILES_ROOT / request.parentPath.lstrip('/')
        parent_path.mkdir(parents=True, exist_ok=True)
        
        # Create new file/folder path
        new_path = parent_path / request.name
        
        if new_path.exists():
            return FileOperationResponse(
                success=False,
                message=f"{request.type.capitalize()} '{request.name}' already exists",
                error="File already exists"
            )
        
        if request.type == "folder":
            new_path.mkdir()
        else:
            new_path.write_text(request.content or "")
        
        # Convert to FileItem
        file_item = path_to_file_item(new_path)
        
        return FileOperationResponse(
            success=True,
            message=f"{request.type.capitalize()} '{request.name}' created successfully",
            data=file_item
        )
        
    except Exception as e:
        return FileOperationResponse(
            success=False,
            message=f"Failed to create {request.type}",
            error=str(e)
        )

@app.post("/api/v1/files/upload", response_model=FileOperationResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    targetPath: str = Form("/"),
    overwrite: bool = Form(False)
):
    """Upload files to target directory"""
    try:
        target_dir = MOCK_FILES_ROOT / targetPath.lstrip('/')
        target_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_files = []
        
        for file in files:
            file_path = target_dir / file.filename
            
            if file_path.exists() and not overwrite:
                continue
                
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_item = path_to_file_item(file_path)
            uploaded_files.append(file_item)
        
        return FileOperationResponse(
            success=True,
            message=f"Uploaded {len(uploaded_files)} files",
            data=uploaded_files[0] if uploaded_files else None
        )
        
    except Exception as e:
        return FileOperationResponse(
            success=False,
            message="Upload failed",
            error=str(e)
        )

@app.delete("/api/v1/files/{file_id}")
async def delete_file(file_id: str, recursive: bool = False):
    """Delete a file or folder"""
    try:
        # Find file by ID (simplified - in real app would have proper ID mapping)
        for item in MOCK_FILES_ROOT.rglob("*"):
            if str(hash(str(item))) == file_id:
                if item.is_dir():
                    if recursive:
                        shutil.rmtree(item)
                    else:
                        item.rmdir()
                else:
                    item.unlink()
                
                return FileOperationResponse(
                    success=True,
                    message=f"Deleted {item.name} successfully"
                )
        
        return FileOperationResponse(
            success=False,
            message="File not found",
            error="File not found"
        )
        
    except Exception as e:
        return FileOperationResponse(
            success=False,
            message="Delete failed",
            error=str(e)
        )

@app.put("/api/v1/files/{file_id}/rename")
async def rename_file(file_id: str, newName: str):
    """Rename a file or folder"""
    try:
        # Find and rename file (simplified implementation)
        for item in MOCK_FILES_ROOT.rglob("*"):
            if str(hash(str(item))) == file_id:
                new_path = item.parent / newName
                item.rename(new_path)
                
                file_item = path_to_file_item(new_path)
                return FileOperationResponse(
                    success=True,
                    message=f"Renamed to '{newName}' successfully",
                    data=file_item
                )
        
        return FileOperationResponse(
            success=False,
            message="File not found",
            error="File not found"
        )
        
    except Exception as e:
        return FileOperationResponse(
            success=False,
            message="Rename failed",
            error=str(e)
        )

@app.put("/api/v1/files/{file_id}/move")
async def move_file(file_id: str, targetParentId: str):
    """Move a file or folder to a different parent directory"""
    try:
        source_item = None
        target_parent = None
        
        # Find source file/folder by ID
        for item in MOCK_FILES_ROOT.rglob("*"):
            if str(hash(str(item))) == file_id:
                source_item = item
                break
        
        if not source_item:
            return FileOperationResponse(
                success=False,
                message="Source file not found",
                error="Source file not found"
            )
        
        # Find target parent folder by ID
        for item in MOCK_FILES_ROOT.rglob("*"):
            if str(hash(str(item))) == targetParentId and item.is_dir():
                target_parent = item
                break
        
        if not target_parent:
            return FileOperationResponse(
                success=False,
                message="Target folder not found",
                error="Target folder not found"
            )
        
        # Move the file/folder
        new_path = target_parent / source_item.name
        
        if new_path.exists():
            return FileOperationResponse(
                success=False,
                message=f"'{source_item.name}' already exists in target location",
                error="File already exists"
            )
        
        source_item.rename(new_path)
        
        file_item = path_to_file_item(new_path)
        return FileOperationResponse(
            success=True,
            message=f"Moved '{source_item.name}' successfully",
            data=file_item
        )
        
    except Exception as e:
        return FileOperationResponse(
            success=False,
            message="Move failed",
            error=str(e)
        )

# =============================================================================
# CONTROL LOOP INSTANCES API - Basic Mock Implementation
# =============================================================================

# Mock control loop data
MOCK_CONTROL_LOOPS = [
    {
        "id": "loop-001",
        "name": "Temperature Control Loop 1", 
        "type": "PID",
        "status": "active",
        "setpoint": 75.0,
        "processValue": 74.8,
        "output": 45.2,
        "lastUpdated": datetime.now().isoformat()
    },
    {
        "id": "loop-002", 
        "name": "Pressure Control Loop 1",
        "type": "PID",
        "status": "active", 
        "setpoint": 15.0,
        "processValue": 14.9,
        "output": 52.1,
        "lastUpdated": datetime.now().isoformat()
    }
]

@app.get("/api/v1/instances")
async def get_control_loop_instances():
    """Get control loop instances - mock implementation"""
    return {
        "success": True,
        "message": "Control loop instances retrieved",
        "data": MOCK_CONTROL_LOOPS,
        "total": len(MOCK_CONTROL_LOOPS)
    }

@app.post("/api/v1/instances")
async def create_control_loop_instance(data: dict):
    """Create control loop instance - mock implementation"""
    new_loop = {
        "id": f"loop-{len(MOCK_CONTROL_LOOPS) + 1:03d}",
        "name": data.get("name", "New Control Loop"),
        "type": data.get("type", "PID"),
        "status": "active",
        "setpoint": data.get("setpoint", 0.0),
        "processValue": data.get("setpoint", 0.0),
        "output": 0.0,
        "lastUpdated": datetime.now().isoformat()
    }
    MOCK_CONTROL_LOOPS.append(new_loop)
    
    return {
        "success": True,
        "message": "Control loop instance created",
        "data": new_loop
    }

@app.get("/api/v1/instances/{instance_id}")
async def get_control_loop_instance(instance_id: str):
    """Get specific control loop instance"""
    loop = next((loop for loop in MOCK_CONTROL_LOOPS if loop["id"] == instance_id), None)
    if not loop:
        raise HTTPException(status_code=404, detail="Control loop instance not found")
    
    return {
        "success": True,
        "message": "Control loop instance retrieved", 
        "data": loop
    }

# =============================================================================
# WEBSOCKET ENDPOINT - Basic Implementation  
# =============================================================================

# Store active WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Basic WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "message": "WebSocket connected successfully",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_json()
                
                # Echo back for now (basic implementation)
                await websocket.send_json({
                    "type": "echo",
                    "received": data,
                    "timestamp": datetime.now().isoformat()
                })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error", 
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_file_api:app", host="0.0.0.0", port=8000, reload=True) 