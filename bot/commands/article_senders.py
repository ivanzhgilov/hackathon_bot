import json
import os
commands_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
    points = json.load(file)
    print(points.keys())