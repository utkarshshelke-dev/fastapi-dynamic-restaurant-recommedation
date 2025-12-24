uvicorn main:app --reload

ws://127.0.0.1:8000/ws/restaurants

const we = new WebSocket("ws://localhost:8000/ws/restaurants);

ws.onopen = () => { ws.send(JSON.stringify({ lat:40.7128, lng:74.0060, radius: 3000 })); };

ws.onmessage = (event) => { console.log("Recieved":, JSON.parse(event.data)); };