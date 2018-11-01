import os
import signal
import sys
from pprint import pformat
from random import random
from importlib import import_module
import numpy as np

### !!!
os.path.expanduser = lambda p : p.replace('~', '/home/regele') # theta only, cray os error...
### !!!
import tensorflow as tf

import time

from deephyper.search import util
from deephyper.run.nas_cmdline import create_parser

from nas.model.trainer import BasicTrainer

logger = util.conf_logger('deephyper.search.nas')

def run(param_dict):
    logger.debug('Starting...')
    config = param_dict

    # load functions
    if config.get('preprocessing') is not None:
        preprocessing = util.load_attr_from(config['preprocessing']['func'])
        config['preprocessing']['func'] = preprocessing
    else:
        config['preprocessing'] = None
    load_data = util.load_attr_from(config['load_data']['func'])
    config['load_data']['func'] = load_data
    config['create_structure']['func'] = util.load_attr_from(
        config['create_structure']['func'])

    logger.debug('[PARAM] Loading data')
    # Loading data
    kwargs = config['load_data'].get('kwargs')
    (t_X, t_y), (v_X, v_y) = load_data() if kwargs is None else load_data(**kwargs)
    logger.debug('[PARAM] Data loaded')

    # Set data shape
    config['input_shape'] = list(np.shape(t_X))[1:]
    config['output_shape'] = list(np.shape(t_y))[1:]

    config['data'] = {
        'train_X': t_X,
        'train_Y': t_y,
        'valid_X': v_X,
        'valid_Y': v_y
    }


    # For all the Net generated by the CONTROLLER
    trainer = BasicTrainer(config)

    # Run the trainer and get the rewards
    architecture = config['arch_seq']
    result = trainer.get_rewards(architecture)

    logger.debug(f'[REWARD/RESULT] = {result}')
    return result

if __name__ == '__main__':
    parser = create_parser()
    cmdline_args = parser.parse_args()
    param_dict = cmdline_args.config
    run(param_dict)