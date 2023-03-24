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


def create_database():
    conn = psycopg2.connect(user=config["user"][2], password=config["password"][2], host=config["host"][1], port=config["port"][1])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor=conn.cursor()
    for dbname in ["tpcc","tatp","smallbank","voter","tpcc_test"]:
        cmd = "create database " + dbname + " owner " + config["user"][1] + ";"
        cursor.execute(cmd)
        cmd = "grant all privileges on database " + dbname + " to " + config["user"][1] + ";"
        cursor.execute(cmd)
    conn.commit()
    return


if __name__ == '__main__':
    create_database()
