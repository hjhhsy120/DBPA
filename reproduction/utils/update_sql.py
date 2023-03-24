import time
from multiprocessing.pool import *
import psycopg2
import random
import string
import os
import csv
import argparse
import subprocess
import numpy as np

config = {
        "host":         ("The hostname to postgresql", "localhost" ),
        "port":         ("The port number to postgresql", 5432 ),
        "dbname":         ("Database name", "postgres"),
        "user":         ("user of the database", "postgres"),
        "password":     ("the password", "postgres")
    }


def getTime():
    status, tim = subprocess.getstatusoutput("date +'%H-%M-%S'")
    return tim.replace("-", ":")


def fault_time(fault_id, wait_type):
    print('fault_{}_{}\t{}'.format(fault_id, wait_type, getTime()))


def execute_sql(table_name, ncolumns, colsize, duration, nrows):
    rpt = colsize // 3
    start = time.time()
    while time.time()-start < duration:
        try:
            conn = psycopg2.connect(database=config["dbname"][1], user=config["user"][1], password=config["password"][1],
                                    host=config["host"][1], port=config["port"][1])
            cursor = conn.cursor()
            cnt = 0
            while time.time()-start < duration:
                sql = 'update '+table_name+' set '
                colid = random.randint(0, ncolumns-1)
                rowid = random.randint(1, nrows-1)
                sql += 'name{}=repeat(round(random()*999)::text,{}) where id={};'.format(
                    colid, rpt, rowid)
                cursor.execute(sql)
                cnt += 1
                conn.commit()
            conn.commit()
            conn.close()
        except Exception as e:
            fault_time('lockwait', 'end2')
            print(e)
    fault_time('lockwait', 'end3')
    return cnt


def update_all(table_name, ncolumns, colsize, duration):

    start = time.time()
    while time.time()-start < duration:
        try:
            conn = psycopg2.connect(database=config["dbname"][1], user=config["user"][1], password=config["password"][1],
                                    host=config["host"][1], port=config["port"][1])
            cursor = conn.cursor()
            while time.time() - start < duration:
                up_i = random.randint(0, ncolumns-1)
                xx = ''
                rpt = colsize // 3
                for _ in range(rpt):
                    xx += str(random.randint(100, 999))
                sql = 'update '+table_name+' set name{}=\'{}\';'.format(up_i, xx)
                fault_time('lockwait', 'begin')
                cursor.execute(sql)
                fault_time('lockwait', 'end0')
                conn.commit()
            conn.close()
        except Exception as e:
            fault_time('lockwait', 'end1')
            print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=int, default=3, help='client number')
    parser.add_argument('-a', help='whether full update', default=False)
    parser.add_argument('--duration', type=int, default=60, help='duration')
    parser.add_argument('--ncolumns', type=int, default=10,
                        help="number of columns except id and ts")
    parser.add_argument('--colsize', type=int, default=200,
                        help="size of each varchar column")
    parser.add_argument('--nrows', type=int, default=10,
                        help="number of rows per insertion")
    parser.add_argument('--table_name', type=str,
                        default='aa', help="name of table")

    args = parser.parse_args()
    client = args.c
    all_update_f = args.a
    duration = args.duration
    ncolumns = args.ncolumns
    colsize = args.colsize
    nrows = args.nrows
    table_name = args.table_name

    random.seed(time.time())

    if all_update_f:
        print("all")
        pool = Pool(client+1)
        pool.apply_async(update_all, (table_name, ncolumns, colsize, duration,))
        time.sleep(1)
    else:
        pool = Pool(client)
    execute_cnt = []
    for _ in range(client):
        execute_cnt.append(pool.apply_async(
            execute_sql, (table_name, ncolumns, colsize, duration, nrows,)))
    print([execute_cnt[i].get() for i in range(client)])
    print('avg_exe_cnt : {}'.format(
        np.mean([execute_cnt[i].get() for i in range(client)])))
    pool.close()
    pool.join()
