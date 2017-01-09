    def visit_Call(self, node):
        """ The visit of a call node.
         Is an overwrite of Visit_Call ignoring all calls
         except for those we need to modify.
        :param node: A call node
        """
        name = self.__find_call_name(node)
        if name in ATOMIC_SOURCES:
            id = self.__get_id()
            self.__replace_connection(id, node)

        elif name in WRAPPERS:
            if self.dw_flag:
                raise Exception('There is more than one wrapper in this program')
            else:
                id = self.dw_id
                self.__replace_connection(id, node)
                self.dw_flag = True
