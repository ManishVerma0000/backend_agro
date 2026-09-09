from fastapi import APIRouter, Query, HTTPException
from app.utils.gmaps import resolve_google_maps_url

router = APIRouter()

@router.get("/resolve-maps-url")
async def get_maps_details(url: str = Query(..., description="The shortened Google Maps URL")):
    """
    Takes a shortened Google Maps URL, resolves it, and returns coordinates and place name.
    """
    if not ("google.com/maps" in url or "maps.app.goo.gl" in url or "goo.gl/maps" in url):
        raise HTTPException(status_code=400, detail="Invalid Google Maps URL")
        
    details = await resolve_google_maps_url(url)
    
    if "error" in details:
        raise HTTPException(status_code=400, detail=details["error"])
        
    return details
