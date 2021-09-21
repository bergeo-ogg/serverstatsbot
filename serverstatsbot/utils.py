import json


def load_json(filename):
    try:
        with open(filename, encoding="utf-8") as f:
            return json.loads(f.read())

    except IOError as e:
        print("Error loading", filename, e)
        return []


def write_json(filename, contents):
    with open(filename, "w") as outfile:
        outfile.write(json.dumps(contents, indent=2))
