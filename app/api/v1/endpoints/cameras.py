from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from app.db.database import get_database
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse, ConveyorCreate, ConveyorUpdate, ConveyorResponse

router = APIRouter()

@router.post("/cameras", response_model=CameraResponse)
async def create_camera(
    camera: CameraCreate = Body(...),
    db = Depends(get_database)
):
    """
    Create a new camera in the system.
    """
    # Generate camera ID
    camera_id = str(uuid4())
    
    # Create camera document
    camera_doc = {
        "camera_id": camera_id,
        "name": camera.name,
        "location": camera.location,
        "conveyor_id": camera.conveyor_id,
        "ip_address": camera.ip_address,
        "rtsp_url": camera.rtsp_url,
        "active": camera.active,
        "config": camera.config.dict() if camera.config else {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # Insert to database
    await db.cameras.insert_one(camera_doc)
    
    return CameraResponse(**camera_doc)

@router.get("/cameras", response_model=List[CameraResponse])
async def list_cameras(
    conveyor_id: Optional[str] = Query(None, description="Filter by conveyor ID"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db = Depends(get_database)
):
    """
    List all cameras in the system.
    """
    # Build query
    query = {}
    
    if conveyor_id:
        query["conveyor_id"] = conveyor_id
    
    if active is not None:
        query["active"] = active
    
    # Retrieve cameras
    cameras = await db.cameras.find(query).to_list(length=None)
    
    return cameras

@router.get("/cameras/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: str = Path(..., description="The ID of the camera to retrieve"),
    db = Depends(get_database)
):
    """
    Get details for a specific camera.
    """
    camera = await db.cameras.find_one({"camera_id": camera_id})
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID {camera_id} not found")
    
    return camera

@router.put("/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: str = Path(..., description="The ID of the camera to update"),
    camera_update: CameraUpdate = Body(...),
    db = Depends(get_database)
):
    """
    Update an existing camera.
    """
    # Check if camera exists
    camera = await db.cameras.find_one({"camera_id": camera_id})
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID {camera_id} not found")
    
    # Update fields
    update_data = camera_update.dict(exclude_unset=True)
    
    if update_data:
        update_data["updated_at"] = datetime.now()
        
        # Update in database
        await db.cameras.update_one(
            {"camera_id": camera_id},
            {"$set": update_data}
        )
    
    # Get updated camera
    updated_camera = await db.cameras.find_one({"camera_id": camera_id})
    
    return updated_camera

@router.delete("/cameras/{camera_id}", response_model=dict)
async def delete_camera(
    camera_id: str = Path(..., description="The ID of the camera to delete"),
    db = Depends(get_database)
):
    """
    Delete a camera from the system.
    """
    # Check if camera exists
    camera = await db.cameras.find_one({"camera_id": camera_id})
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID {camera_id} not found")
    
    # Delete camera
    await db.cameras.delete_one({"camera_id": camera_id})
    
    return {"message": f"Camera with ID {camera_id} deleted successfully"}

@router.post("/conveyors", response_model=ConveyorResponse)
async def create_conveyor(
    conveyor: ConveyorCreate = Body(...),
    db = Depends(get_database)
):
    """
    Create a new conveyor belt in the system.
    """
    # Generate conveyor ID
    conveyor_id = str(uuid4())
    
    # Create conveyor document
    conveyor_doc = {
        "conveyor_id": conveyor_id,
        "name": conveyor.name,
        "location": conveyor.location,
        "active": conveyor.active,
        "config": conveyor.config.dict() if conveyor.config else {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # Insert to database
    await db.conveyors.insert_one(conveyor_doc)
    
    return ConveyorResponse(**conveyor_doc)

@router.get("/conveyors", response_model=List[ConveyorResponse])
async def list_conveyors(
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db = Depends(get_database)
):
    """
    List all conveyor belts in the system.
    """
    # Build query
    query = {}
    
    if active is not None:
        query["active"] = active
    
    # Retrieve conveyors
    conveyors = await db.conveyors.find(query).to_list(length=None)
    
    return conveyors

@router.get("/conveyors/{conveyor_id}", response_model=ConveyorResponse)
async def get_conveyor(
    conveyor_id: str = Path(..., description="The ID of the conveyor to retrieve"),
    db = Depends(get_database)
):
    """
    Get details for a specific conveyor belt.
    """
    conveyor = await db.conveyors.find_one({"conveyor_id": conveyor_id})
    
    if not conveyor:
        raise HTTPException(status_code=404, detail=f"Conveyor with ID {conveyor_id} not found")
    
    return conveyor

@router.put("/conveyors/{conveyor_id}", response_model=ConveyorResponse)
async def update_conveyor(
    conveyor_id: str = Path(..., description="The ID of the conveyor to update"),
    conveyor_update: ConveyorUpdate = Body(...),
    db = Depends(get_database)
):
    """
    Update an existing conveyor belt.
    """
    # Check if conveyor exists
    conveyor = await db.conveyors.find_one({"conveyor_id": conveyor_id})
    
    if not conveyor:
        raise HTTPException(status_code=404, detail=f"Conveyor with ID {conveyor_id} not found")
    
    # Update fields
    update_data = conveyor_update.dict(exclude_unset=True)
    
    if update_data:
        update_data["updated_at"] = datetime.now()
        
        # Update in database
        await db.conveyors.update_one(
            {"conveyor_id": conveyor_id},
            {"$set": update_data}
        )
    
    # Get updated conveyor
    updated_conveyor = await db.conveyors.find_one({"conveyor_id": conveyor_id})
    
    return updated_conveyor

@router.delete("/conveyors/{conveyor_id}", response_model=dict)
async def delete_conveyor(
    conveyor_id: str = Path(..., description="The ID of the conveyor to delete"),
    db = Depends(get_database)
):
    """
    Delete a conveyor belt from the system.
    """
    # Check if conveyor exists
    conveyor = await db.conveyors.find_one({"conveyor_id": conveyor_id})
    
    if not conveyor:
        raise HTTPException(status_code=404, detail=f"Conveyor with ID {conveyor_id} not found")
    
    # Check if conveyor has cameras
    cameras_count = await db.cameras.count_documents({"conveyor_id": conveyor_id})
    
    if cameras_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete conveyor with ID {conveyor_id} because it has {cameras_count} associated cameras"
        )
    
    # Delete conveyor
    await db.conveyors.delete_one({"conveyor_id": conveyor_id})
    
    return {"message": f"Conveyor with ID {conveyor_id} deleted successfully"}
