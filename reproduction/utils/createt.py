import os
import subprocess
import argparse
import time
import _thread
import database

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arguments from cmd')
    parser.add_argument('--ncolumns', type=int, default=10,
                        help="number of columns except id and ts")
    parser.add_argument('--nrows', type=int, default=10000,
                        help="number of rows")
    parser.add_argument('--colsize', type=int, default=200,
                        help="size of each varchar column")
    parser.add_argument('--table_name', type=str,
                        default='aa', help="name of table")
    args = parser.parse_args()

    ncolumns = args.ncolumns
    nrows = args.nrows
    colsize = args.colsize
    table_name = args.table_name

    sql0 = 'drop table if exists '+table_name+';'
    sql1 = 'create table '+table_name+'(id bigint, '
    for i in range(ncolumns):
        sql1 += 'name{} varchar({}), '.format(i, colsize)
    sql1 += 'in_time timestamp);'

    rpt = colsize // 3
    sql2 = 'insert into '+table_name + \
        ' select generate_series(1,{}), '.format(nrows)
    for i in range(ncolumns):
        sql2 += 'repeat(round(random()*999)::text,{}), '.format(rpt)
    sql2 += 'now();'
    database.execute_sql([sql0, sql1, sql2])
    print('table created', table_name, ncolumns, nrows, colsize)
