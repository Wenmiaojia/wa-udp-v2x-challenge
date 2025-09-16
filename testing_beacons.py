import socket,json,time

#create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Example message from one car
#loop to send 5 beacons
for i in range(5):
    msg = {
        "car_id": "car_888",
        "position": [10.0, 5.0],
        "timestamp": time.time()
    }
    sock.sendto(json.dumps(msg).encode(), ("127.0.0.1", 5005))
    print(f"Sent beacon: {msg}")
    time.sleep(1)