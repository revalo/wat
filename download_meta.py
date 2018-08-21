"""Thanks firehose! This file gets the firehose data
and caches the json in memory.
"""

import requests
import json


def download_firehose(filename):
    # Download from the server.
    r = requests.get("https://firehose.guide/full.js")
    text = r.text

    # Find the JSON payload.
    json_str = text[text.index("{") : text.rindex("}") + 1]

    # Try to see if this JSON data is valid.
    classes = json.loads(json_str)

    # Dump it back.
    with open(filename, "w") as f:
        f.write(json.dumps(classes))


def strip_classes(classes_fn, stripped_fn):
    """Takes in a classes JSON file and dumps it
    as a static Javascript file, stripping away
    everything we don't need.
    """

    # Read.
    with open(classes_fn, "r") as f:
        classes = json.loads(f.read())

    # Strip.
    stripped = []
    for key, value in classes.items():
        stripped.append({"code": value["no"], "name": value["n"]})

    # Serialize as a Javascript file.
    js = "var classes = {json};"
    with open(stripped_fn, "w") as f:
        f.write(js.format(json=json.dumps(stripped)))


if __name__ == "__main__":
    download_firehose("store/classes.json")
    strip_classes("store/classes.json", "wat/static/classes.js")
