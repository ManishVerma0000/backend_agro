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
    
    return details

@router.get("/proxy-image")
async def proxy_image(url: str = Query(..., description="External image URL to proxy")):
    """
    Proxies external images (like S3) to prevent browser CORS blocking.
    """
    import httpx
    from fastapi.responses import Response
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch image")
            media_type = resp.headers.get("content-type", "image/jpeg")
            return Response(
                content=resp.content,
                media_type=media_type,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=86400"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

