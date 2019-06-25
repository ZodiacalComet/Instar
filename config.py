import json

# Getting the token from json file
with open("./token.json", "r") as f:
    json_data = json.load(f)

instar_token = json_data["token"]

# Uno Config
category_name = "UNO | Game"

seat_amount = 6
channel_names = [f"uno-seat-{numb}" for numb in range(1, seat_amount + 1)]
role_names = [f"{numb} | UNO Seat Access" for numb in range(1, seat_amount + 1)]

# Utility Functions

def inverse_lst(lst):
    out = []

    for i in range(1, len(lst) + 1):
        out.append(lst[-i])

    return out
