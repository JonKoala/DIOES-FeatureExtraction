
class Dataset(list):

    def __init__(self, entries=[]):
        list.extend(self, entries)

    @property
    def data(self):
        return [entry.data for entry in self]

    @property
    def target(self):
        return [entry.target for entry in self]

class DatasetEntry:

    def __init__(self, id, data, target):
        self.id = id
        self.data = data
        self.target = target

    def __repr__(self):
        return '<DatasetEntry(id={}, data={}, target={})>'.format(self.id, self.data, self.target)
