import argparse
import configparser
import logging
from threading import Thread
import os
import time
import ftputil

parser = argparse.ArgumentParser()
parser.add_argument("-config", help="number of threads", nargs='?')
args = parser.parse_args()
args.config = args.config if args.config!=None else "conf.txt"

config = configparser.ConfigParser()
config.read(args.config)

log_file = config['General']['log_path']

logging.basicConfig(filename=log_file, format='[%(asctime)s]\t[%(levelname)s]\t\t%(message)s', level=logging.DEBUG)
logging.info('Config file: %s', args.config)

def sync(i):
    sync_nr = 'Sync_#'+ str(i+1)
    logging.debug('Thread %i started with %s', i, sync_nr)
    src_type = config[sync_nr]['src_type']
    src_name = config[sync_nr]['src_name']
    src = config[sync_nr]['src']
    dst_type = config[sync_nr]['dst_type']
    dst = config[sync_nr]['dst']
    dst_name = config[sync_nr]['dst_name']
    ftp_mode = config[sync_nr]['ftp_mode']
    update_interval = config[sync_nr]['update_interval']
    delete_extra_dst_content = config[sync_nr]['delete_extra_dst_content']
    move_files = config[sync_nr]['move_files']
    timeout = config[sync_nr]['timeout']

    #  1. verific daca fisierele sunt la fel in ambele parti
    #  2. verific daca s-au mai facut modificari in fisierele din src de la 'last update'
    for root, dirs, files in os.walk(src):
        for d in dirs:
            dir = os.path.join(root, d)[len(src):]
            print(dir)
        for f in files:
            file = os.path.join(root, f)[len(src):]
            print(file)


nr_loc = len(config.sections())-1
t = [0 for i in range(0,nr_loc)]

for i in range(0, nr_loc):
    try:
        t[i] = Thread(target=sync, args=(i,))
        t[i].start()
    except Exception as e:
        logging.error('Thread %d: %s', i, e)





with ftputil.FTPHost('ftp.dlptest.com', 'dlpuser@dlptest.com', 'puTeT3Yei1IJ4UYT7q0r') as host:
    # names = host.listdir(host.curdir)
    # for name in names:
    #     # if host.path.isfile(name):
    #         # Remote name, local name
    #         # host.download(name, name)
    #     print(name)
    for root, dirs, files in host.walk('/'):
        for f in files:
            print(f)
