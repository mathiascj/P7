sql = \
    " SELECT * " + \
    " FROM " + table1.name + \
    " WHERE NOT EXISTS" \
    "( " + \
    "SELECT NULL " + \
    " FROM " + table2.name + \
    " WHERE " + table1.name + "." + key + \
    " = " \
    + table2.name + "." + key + \
    " )"
return sql