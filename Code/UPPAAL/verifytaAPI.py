import subprocess
import re


def run_verifyta(xml, queries, *args, verifyta):
    """
    :param xml: string giving the path to a uppaal project XML file
    :param queries: string giving the path to a uppaal query file
    :param *args: other args giving to verifyta, e.g. -t 2 for getting the fastest trace.
    :param verifyta: string giving the path to verifyta
    :return 0: Returns the standard output, i.e. if the queries were satisfied
    :return 1: Returns the trace(s) of the queries.
    """
    res = subprocess.run([verifyta, xml, queries] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.stdout, res.stderr   # ResultBin, Trace


def run_verifyta_some_breadth(xml, queries, verifyta):
    """
    :param xml: string giving the path to a uppaal project XML file
    :param queries: string giving the path to a uppaal query file
    :param verifyta: string giving the path to verifyta
    :return 0: Returns the standard output, i.e. if the queries were satisfied
    :return 1: Returns the trace(s) of the queries.
    """
    # -o 0: Argument for Breadth First search
    # -t 0: Argument for finding some trace
    result, trace = run_verifyta(xml, queries, '-o 0', '-t 0', verifyta)
    return result, trace


def run_verifyta_best_randbestdepth(xml, queries, verifyta):
    """
    :param xml: string giving the path to a uppaal project XML file
    :param queries: string giving the path to a uppaal query file
    :param verifyta: string giving the path to verifyta
    :return 0: Returns the standard output, i.e. if the queries were satisfied
    :return 1: Returns the trace(s) of the queries.
    """
    # -o 4: Argument for Random Best Depth First
    # -t 3: Argument for finding Best Trace
    result, trace = run_verifyta(xml, queries, '-o 4', '-t 3', verifyta)
    return result, trace


def get_trace_time(trace, clock_name='global_c'):
    """
    :param trace: The trace represented as bytes given by uppaal, from which we find the last value of a global clock.
    :param clock_name: A string representing the name of the global clock from which we will extract a value
    :return: An integer representing the last clock value
    """
    lst = trace.splitlines()
    s = str(lst[-1])    # The information we want is on the last line
    res = re.search(clock_name + ">=(\d+)", s).group(1)
    return int(res)


def get_best_cost(result, default):
    """
    :param result: The result of running uppaal given as bytes. Requires that it was run with the -t flag
    :return: An integer representing the best cost
    """
    lst = result.splitlines()
    if len(lst) == 13:      # If the length is not 13, we know the verification failed
        s = str(lst[-2])    # The information we want is on the second last line
        res = re.search(' -- Best solution   : (\d+)', s).group(1)
    else:
        res = default
    return int(res)


def get_satisfied(result):
    """
    :param result: binary string with a result from UPPAAL CORA
    :return: Boolean, False if some query did not succeed, True if all queries succeeded
    """
    s = str(result)
    if re.search('-- Property is NOT satisfied.', s):
        return False
    else:
        return True




