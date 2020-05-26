import logging
import csv
import yaml
from typing import List, Dict


def read_yaml(file) -> List[Dict]:
    yaml_data = list(filter(lambda x: x, yaml.load_all(open(file, "r"))))
    return yaml_data


def read_csv(file, skip_lines=0) -> List[Dict]:
    with open(file, "r") as f:
        for i in range(skip_lines):
            next(f)
        reader = csv.DictReader(f)
        return [r for r in reader]
