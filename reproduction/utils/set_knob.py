import psycopg2
import argparse
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


config = {
        "host":         ("The hostname to postgresql", "localhost" ),
        "port":         ("The port number to postgresql", 5432 ),
        "dbname":         ("Database name", "postgres"),
        "user":         ("user of the database", "postgres"),
        "password":     ("the password", "postgres")
    }


def set_knob(knob_name, knob_value):
    conn = psycopg2.connect(user=config["user"][2], password=config["password"][2], host=config["host"][1], port=config["port"][1])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor=conn.cursor()
    cmd="ALTER SYSTEM SET " + knob_name + "= \'" + knob_value + "\';"
    cursor.execute(cmd)
    conn.commit()
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-kn', help='knob name')
    parser.add_argument('-kv', help='knob value')
    args = parser.parse_args()
    knob_name = args.kn
    knob_value = args.kv
    set_knob(knob_name, knob_value)
