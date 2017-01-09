missing_keys = []

    # Maps table names to table_representations
    refs = {}
    for alpha, beta in self.refs.items():
        b = []
        if isinstance(alpha, str):
                a = dw_rep.get_data_representation(alpha)
        else:
            raise ValueError('Expected string in refs, got: ' +
                                 str(type(x)))

