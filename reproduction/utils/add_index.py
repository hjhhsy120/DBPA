import psycopg2
import argparse

config = {
        "host":         ("The hostname to postgresql", "localhost" ),
        "port":         ("The port number to postgresql", 5432 ),
        "dbname":         ("Database name", "postgres"),
        "user":         ("user of the database", "postgres"),
        "password":     ("the password", "postgres")
    }

def build_index(table_name,idx_num):
    conn = psycopg2.connect(database = config['dbname'][1], user = config['user'][1], password = config['password'][1],
                            host = config['host'][1], port = config['port'][1])
    cursor = conn.cursor()
    for i in range(0, idx_num):
        the_sql = 'CREATE INDEX index_'+table_name+'_' + str(i) + ' ON '+table_name+'(name' + str(i) + ');'
        print(the_sql)
        cursor.execute(the_sql)
    conn.commit()
    conn.close()
    return


def drop_index(table_name):
    conn = psycopg2.connect(database=config['dbname'][1], user=config['user'][1], password=config['password'][1],
                            host=config['host'][1], port=config['port'][1])
    cursor = conn.cursor()
    cursor.execute("select indexname from pg_indexes where tablename='"+table_name+"';")
    idxs = cursor.fetchall()
    for idx in idxs:
        the_sql = 'DROP INDEX ' + idx[0] + ';'
        print(the_sql)
        cursor.execute(the_sql)
    conn.commit()
    conn.close()
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='number of columns for index, 0 to drop all', type=int)
    parser.add_argument('--table_name', help='table to create the index on', type=str,default='aa')
    args = parser.parse_args()
    c = args.c
    table_name = args.table_name
    if c == 0:
        drop_index(table_name)
    else:
        build_index(table_name,c)
