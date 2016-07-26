import time
import multiprocessing as mp
from multiprocessing.connection import Listener
address = ('localhost',6111)
listener = Listener(address)


while True:
    print 'Listening...'
    if listener.poll():
        cmd = listener.recv()
        print 'recieved: ', cmd

    time.sleep(5)

