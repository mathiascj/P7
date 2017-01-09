cursor = dw_rep.connection.cursor()
cursor.execute(lookup_sql)
query_result = cursor.fetchall()
cursor.close()

# Create dict, so that attributes have names
names = [t[0] for t in cursor.description]
dict_result = []
for row in query_result:
    dict_result.append(dict(zip(names, row)))

# If any rows were fetched. Assertion fails
if not dict_result:
    self.__result__ = True