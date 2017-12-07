import sys
sys.path.insert(0, '.')

from dnschaind.app import server


if __name__ == '__main__':
    server.start()
