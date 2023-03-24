import subprocess
import database
import time
import os
import random


def getTime():
    status, tim = subprocess.getstatusoutput("date +'%F %H:%M:%S'")
    tims = tim.split(' ')
    tims[1] = tims[1].replace("-", ":")
    return tims[0]+' '+tims[1]


def fault_wait(fault_id, wait_type, interval):
    print('fault_{}_{}_1\t{}'.format(fault_id, wait_type, getTime()))
    time.sleep(interval)
    print('fault_{}_{}_2\t{}'.format(fault_id, wait_type, getTime()))


# Highly concurrent inserts
def fault_1(table_name, client, interval, duration, ncolumns, nrows, colsize):
    rpt = colsize // 3
    sql2 = 'insert into '+table_name + \
        ' select generate_series(1,{}), '.format(nrows)
    for i in range(ncolumns):
        sql2 += 'repeat(round(random()*999)::text,{}), '.format(rpt)
    sql2 += 'now();'
    fault_wait(1, 'begin', interval)
    database.concurrent_execute_sql(client, duration, sql2)
    fault_wait(1, 'end', interval)


# Missing indexes
def fault_2(table_name, client, interval, duration, tabsize):
    sql = 'select * from '+table_name+' where id='
    fault_wait(2, 'begin', interval)
    database.concurrent_execute_sql(client, duration, sql, tabsize)
    fault_wait(2, 'end', interval)


# Heavy workload
def fault_3(interval, bench, benchconfig):
    fault_wait(3, 'begin', interval)
    os.system(
        "$OLTPBENCH_HOME/oltpbenchmark -b {} -c {} --execute=true".format(bench, benchconfig))
    fault_wait(3, 'end', interval)


# Vacuum
def fault_4(table_name, client, interval, duration, tabsize):
    sql = 'select * from '+table_name+' where id='
    fault_wait(4, 'begin', interval)
    database.concurrent_execute_sql(client, duration, sql, tabsize)
    fault_wait(4, 'end', interval)


# Highly concurrent commits
def fault_5(table_name, client, interval, duration, ncolumns, nrows, colsize):
    rpt = colsize // 3
    sql2 = 'insert into '+table_name + \
        ' select generate_series(1,{}), '.format(nrows)
    for i in range(ncolumns):
        sql2 += 'repeat(round(random()*999)::text,{}), '.format(rpt)
    sql2 += 'now();'
    fault_wait(5, 'begin', interval)
    database.concurrent_execute_sql(client, duration, sql2, commit_interval=1)
    fault_wait(5, 'end', interval)


if __name__ == '__main__':
    print(getTime())
