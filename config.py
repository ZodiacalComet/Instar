import json

with open("./token.json", "r") as f:
    json_data = json.load(f)

instar_token = json_data["token"]