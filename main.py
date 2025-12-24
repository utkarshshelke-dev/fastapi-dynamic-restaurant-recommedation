from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager
from app.restaurant_service import get_restaurant_recommendations
from app.geo_utils import distance_meters
import json
import time

app = FastAPI()


@app.websocket("/ws/location")
async def location_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send(websocket, {"status": "connected"})

    last_location = None
    last_time = None

    try:
        while True:
            message = await websocket.receive()

            text = message.get("text")
            if text is None:
                continue

            text = text.strip()
            if not text:
                continue

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                await manager.send(websocket, {"error": "Invalid JSON"})
                continue

            lat = data.get("latitude")
            lng = data.get("longitude")

            if lat is None or lng is None:
                await manager.send(websocket, {
                    "error": "latitude and longitude required"
                })
                continue

            now = time.time()

            # First location → initial fetch
            if last_location is None:
                radius = 1000
            else:
                moved = distance_meters(
                    last_location["lat"],
                    last_location["lng"],
                    lat,
                    lng
                )

                # Ignore GPS noise
                if moved < 50:
                    continue

                time_diff = max(now - last_time, 1)
                speed = moved / time_diff  # meters/sec

                # Adaptive radius
                if speed < 1.5:        # walking
                    radius = 1000
                elif speed < 8:        # slow vehicle
                    radius = 3000
                else:                  # fast vehicle
                    radius = 5000

            restaurants = await get_restaurant_recommendations(lat, lng, radius)

            await manager.send(websocket, {
                "latitude": lat,
                "longitude": lng,
                "radius_used": radius,
                "count": len(restaurants),
                "recommendations": restaurants
            })

            last_location = {"lat": lat, "lng": lng}
            last_time = now

    except WebSocketDisconnect:
        manager.disconnect(websocket)
