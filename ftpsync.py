import argparse
import configparser
import logging
from threading import Thread, Timer
from multiprocessing import *
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

logging.basicConfig(filename=log_file, format='[%(asctime)s]\t[%(levelname)s]\t\t[line:%(lineno)d]\t%(message)s', level=logging.DEBUG)
logging.info('Config file: %s', args.config)


def sync(i):
    sync_nr = 'Sync_#'+ str(i+1)
    logging.debug('Thread %i started with %s', i, sync_nr)
    # src_type = config[sync_nr]['src_type']
    # src_name = config[sync_nr]['src_name']
    src = config[sync_nr]['src']
    # dst_type = config[sync_nr]['dst_type']
    dst = config[sync_nr]['dst']
    # dst_name = config[sync_nr]['dst_name']
    # ftp_mode = config[sync_nr]['ftp_mode']

    if (config[sync_nr]['delete_extra_dst_content'] == 'YES' and config[sync_nr]['move_files'] == 'YES'):
        logging.error('Inconsistency in config file in [%s]: delete_extra_dst_content and move_files', sync_nr)
        return

    src_files = []

    # if src_type = dst_type = DISK
    for root, dirs, files in os.walk(src):
        for d in dirs:
            src_dir = os.path.join(root, d)
            src_files.append(src_dir[len(src)+1:])
            s_modif = os.stat(src_dir).st_mtime
            dest_dir = os.path.join(dst, src_dir[len(src)+1:])
            if (os.path.exists(dest_dir)):
                d_modif = os.stat(dest_dir).st_mtime
                logging.info('%s: Directory %s already exists', sync_nr, src_dir[len(src):])
            else:
                try:
                    os.makedirs(dest_dir)
                    logging.info('%s: Directory %s was created', sync_nr, dest_dir)
                except Exception as e:
                    logging.error('%s: Unable to create directory %s: %s', sync_nr, dest_dir, e)

        for f in files:
            src_file = os.path.join(root, f)
            src_files.append(src_file[len(src)+1:])
            s_modif = os.stat(src_file).st_mtime
            dest_file = os.path.join(dst, src_file[len(src)+1:])
            if (os.path.isfile(dest_file)):
                d_modif = os.stat(dest_file).st_mtime
            else:
                d_modif = 0

            if(int(s_modif)==int(d_modif)):
                logging.info('%s: File %s: nothing changed', sync_nr, src_file[len(src):])
            else:
                logging.info('%s: File %s has changed in the source', sync_nr, src_file[len(src):])
                try:
                    shutil.copy2(src_file, dest_file[:len(dest_file)-len(f)])
                    logging.info('%s: File %s is up to date', sync_nr, src_file[len(src):])
                except Exception as e:
                    logging.error('%s: Unable to copy %s: %s', sync_nr, src_file, e)


    if(config[sync_nr]['move_files'] == 'YES'):
        for i in os.listdir(src):
            item = os.path.join(src, i)
            if(os.path.isfile(item)):
                try:
                    os.remove(item)
                    logging.info('%s: %s deleted', sync_nr, item)
                except Exception as e:
                    logging.error('%s: Unable to delete file: %s: %s', sync_nr, item, e)
            if(os.path.isdir(item)):
                try:
                    shutil.rmtree(item)
                    logging.info('%s: %s deleted', sync_nr, item)
                except Exception as e:
                    logging('%s: Unable to delete directory %s: %s', sync_nr, item, e)

    if(config[sync_nr]['delete_extra_dst_content'] == 'YES'):
        for root, dirs, files in os.walk(dst):
            for f in files:
                f = os.path.join(root, f)[len(dst)+1:]
                if (f not in src_files):
                    try:
                        f = os.path.join(root, f)
                        os.remove(f)
                        logging.info('%s: %s deleted from %s', sync_nr, f, dst)
                    except Exception as e:
                        logging.error('%s: Unable to delete file: %s: %s', sync_nr, f, e)
            for d in dirs:
                d = os.path.join(root, d)[len(dst)+1:]
                if(d not in src_files):
                    try:
                        d = os.path.join(root, d)
                        shutil.rmtree(d)
                        logging.info('%s: %s deleted from %s', sync_nr, d, dst)
                    except Exception as e:
                        logging.error('%s: Unable to delete directory %s: %s', sync_nr, d, e)

def start_sync(i):
    sync_nr = 'Sync_#'+ str(i+1)
    status = 'Ok'
    while(True):
        try:
            start_time = time.time()
            p = Process(target=sync, args=(i,))
            p.start()
            p.join(int(config[sync_nr]['timeout']))
            last_update = time.time()
            if(p.is_alive()):
                p.terminate()
                status = 'Failed'
                logging.debug('%s reached timeout', sync_nr)

            print('%s | SRC-%s: %s >>> DST-%s: %s | Last update: %s | Sync duration: %s | Status: %s' % (
                sync_nr, config[sync_nr]['src_type'], config[sync_nr]['src_name'], config[sync_nr]['dst_type'], config[sync_nr]['dst_name'], time.ctime(last_update), last_update-start_time, status))

            while (time.time()-start_time <  int(config[sync_nr]['update_interval'])):
                time.sleep(1)
        except Exception as e:
            logging.error('Thread %d: %s', i, e)
            return


if __name__ == "__main__":
    nr_loc = len(config.sections())-1
    t = [0 for i in range(0,nr_loc)]

    for i in range(0, nr_loc):
        try:
            t[i] = Thread(target=start_sync, args=(i,))
            t[i].start()
        except Exception as e:
            logging.error('Thread %d: %s', i, e)
            continue




# with ftputil.FTPHost('ftp.dlptest.com', 'dlpuser@dlptest.com', 'puTeT3Yei1IJ4UYT7q0r') as host:
#     for root, dirs, files in host.walk('/'):
#         for f in files:
#             print(f)
