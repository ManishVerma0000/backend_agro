import httpx
import re
from typing import Optional, Dict, Any
from urllib.parse import unquote

async def resolve_google_maps_url(url: str) -> Dict[str, Any]:
    """
    Follows redirects and extracts coordinates and place info from a Google Maps URL.
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            response = await client.head(url)
            final_url = str(response.url)
        except Exception as e:
            return {"error": f"Failed to resolve URL: {str(e)}"}

    result = {
        "final_url": final_url,
        "lat": None,
        "lng": None,
        "place_name": None
    }

    # 1. Extract Lat/Lng from @lat,long format
    # Example: .../@28.5548624,77.3449955,21z/...
    coord_match = re.search(r'@([-+]?\d+\.\d+),([-+]?\d+\.\d+)', final_url)
    if coord_match:
        result["lat"] = float(coord_match.group(1))
        result["lng"] = float(coord_match.group(2))

    # 2. Extract Lat/Lng from !3d!4d if not found above
    # Example: ...!3d28.5548652!4d77.3451542...
    if not result["lat"]:
        lat_match = re.search(r'!3d([-+]?\d+\.\d+)', final_url)
        lng_match = re.search(r'!4d([-+]?\d+\.\d+)', final_url)
        if lat_match and lng_match:
            result["lat"] = float(lat_match.group(1))
            result["lng"] = float(lng_match.group(2))

    # 3. Extract Place Name
    # Example: https://www.google.com/maps/place/Ultra+Speech+%26+Hearing+care+Pvt+Ltd/...
    place_match = re.search(r'/place/([^/]+)', final_url)
    if place_match:
        result["place_name"] = unquote(place_match.group(1).replace('+', ' '))

    return result
