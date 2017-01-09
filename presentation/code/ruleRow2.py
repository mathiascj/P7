# Iterates over each row, calling the constraint function upon it
for row in dw_rep.iter_join(self.table_name):

    # Finds parameters. First attributes then additional params.
    arguments = []
    for name in column_arg_names:
        arguments.append(row[name])

    if self.constraint_args:
        arguments.append(*self.constraint_args)

    # Runs function on parameters
    if not self.constraint_function(*arguments):
        wrong_rows.append(row)

if not wrong_rows:
    self.__result__ = True