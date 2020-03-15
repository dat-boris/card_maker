import logging
import yaml
from typing import List, Dict


def parse_content_from_array(data_list: List[Dict]) -> List[Dict[str, any]]:
    all_data: List[Dict[str, any]] = []
    for d in data_list:
        logging.info("Getting data: {}".format(d))
        # Template_file is not used in the data
        d.pop('template_file')

        try:
            count = int(d.pop('count'))
        except KeyError:
            # no key, assume 1
            count = 1
        except ValueError:
            # It has count, but no value provided
            count = 0
        all_data.extend([d] * count)

    return all_data


def read_yaml(file):
    yaml_data = filter(lambda x: x, yaml.load_all(open(file, 'r')))
    return parse_content_from_array(yaml_data)
