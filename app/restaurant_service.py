import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

async def get_restaurant_recommendations(lat: float, lng: float, radius: int):
    query = f"""
    [out:json];
    node
      ["amenity"="restaurant"]
      (around:{radius},{lat},{lng});
    out;
    """

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            OVERPASS_URL,
            data=query,
            headers={"Content-Type": "text/plain"}
        )
        response.raise_for_status()
        data = response.json()

    restaurants = []

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        restaurants.append({
            "name": name,
            "latitude": el.get("lat"),
            "longitude": el.get("lon"),
            "cuisine": tags.get("cuisine"),
        })

    return restaurants[:5]
