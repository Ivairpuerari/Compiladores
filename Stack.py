class Stack(object):
    def __init__(self):
        self.data = []
 
    def push(self, e):
        self.data.append(e)

    def pop(self,size):
        for i in range(0,size):
            self.data.pop(-1)
    def size(self):
        return len(self.data)
   
    def top(self):
        return self.data[-1]