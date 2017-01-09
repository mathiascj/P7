# Generates id names for sources and DW,
# zipping names and replacement objects into a dictionary,
# which is later used as a scope.
self.dw_id = '__0__'
self.scope = {self.dw_id: self.dw_conn}
counter = 0

for entry in source_conns:
    source_id = "__" + str(source_conns.index(entry) + 1) + "__"
    self.source_ids.append(source_id)
    source = self.conn_scope.__getitem__(counter)
    self.scope[source_id] = source
    counter += 1