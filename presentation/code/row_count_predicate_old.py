__author__ = 'Arash Michael Sami Kjær'
__maintainer__ = 'Mikael Vind Mikkelsen'

from .predicate import Predicate
from .report import Report


class RowCountPredicate(Predicate):

    def __init__(self, table_name, number_of_rows):
        """
        :param table_name: name of the table we are testing
        :param number_of_rows: number of rows we are testing for
        """
        self.__result__ = bool
        self.table_name = table_name
        self.number_of_rows = number_of_rows
        self.table = []
        self.row_number = int

    def run(self, dw_rep):
        self.row_number = 0
        self.table = []

        for row in dw_rep.get_data_representation(self.table_name):
            self.table.append(row)
            self.row_number += 1

        if len(self.table) == self.number_of_rows:
            self.__result__ = True
        else:
            self.__result__ = False

        return Report(result=self.__result__,
                      tables=self.table_name,
                      predicate=self,
                      elements=None,
                      msg="""The predicate did not hold, tested for {} row(s),
                      actual number of row(s): {}""".format(
                          self.number_of_rows, self.row_number
                      ))


