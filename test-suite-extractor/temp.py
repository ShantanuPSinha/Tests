import json

def load_ndjson_as_dict(file_path):
    data_dict = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    json_obj = json.loads(line)
                    key = list(json_obj.keys())[0]
                    data_dict[key] = json_obj[key]
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse line as JSON: {line}")
                except KeyError:
                    print(f"Warning: Key not found in line: {line}")
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"Error: {e}")

    return data_dict


sols = load_ndjson_as_dict ("/home/shantanu/duality/Tests/test-suite-extractor/.temp_sols.ndjson")
keys = list(sols.keys())


no_sol = 0
sol = 0
timed_out = 0

sol_keys = []

for key in keys:
    if sols[key] == "NO_SOL":
        no_sol += 1
    elif sols[key] == "TIMEOUT":
        timed_out += 1
    else:
        sol += 1
        sol_keys.append(key)
        


print (f"Total: {len(keys)}")
print (f"No Solution: {no_sol}")
print (f"Solution: {sol}")
print (f"Timed Out: {timed_out}")

print (f"Percenatge of Solution: {sol/len(keys)*100 : .2f}%")


def load_data(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = []

    for line in enumerate(lines):
        entry = json.loads(line)
        data.append(entry)

    return data


data = load_data ("/home/shantanu/duality/Tests/test-suite-extractor/rfixer_solutions.ndjson")
filtered_data = [d for d in data if d.get('id') in sol_keys]


print (f"Total: {len(filtered_data)}")
