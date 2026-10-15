import time
import random

def start_simulation(process):

    print("SIMULATION STARTED\n")

    # NORMAL TRAFFIC
    print("NORMAL TRAFFIC...\n")

    for _ in range(15):
        process({
            "flags": "A",
            "port": random.choice([80, 443, 22]),
            "burst": 0
        })
        time.sleep(0.2)

    print("NORMAL DONE\n")

    time.sleep(2)

    # ATTACK TRAFFIC
    print("ATTACK TRAFFIC...\n")

    for _ in range(30):
        process({
            "flags": "S",
            "port": 80,
            "burst": 1
        })
        time.sleep(0.1)

    print("ATTACK DONE\n")
    print("SIMULATION COMPLETE\n")