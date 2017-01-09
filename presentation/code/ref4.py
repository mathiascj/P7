        # Check that each entry in foreign key table has match
        if self.all_pointed_to:
            query_result = referential_check(dim, table, key, dw_rep)

            if query_result:
                for row in query_result:
                    msg = '{}: {} in {} not found in {}' \
                        .format(key, row[0], dim.name, table.name)
                    missing_keys.append(msg)

if not missing_keys:
    self.__result__ = True