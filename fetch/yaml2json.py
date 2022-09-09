#!/usr/bin/env python
import json
from fetch.utils import get_model
import string
import glob
import logging

logger = logging.getLogger()
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=format)
logging.getLogger('pika').setLevel(logging.INFO)


model_idxs = list(string.ascii_lowercase)[0:11]

path = '/home/franz/git/astroflash-fetch/fetch/'
for model_idx in model_idxs:
    model_yaml = glob.glob(f'{path}/models/{model_idx}_FT*//*yaml')[0]
    model_json = model_yaml.replace('.yaml', '.json')
    logging.info(f'loading {model_yaml} and writing to {model_json}')
    model = get_model(model_idx)
    model = model.to_json()
    with open(model_json, 'w') as f:
        json.dump(model, f)
