import argparse
import logging
import zipfile
import os
from multiprocessing import *
from threading import Thread
import time
import sys

def unzip(filename, dir, i):
    zf = zipfile.ZipFile(filename)
    dir = os.path.dirname(os.path.abspath(filename))
    # uncompress_size = sum((file.file_size for file in zf.infolist()))
    # extracted_size = 0

    for file in zf.infolist():
        try:
            zf.extract(file, dir)
        except Exception as e:
            raise
            print(e) #logging...
        # extracted_size += file.file_size
        # print("%s %%" % int(extracted_size * 100/uncompress_size))


def start_unzip(i, q, terminated, lock):
    while(not q.empty()):
        try:
            file = q.get()
            # os.system('cls')
            logging.debug('Extracting \'%s\' from thread %d', file, i)
            p = Process(target=unzip, args=(file, dir, i,))
            p.start()
            p.join(args.ttimeout)
            if(p.is_alive()):
                p.terminate()
                lock.acquire()
                terminated += 1
                lock.release()
                logging.info('\'%s\' reached timeout', file)
            sys.stdout.write("\rProcessing: %d/%d | Terminated: %d" % (total-q.qsize(), total, terminated))
        except Exception as e:
            logging.error('\'%s\': %s', file, e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", help="number of threads", type=int, default=3)
    parser.add_argument("-log", nargs='?', help="logfile name", default="log.txt")
    parser.add_argument("-ttimeout", help="ttimeout in sec for a zip file", type=float, default=60)
    parser.add_argument("-gtimeout", help="total ttimeout in sec", type=float, default=180)
    parser.add_argument("dir", help="dir with zip files")

    args = parser.parse_args()
    args.log = args.log if args.log!=None else "log.txt"

    logging.basicConfig(filename=args.log, format='[%(asctime)s]\t[%(levelname)s]\t\t%(message)s', level=logging.DEBUG)
    logging.info('%d unzipping threads running', args.t)
    logging.info('%s set as logfile', args.log)
    logging.info('%ds - timeout for a single zip file', args.ttimeout)
    logging.info('%ds - total timeout', args.gtimeout)
    logging.info('Start unzipping ...')

    files = Queue()
    terminated = 0

    for file in os.listdir(args.dir):
        if file.endswith(".zip"):
            f = os.path.join(args.dir, file)
            files.put(f)
    total = files.qsize()

    logging.info('Total nr of zipfiles: %d', files.qsize())

    lock = Lock()
    t = [0 for i in range(0, args.t)]
    ttime = time.time()
    # os.system('cls')

    for i in range(0, args.t):
        try:
            logging.debug('Thread %d starting', i)
            t[i] = Thread(target=start_unzip, args=(i, files, terminated,lock,))
            t[i].start()
        except Exception as e:
            logging.error('Thread %d: %s', i, e)

    active = True
    while(time.time()-ttime <= args.gtimeout and active):
        active = False
        for th in t:
            if(th.is_alive()):
                active = True
                time.sleep(1)
    else:
        sys.exit()

    if(active):
        logging.info('Reached timeout')
