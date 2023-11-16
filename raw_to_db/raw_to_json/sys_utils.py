import json
import typing as t


def save_model(model, name="data.jsonl"):
    full_dict = [x.dict() for x in model]
    with open(name, "w") as f:
        for item in full_dict:
            f.write(json.dumps(item) + "\n")


def load_model(model, name="data.jsonl"):
    data = []
    with open(name, "r") as f:
        for line in f:
            data.append(json.loads(line))

    list_model = []

    for x in data:
        list_model.append(model(**x))

    return list_model
