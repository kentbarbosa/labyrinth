from __future__ import print_function

from multiprocessing.managers import BaseManager
import Queue
queue = Queue.Queue()
class QueueManager(BaseManager):pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('127.0.0.1',50001),authkey=b'labyrinth')
s = m.get_server()
print('Command manager running. Ctrl-C to exit.')
s.serve_forever()

    
