import math
import socket 
import json
import time
import sys

'''
math   -- need sqrt for distance 
socket -- opens a network connection that listens for UDP packets
json   -- converts JSON strings to Python dicts and vice versa 
time   -- for timing and timestamps
sys    -- for interacting with system-level input/output
'''
 
# Creating one function that takes one input which is the position 
def euclidean_distance_to_origin(position):
    """
    Calculate the Euclidean distance of a point from the origin (0,0).

    Args:
        position (list or tuple): A 2-element list/tuple [x, y].

    Returns:
        float: Distance from origin.

    Raises:
        ValueError: If the input is not valid.
    """

    # Check if the input is valid
    # isinstance() checks if the position is a list or tuple
    # len() checks if the length of the position is 2
    if not (isinstance(position, (list, tuple)) and len(position) == 2):
        raise ValueError("Position must be a list or tuple of two elements")

    x, y = position

    # Check if the elements of the position are numbers (int or float)
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        raise ValueError("Position elements must be numbers")

    # Calculating the distance from the origin (0,0) to the given position (x,y)
    return math.sqrt(x**2 + y**2)


# Creating a function to find the nearest car
def find_nearestneighbor_car(beacons):
    """
    Find the car nearest to the origin (0,0).

    Args:
        beacons (dict): Dictionary mapping car_id -> {"pos": [x, y], ...}

    Returns:
        tuple: (nearest_car_id, nearest_distance)
               or (None, None) if no valid positions.
    """
    nearest_car_id = None            # Initialize with None
    nearest_distance = float('inf')  # Start with infinity

    # Iterate through each car in the beacons dictionary
    for car_id, data in beacons.items():
        pos = data.get('position')  # Get the position of the car
        try:
            # Calculate the distance to the origin
            distance = euclidean_distance_to_origin(pos)
        except Exception:
            continue  # Skip if position invalid

        # Keep track of the nearest car so far
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_car_id = car_id

    # If no valid beacons found
    if nearest_car_id is None:
        return None, None

    return nearest_car_id, nearest_distance


# Creating a function to listen for UDP packets and collect beacons
def main(listen_ip="127.0.0.1", listen_port=5005, collect_seconds=20.0):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    # Bind the socket to the specified IP and port   
    sock.bind((listen_ip, listen_port)) 
    # Set a timeout for the socket operations
    sock.settimeout(1.0) 
   
    beacons = {}  # Dictionary to hold all received beacons
    start_time = time.time()  # Record the start time

    # Continue until the specified collection time has passed
    while time.time() - start_time < collect_seconds:
        try:
            raw, addr = sock.recvfrom(4096)  # Receive data from the socket
        except socket.timeout:
            # If no data is received before timeout, loop again
            continue
      
        # JSON parsing + validation
        try:
            # Decode the received bytes to a string and parse it as JSON
            msg = json.loads(raw.decode('utf-8'))  
        except json.JSONDecodeError:
            # If the JSON is invalid, skip this iteration
            continue
        
        # Check if the parsed message is a dictionary
        if not isinstance(msg, dict):
            print("Warning: Received message is not a dictionary", raw, file=sys.stderr)
            continue
      
        # Extract required fields
        car_id = msg.get('car_id')          # Car ID
        position = msg.get('position')      # Car position [x, y]
        timestamp = msg.get('timestamp', time.time())  # Timestamp or current time
      
        # Validate car_id
        if not isinstance(car_id, str):
            print("Warning: Invalid or missing car_id", raw, file=sys.stderr)
            continue
      
        # Validate position
        if not (isinstance(position, (list, tuple)) and len(position) == 2):
            print("Warning: Invalid or missing position", raw, file=sys.stderr)
            continue
        
        # Ensure position elements are numbers
        try:
            x = float(position[0])
            y = float(position[1])
        except (TypeError, ValueError):
            print("Warning: Position elements must be numbers", raw, file=sys.stderr)
            continue
      
        # Store the beacon data in the beacons dictionary
        beacons[car_id] = {"position": [x, y], "timestamp": timestamp} 

    # --- After collection: compute nearest and build summary ---
    if beacons:
        nearest_car_id, nearest_distance = find_nearestneighbor_car(beacons)

        if nearest_car_id is None:
            # No valid nearest car could be determined
            summary = {
                "topic": "v2x/neighborcar_summary",
                "count": 0,
                "nearest_car_id": None,
                "timestamp": int(time.time() * 1000)  # Current time in ms
            }
        else:
            # At least one valid car detected → include nearest
            summary = {
                "topic": "v2x/neighborcar_summary",
                "count": len(beacons),  # Total number of valid beacons
                "nearest_car_id": {
                    "id": nearest_car_id,
                    "distance": round(nearest_distance, 2)  # Round distance for readability
                },
                "timestamp": int(time.time() * 1000)  # Current time in ms
            }
    else:
        # If no beacons were collected at all
        summary = {
            "topic": "v2x/neighborcar_summary",
            "count": 0,
            "nearest_car_id": None,
            "timestamp": int(time.time() * 1000)  # Current time in ms
        }

    # Print the JSON summary (final output of the program)
    print(json.dumps(summary))


# This section ensures the script runs only when executed directly,
# not when imported as a module in another program.
if __name__ == "__main__":
    # Call main() with default arguments (listening on 127.0.0.1:5005 for 1 second)
    main()
