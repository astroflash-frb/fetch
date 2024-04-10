#!/usr/bin/env python3

import argparse
import logging
import pathlib
from multiprocessing import Pool
import os
import pylab as plt

os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
import numpy as np
import pandas as pd
from pysigproc import SigprocFile
from candidate import *
from gpu_utils import gpu_dedisp_and_dmt_crop
logger = logging.getLogger()


def normalise(data):
    """
    Noramlise the data by unit standard deviation and zero median
    :param data: data
    :return:
    """
    data = np.array(data, dtype=np.float32)
    median = np.median(data)
    std = np.std(data)
    logging.debug(f'Data median: {median}')
    logging.debug(f'Data std: {std}')
    data -= median
    data /= std
    return data


def cand2h5(cand_val):
    """
    TODO: Add option to use cand.resize for reshaping FT and DMT
    Generates h5 file of candidate with resized frequency-time and DM-time arrays
    :param cand_val: List of candidate parameters (fil_name, snr, width, dm, label, tcand(s))
    :type cand_val: Candidate
    :return: None
    """
    fil_name, snr, width, dm, label, tcand, kill_mask_path, args = cand_val
    if kill_mask_path == kill_mask_path:
        kill_mask_file = pathlib.Path(kill_mask_path)
        if kill_mask_file.is_file():
            logging.info(f'Using mask {kill_mask_path}')
            try:
                kill_chans = np.loadtxt(kill_mask_path, dtype=np.int)
            except(ValueError) as e:
                ranges = np.loadtxt(kill_mask_path, dtype=np.str, ndmin=1)
                kill_chans = np.array([], dtype=np.int)
                for r in ranges:
                    b,e = [int(i) for i in r.split('-')]
                    kill_chans = np.concatenate((kill_chans, np.arange(b, e+1)))
            filobj = SigprocFile(fil_name)
            kill_mask = np.zeros(filobj.nchans, dtype=np.bool)
            kill_mask[kill_chans]= True

    else:
        logging.debug('No Kill Mask')
        kill_mask = None

    cand = Candidate(fil_name, snr=snr, width=width, dm=dm, label=label, tcand=tcand, kill_mask=kill_mask)
    cand.get_chunk()
    cand.fp.close()
    logging.info('Got Chunk')
    cand=gpu_dedisp_and_dmt_crop(cand, dm_range_scale=args.dm_range_scale)
    logging.info('Done with DMT')
    cand.dedispersed=resize(cand.dedispersed, (256,256))
    logging.info('resized FT')

    cand.dmt = normalise(cand.dmt)
    cand.dedispersed = normalise(cand.dedispersed)

    fout = cand.save_h5(out_dir=args.fout)
    logging.info(fout)
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-fs', '--frequency_size', type=int, help='Frequency size after rebinning', default=256)
    parser.add_argument('-ts', '--time_size', type=int, help='Time length after rebinning', default=256)
    parser.add_argument('-c', '--cand_param_file', help='csv file with candidate parameters', type=str, required=True)
    parser.add_argument('-n', '--nproc', type=int, help='number of processors to use in parallel (default: 2)',
                        default=2)
    parser.add_argument('-p', '--plot', dest='plot', help='To display and save the candidates plots',
                        action='store_true')
    parser.add_argument('-o', '--fout', help='Output file directory for candidate h5', type=str)
    parser.add_argument('-opt', '--opt_dm', dest='opt_dm', help='Optimise DM', action='store_true', default=False)
    parser.add_argument('-s', '--dm_range_scale', dest='dm_range_scale', type=float, default=1.0,
                        help='Scaling factor to zoom in on bow tie in dm-time plot for low frequencies. Default:1.0')
    values = parser.parse_args()

    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'

    if values.verbose:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)

    cand_pars = pd.read_csv(values.cand_param_file,
                            names=['fil_file', 'snr', 'stime', 'dm', 'width', 'label', 'kill_mask_path'])
    process_list = []
    for index, row in cand_pars.iterrows():
        process_list.append(
            [row['fil_file'], row['snr'], 2 ** row['width'], row['dm'], row['label'], row['stime'],
             row['kill_mask_path'], values])
    with Pool(processes=values.nproc) as pool:
        pool.map(cand2h5, process_list, chunksize=1)
