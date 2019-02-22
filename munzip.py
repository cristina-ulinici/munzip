import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-t", help="number of threads", type=int)
parser.add_argument("-log", nargs='?', help="logfile name")  # numele optional -
parser.add_argument("-ttimeout", help="ttimeout in sec for a zip file", type=int)
parser.add_argument("-gtimeout", help="total ttimeout in sec", type=int)
parser.add_argument("dir", help="dir with zip files")

args = parser.parse_args()
