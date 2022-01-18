import argparse
import os

from mega import Mega

def maincli():
    parser = argparse.ArgumentParser()
    parser.add_argument('downloadUrl', nargs=1)
    parser.add_argument('destinationDirectory', nargs='?', default=os.path.realpath('.'))
    args = parser.parse_args()
    m = Mega().login()
    m.download_url(args.downloadUrl[0], args.destinationDirectory)


if __name__ == '__main__':
    maincli()