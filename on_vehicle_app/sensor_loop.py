from typing import List
import random


def run_fake_carla_sensors():
    # Create a fake array of 100 bytes where every 4th byte is a number between 0 and 25
    fake_bytes = bytearray(100)
    for i in range(0, 100, 4):
        fake_bytes[i] = random.randint(0, 25)
        
    fake_bytes = bytes(fake_bytes)
