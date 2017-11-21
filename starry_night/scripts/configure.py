#!/usr/bin/env python
# coding: utf-8

'''
Usage:
    configure -c <confFile> [<image>...] [options]

Options:
    What do you want to configure?
    -s              Star catalogue
    -c <confFile>   Camera config file
    --crop          Configurate crop positions
    --visLimits     Configure visibility limits

    --version       Show version.
    --debug         debug it [default: False]
'''
import pkg_resources
import logging

from docopt import docopt
import numpy as np
import pandas as pd
import os
import time
import sys
import configparser
import matplotlib.pyplot as plt
from starry_night import skycam
from re import split
from IPython import embed



__version__ = pkg_resources.require('starry_night')[0].version
directory = os.path.join(os.environ['HOME'], '.starry_night')
if not os.path.exists(directory):
    os.makedirs(directory)

# setup logging
log = logging.getLogger('starry_night')
log.setLevel(logging.DEBUG)
logfile_path = os.path.join(
    directory, 'starry_night.log'
    )
# create handler for file and console output
logfile_handler = logging.FileHandler(filename=logfile_path)
logstream_handler = logging.StreamHandler()
logfile_handler.setLevel(logging.DEBUG)
logstream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(name)s | %(message)s',
    datefmt='%H:%M:%S',
)
formatter.converter = time.gmtime  # use utc in log
logfile_handler.setFormatter(formatter)
logstream_handler.setFormatter(formatter)
log.addHandler(logfile_handler)
log.addHandler(logstream_handler)
logging.captureWarnings(True)




def main(args):
    log.info('starry_night started')
    log.info('version: {}'.format(__version__))
    
    if args['--debug']:
        log.info('DEBUG MODE - NOT FOR REGULAR USE')
        log.setLevel(logging.DEBUG)
        log.debug('started starry_night in debug mode')

    if not args['<image>']:
        log.error('No images were passed as args. Aborting')
        sys.exit(1)

    config = configparser.RawConfigParser()
    log.debug('Parsing config file: {}'.format(args['-c']))
    # configfile can be a filepath or a name of a predefined config file
    if '.' in args['-c'] or '/' in args['-c']:
        conf_succ = len(config.read(args['-c']))
    else:
        conf_succ = len(config.read(pkg_resources.resource_filename(
            'starry_night', 'data/{}_cam.config'.format(args['-c']))
        ))
    # conf_succ != 0 if config was read successfully
    if conf_succ == 0:
        log.error('Unable to parse config file. Does the file exist?')
        sys.exit(1)
    del conf_succ


    if args['--crop']:
        imgDict = skycam.getImageDict(args['<image>'][0], config)
        x = list(map(int, split('\\s*,\\s*', config['crop']['crop_x'])))
        y = list(map(int, split('\\s*,\\s*', config['crop']['crop_y'])))
        r = list(map(int, split('\\s*,\\s*', config['crop']['crop_radius'])))
        inside = list(map(int, split('\\s*,\\s*', config['crop']['crop_deleteinside'])))
        while True:
            df_cr = pd.DataFrame({'x':x, 'y':y, 'r':r, 'inside':inside})
            #config['crop']['crop_x'] = 0
            print('Current cropping configuration:')
            print(df_cr)
            img = imgDict['img'].copy()
            img_inv = imgDict['img'].copy()
            crop_mask = skycam.get_crop_mask(img, config['crop'])
            img[crop_mask] = 0
            img_inv[~crop_mask] = 0
            vmin = np.nanpercentile(img,5)
            vmax = np.nanpercentile(img,90)
            fig = plt.figure()
            ax1 = fig.add_subplot(121)
            ax1.imshow(img, cmap='gray', vmin=vmin, vmax=vmax)
            ax1.grid()
            ax1.set_title('Cropped Image - It looks like this')
            ax2 = fig.add_subplot(122)
            ax2.imshow(img_inv, cmap='gray', vmin=vmin, vmax=vmax)
            ax2.grid()
            ax2.set_title('Inverted - As double check')
            plt.show()

            print('You can change the cropping by setting new values\nfor x,y,r [float]and inside [boolean] like this: x[0]=42\n\n\n')
            embed()
            config['crop']['crop_x'] = str(x).replace('[','').replace(']','')
            config['crop']['crop_y'] = str(y).replace('[','').replace(']','')
            config['crop']['crop_radius'] = str(r).replace('[','').replace(']','')
            config['crop']['crop_deleteinside'] = str(inside).replace('[','').replace(']','')
            

    if args['--visLimits']:
        if len(args['<image>']) != 2:
            log.error('Abort. You need to provide 2 images. First image without clouds, second image fully covered sky.')
            sys.exit(1)
        imgDict1 = skycam.getImageDict(args['<image>'][0], config)
        imgDict2 = skycam.getImageDict(args['<image>'][1], config)



    if args['-s']:
        log.info('Configure new star catalogue')
        fail = True
        while fail:
            catalogue = resource_filename('starry_night', '../data/asu.tsv')
            try:
                stars = pd.read_csv(
                    catalogue,
                    sep=';',
                    comment='#',
                    header=0,
                    skipinitialspace=False,
                    index_col=4,
                )
                stars = stars.convert_objects(convert_numeric=True)
                fail = False
                log.info('Loading catalogue - successful')
            except:
                log.error('''Error loading catalogue.\n
                    It might be formatted in a wrong way.\n
                    Please follow the instructions.'''
                    )
                
                print(
                '''Please make sure that the catalogue contains:\n\t
                a header line before the actual data (no leading "\#"),\n\t
                columns: "gLon, gLat, ra, dec, HIP, vmag"\n\t
                commentaries must start with "\#"'''
                )

                '''
                stars = pd.read_csv(
                    catalogue,
                    sep=';',
                    comment='#',
                    header=0,
                    skipinitialspace=False,
                    index_col=4,
                )
                stars = stars.convert_objects(convert_numeric=True)
                '''
            log.info('Applying cuts')
            print('For good performance, we need to apply some cuts to the catalogue.')
    '''
    print(args)
    # TODO: read config file to obtain URL and stuff
    log.debug('Parsing config file: {}'.format(args['-c']))
    config = configparser.RawConfigParser()
    config.read(resource_filename(
        'starry_night', '../data/{}'.format(args['-c']))
    )
    '''



''' Main Loop '''
if __name__ == '__main__':
    args = docopt(
        doc=__doc__,
        version=__version__,
        )
    try:
        main(args)
    except (KeyboardInterrupt, SystemExit):
        log.info('Exit')
    except:
        raise
