import argparse
import logging


parser = argparse.ArgumentParser()
parser.add_argument("-t", help="number of threads/processes", type=int, default=3)
parser.add_argument("-log", nargs='?', help="logfile name", default="log.txt")
parser.add_argument("-ttimeout", help="ttimeout in sec for a zip file", type=int, default=60)
parser.add_argument("-gtimeout", help="total ttimeout in sec", type=int, default=180)
parser.add_argument("dir", help="dir with zip files")

args = parser.parse_args()
args.log = args.log if args.log!=None else "log.txt"

logging.basicConfig(filename=args.log, format='[%(asctime)s]\t[%(levelname)s]\t\t%(message)s', level=logging.DEBUG)
logging.info('%d unzipping processes running', args.t)
logging.info('%s set as logfile', args.log)
logging.info('%ds - timeout for a single zip file', args.ttimeout)
logging.info('%ds - total timeout', args.gtimeout)
logging.info('Start unzipping ...')
