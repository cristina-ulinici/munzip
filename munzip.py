import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-t", help="number of threads", type=int, default=3)
parser.add_argument("-log", nargs='?', help="logfile name", default="log.txt")
parser.add_argument("-ttimeout", help="ttimeout in sec for a zip file", type=int, default=60)
parser.add_argument("-gtimeout", help="total ttimeout in sec", type=int, default=180)
parser.add_argument("dir", help="dir with zip files")

args = parser.parse_args()
args.log = args.log if args.log!=None else "log.txt"

print(args.t)
print(args.log)
