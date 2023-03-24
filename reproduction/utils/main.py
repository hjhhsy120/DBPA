import os
import subprocess
import argparse
import time
import _thread

from fault import fault_1, fault_2, fault_3, fault_4, fault_5


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arguments from cmd')
    parser.add_argument('--client_1', type=int, default=0, help='client_1')
    parser.add_argument('--client_2', type=int, default=0, help='client_2')
    parser.add_argument('--client_3', type=int, default=0, help='client_3')
    parser.add_argument('--client_4', type=int, default=0, help='client_4')
    parser.add_argument('--client_5', type=int, default=0, help='client_5')
    parser.add_argument('--duration', type=int, default=60, help='duration')
    parser.add_argument('--total_duration', type=int,
                        default=600, help='total_duration')
    parser.add_argument('--interval', type=int, default=30,
                        help='wait XX seconds before starting exec fault')
    parser.add_argument('--inflateRate', type=float,
                        default=0.5, help="inflate rate")

    parser.add_argument('--ncolumns', type=int, default=10,
                        help="fault 1 number of columns except id")
    parser.add_argument('--nrows', type=int, default=10,
                        help="fault 1 number of rows")
    parser.add_argument('--colsize', type=int, default=10,
                        help="fault 1 column length")

    parser.add_argument('--tabsize', type=int, default=10,
                        help="fault 2 table size")

    parser.add_argument('--bench', type=str,
                        default='tpcc', help="benchmark name")
    parser.add_argument('--benchconfig', type=str,
                        default='0.txt', help="benchmark config")

    parser.add_argument('--result', type=str,
                        default='0.txt', help="result file name")

    parser.add_argument('--table_name', type=str,
                        default='aa', help="name of table")
    args = parser.parse_args()

    client_1 = args.client_1
    client_2 = args.client_2
    client_3 = args.client_3
    client_4 = args.client_4
    client_5 = args.client_5
    duration = args.duration
    total_duration = args.total_duration
    interval = args.interval
    inflateRate = args.inflateRate
    ncolumns = args.ncolumns
    nrows = args.nrows
    colsize = args.colsize
    tabsize = args.tabsize
    bench = args.bench
    benchconfig = args.benchconfig
    result = args.result
    table_name = args.table_name

    if client_1 > 0:
        fault_1(table_name, client_1, interval,
                duration, ncolumns, nrows, colsize)
                
    if client_2 > 0:
        fault_2(table_name, client_2, interval, duration, tabsize)

    if client_3 > 0:
        fault_3(interval, bench, benchconfig)

    if client_4 > 0:
        fault_4(table_name, client_4, interval, duration, tabsize)

    if client_5 > 0:
        fault_5(table_name, client_5, interval,
                duration, ncolumns, nrows, colsize)
