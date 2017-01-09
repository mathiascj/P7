# Creates query
table_to_dim_sql = ref_sql(table1, table2, key)

# Run query and return result
cursor = dw_rep.connection.cursor()
cursor.execute(table_to_dim_sql)

query_result = cursor.fetchall()
cursor.close()
return query_result