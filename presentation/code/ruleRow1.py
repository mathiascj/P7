# Gets the attribute names for columns needed for test
column_arg_names = self.setup_columns(dw_rep, self.table_name, self.column_names, self.column_names_exclude)

func_args = inspect.getargspec(self.constraint_function).args
if len(func_args) != len(column_arg_names) + len(self.constraint_args):
    raise ValueError("""Number of columns and number of arguments do not match""")