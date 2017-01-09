# Final setup of the entire SQL command
lookup_sql = "SELECT DISTINCT " + ','.join(select_sql) + \
             " FROM " + \
             " ( " + " NATURAL JOIN ".join(self.table_name) + " ) " + \
             " AS t1 ," + \
             " ( " + " NATURAL JOIN ".join(self.table_name) + " ) " + \
             " AS t2 " + \
             " WHERE " + and_alpha + " AND " + or_beta