import os
import subprocess
import argparse
import time
import _thread
import database

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arguments from cmd')
    parser.add_argument('--nrows', type=int, default=10000,
                        help="number of rows")
    parser.add_argument('--droprate', type=float,
                        default=0.5, help="drop rate")
    parser.add_argument('--table_name', type=str,
                        default='aa', help="name of table")
    args = parser.parse_args()

    nrows = args.nrows
    droprate = args.droprate
    table_name = args.table_name

    firstid = int(nrows * droprate)

    database.execute_sql(['delete from '+table_name+' where id<{};'.format(firstid)])
    print('drop',table_name, nrows, droprate)
