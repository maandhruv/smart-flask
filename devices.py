import random
import time
import json
import os

def generate_mock_data(device_id):
    return {
        "device_id": device_id,
        "timestamp": time.time(),
        "energy_consumption": round(random.uniform(0.5, 3.5), 2)  # kWh
    }


def main():
    device_ids = [1, 2, 3, 4, 5]
    while True:
        for device_id in device_ids:
            data = generate_mock_data(device_id)
            with open(f"/Users/dhruvmaan/Desktop/flaskproject/devices/data_{device_id}.json", "r") as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                        existing_data=[]
            
            existing_data.append(data)      
            with open(f"/Users/dhruvmaan/Desktop/flaskproject/devices/data_{device_id}.json", "w") as f:
                json.dump(existing_data, f, indent=4)   
        time.sleep(10)  
        print("1")
if __name__ == "__main__":
    main()
