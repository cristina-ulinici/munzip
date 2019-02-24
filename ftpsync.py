import argparse
import configparser
import logging
from threading import Thread
import os
import time
import ftputil
import shutil

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
            src_dir = os.path.join(root, d)
            s_modif = os.stat(src_dir).st_mtime
            dest_dir = os.path.join(dst, src_dir[len(src)+1:])
            if (os.path.exists(dest_dir)):
                d_modif = os.stat(dest_dir).st_mtime
                logging.info('Directory %s already exists', src_dir[len(src):])
            else:
                try:
                    os.makedirs(dest_dir)
                    logging.info('Directory %s was created', dest_dir)
                except Exception as e:
                    logging.error('Unable to create directory %s: %s', dest_dir, e)

        for f in files:
            src_file = os.path.join(root, f)
            s_modif = os.stat(src_file).st_mtime
            dest_file = os.path.join(dst, src_file[len(src)+1:])
            if (os.path.isfile(dest_file)):
                d_modif = os.stat(dest_file).st_mtime
            else:
                d_modif = None

            if(int(s_modif)==int(d_modif)):
                logging.info('File %s: nothing changed', src_file[len(src):])
                print('%s already exists' % dest_file) # !!!!!!!!!!!!!!!!!!!!!
            else:
                logging.info('File %s has changed in the source', src_file[len(src):])
                print('%s has changed in the source' % dest_file) # !!!!!!!!!!!!!!!!!!!!!
                try:
                    shutil.copy2(src_file, dest_file[:len(dest_file)-len(f)])
                except Exception as e:
                    logging.error('Unable to copy %s: %s', src_file, e)

nr_loc = len(config.sections())-1
t = [0 for i in range(0,nr_loc)]

for i in range(0, nr_loc):
    try:
        t[i] = Thread(target=sync, args=(i,))
        t[i].start()
    except Exception as e:
        logging.error('Thread %d: %s', i, e)





# with ftputil.FTPHost('ftp.dlptest.com', 'dlpuser@dlptest.com', 'puTeT3Yei1IJ4UYT7q0r') as host:
#     for root, dirs, files in host.walk('/'):
#         for f in files:
#             print(f)
