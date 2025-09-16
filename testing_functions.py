import socket
import json
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# List of example cars
cars = [
    {"car_id": "car_101", "position": [2, 1]},
    {"car_id": "car_202", "position": [6, 8]},
    {"car_id": "car_303", "position": [12, 3]},
    {"car_id": "car_888", "position": [10.0, 5.0]}
]

# Loop to send each car's beacon 5 times
for i in range(5):
    for car in cars:
        msg = {**car, "timestamp": time.time()}
        sock.sendto(json.dumps(msg).encode(), ("127.0.0.1", 5005))
        print(f"Sent beacon: {msg}")
        time.sleep(1)
