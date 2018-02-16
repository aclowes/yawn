import os

import yaml


def load_sample_workflow():
    filename = os.path.join(os.path.dirname(__file__), 'workflow.yaml')
    return yaml.load(open(filename).read())
