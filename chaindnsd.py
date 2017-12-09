import sys
sys.path.insert(0, '.')

from chaindnsd.app import server


if __name__ == '__main__':
    server.start()
