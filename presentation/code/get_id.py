def __get_id(self):
    """
    Goes through a single iteration of the keys of the source_ids.
    """
    if self.counter == len(self.source_ids):
        raise StopIteration('There are no more mappings to use')
    else:
        id = self.source_ids[self.counter]
        self.counter += 1
        return id