    if isinstance(beta, str):
        b.append(dw_rep.get_data_representation(beta))
            else:
                for x in beta:
                    if isinstance(x, str):
                        b.append(dw_rep.get_data_representation(x))
                    else:
                        raise ValueError('Expected string' + ' in refs, got: ' + str(type(x)))
            refs[a] = tuple(b)
        self.refs = refs