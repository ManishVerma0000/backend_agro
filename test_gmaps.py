import asyncio
from app.utils.gmaps import resolve_google_maps_url

async def test():
    url = 'https://maps.app.goo.gl/6D1eDTrJh2BuSF4u8'
    res = await resolve_google_maps_url(url)
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
