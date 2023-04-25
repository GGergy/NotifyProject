class HopeDict:
    def __init__(self, size=1000):
        self.size = size
        self.collection = {}

    def __getitem__(self, index):
        return self.collection.get(index, None)

    def __setitem__(self, index, value):
        self.collection[index] = value
        if len(self.collection.keys()) > self.size:
            self.collection.pop(list(self.collection.keys())[0])
