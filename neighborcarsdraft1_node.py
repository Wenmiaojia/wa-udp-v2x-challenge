import math
import socket 
import json
import time
import sys

'''math -- need sqrt for distance 
socket -- for opens a network connection that listen for UDP  packets
json -- for converts json strings to python dicts and vice versa 
time -- for timing and timestamps
sys -- for interact with system level input/output'''
#Creating one fuction that takes one input which is the position 
def euclidean_distance_to_origin(position):
    """

    Check if the input is valid
    isinstance() checks if the position is a list or tuple
    len() checks if the length of the position is 2

    """
   
    if not (isinstance(position, (list, tuple)) and len(position) == 2):
        raise ValueError("Position must be a list or tuple of two elements")

    
    x, y = position

    #Check if the elements of the position are numbers (int or float)
   
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        raise ValueError("Position elements must be numbers")

    # Calculating the distance from the origin (0,0) to the given position (x,y)
    return math.sqrt(x**2 + y**2)
    


#Creating a function to find the nearest car
def find_nearestneighbor_car(beacons):
    """
    Find the car nearest to the origin (0,0).

    Args:
        beacons (dict): Dictionary mapping car_id -> {"pos": [x, y], ...}

    Returns:
        tuple: (nearest_car_id, nearest_distance)
               or (None, None) if no valid positions.
    """
    nearest_car_id = None      # Initialize with None
    nearest_distance = float('inf')  # Start with infinity

    # Iterate through each car in the beacons dictionary
    for car_id, data in beacons.items():
        pos = data.get('pos')  # Get the position of the car
        try:
            # Calculate the distance to the origin
            distance = euclidean_distance_to_origin(pos)
        except Exception:
            continue  # Skip if position invalid

        if distance < nearest_distance:
            nearest_distance = distance
            nearest_car_id = car_id

    # If no valid beacons found
    if nearest_car_id is None:
        return None, None

    return nearest_car_id, nearest_distance
#Creating a function to listen for UDP packets and collect beacons
def main(listen_ip="127.0.0.1", listen_port=5005, collect_seconds=1.0):
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create a UDP socket
   sock.bind((listen_ip, listen_port)) # Bind the socket to the specified IP and port   
   sock.settimeout(1.0) # Set a timeout for the socket operations
   
   beacons = {}
   start_time = time.time() # Record the start time

   while time.time() - start_time < collect_seconds: # Continue until the specified collection time has passed
      try:
        raw , addr = sock.recvfrom(4096) # Receive data from the socket
      except socket.timeout:# if no data is recieved in 0.1s loop again
            continue
      
       #Json parsing + validation
       try:
        msg = json.loads(raw.decode('utf-8')) # Decode the received bytes to a string and parse it as JSON
       except json.JSONDecodeError:# If the JSON is invalid, skip this iteration
            continue
        
       if not isinstance(msg, dict): # Check if the parsed message is a dictionary
            print("Warning: Received message is not a dictionary", raw, file=sys.stderr) # Print a warning to stderr and skip this iteration
            continue
      
       car_id = msg.get('car_id') # Extract the car ID from the message
       position = msg.get('position') # Extract the position from the message
       timestamp = msg.get('timestamp', time.time()) # Extract the timestamp or use the current time if not provided
      
        if not isinstance(car_id, str): # Validate the car ID
           print("Warning: Invalid or missing car_id", raw, file=sys.stderr) # Print a warning to stderr and skip this iteration
           continue
      
        if not (isinstance(position, (list, tuple)) and len(position) == 2):
            # Validate the position
           print("Warning: Invalid or missing position", raw, file=sys.stderr) # Print a warning to stderr and skip this iteration
           continue
        
        try:
         
         x = float(position[0]) # Convert the position elements to floats
         y = float(position[1])
        except (TypeError, ValueError): # If conversion fails, skip this iteration  
            print("Warning: Position elements must be numbers", raw, file=sys.stderr) 
         # Print a warning to stderr and skip this iteration
            continue
      
        beacons[car_id] = {"pos":[x, y], "timestamp": timestamp} 
      # Store the beacon data in the beacons dictionary
       # --- After collection: compute nearest and build summary ---
   if beacons:
        nearest_car_id, nearest_distance = find_nearestneighbor_car(beacons)

        if nearest_car_id is None:
            summary = {
                "topic": "v2x/neighborcar_summary",
                "count": 0,
                "nearest_car_id": None,
                "timestamp": int(time.time() * 1000)
            }
        else:
            summary = {
                "topic": "v2x/neighborcar_summary",
                "count": len(beacons),
                "nearest_car_id": {
                    "id": nearest_car_id,
                    "distance": round(nearest_distance, 2)
                },
                "timestamp": int(time.time() * 1000)
            }
    else:
        summary = {
            "topic": "v2x/neighborcar_summary",
            "count": 0,
            "nearest_car_id": None,
            "timestamp": int(time.time() * 1000)
        }

    print(json.dumps(summary))


if __name__ == "__main__":
    main()



        
