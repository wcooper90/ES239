from collections import deque

class Queue():
    def __init__(self, oh_name):
        self.queue = deque([])
        self.name = oh_name


    def enqueue(self, content):
        self.queue.append(content)


    def dequeue(self, client_id):
        to_remove = None
        for item in self.queue:
            if item.client_id == client_id:
                to_remove = item
                break
        if to_remove is not None:
            self.queue.remove(item)


    def __repr__(self):
        out = 'office hour queue for: '+ self.name + '\n '
        for item in self.queue:
            out += repr(item)
            out += "*"*40 + "\n"

        return out
