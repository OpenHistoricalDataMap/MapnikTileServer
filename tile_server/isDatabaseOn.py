#!/usr/bin/env python3

import os
import psycopg2
import time

"""
Wait till the database is online
"""


def isDatabaseActive() -> bool:
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('try onnecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="postgis",
                                database=os.environ['POSTGRES_DB'],
                                user=os.environ['POSTGRES_USER'],
                                password=os.environ['POSTGRES_PASSWORD'])

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()
        return True


print("wait 10 secounds")
time.sleep(10)
# todo check if database is ready not just online

while isDatabaseActive() is False:
    print("Database is still offline")
    time.sleep(2)

print("Database is now online")
