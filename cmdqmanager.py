
from multiprocessing.managers import BaseManager
import Queue
queue = Queue.Queue()
class QueueManager(BaseManager):pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('127.0.0.1',50001),authkey='labyrinth')
s = m.get_server()
s.serve_forever()

    
