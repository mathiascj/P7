# If references not given. We check refs between all tables.
if not self.refs:
    self.refs = dw_rep.refs

# Performs check for each pair of main table and foreign key table.
for table, dims in self.refs.items():
    for dim in dims:
        key = dim.key

        # Check that each entry in main table has match
        if self.points_to_all:
            query_result = referential_check(table, dim, key, dw_rep)

            if query_result:
                for row in query_result:
                    msg = '{}: {} in {} not found in {}' \
                        .format(key, row[0], table.name, dim.name)
                    missing_keys.append(msg)