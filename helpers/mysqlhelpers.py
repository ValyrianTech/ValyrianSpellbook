#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import errorcode

from helpers.loghelpers import LOG


def create_database(cursor, database):
    """
    Create a new database

    :param cursor: A MySQL cursor object
    :param database: The name of the database (string)
    """
    LOG.info('Creating database %s' % database)

    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(database))
    except mysql.connector.Error as err:
        LOG.error("Failed creating database: {}".format(err))


def create_tables(cursor, tables):
    """
    Create tables in a MySQL database

    :param cursor: A MySQL cursor object
    :param tables: A dict containing the sql statements to create each table
    """
    LOG.info('Creating tables...')
    for table_name in tables:
        table_description = tables[table_name]
        try:
            LOG.info("Creating table {}: ".format(table_name))
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                LOG.info("already exists.")
            else:
                LOG.error(err.msg)
        else:
            LOG.info("OK")


def initialize_database(database, tables, user, password):
    # Try to make a connection, if the database does not exist yet, create the database and create the tables in it
    """
    Check if a database exists, if not create it

    :param database: The name of the database (string)
    :param tables: A dict containing the sql statements to create the tables (dict)
    :param user: The username for the database (string)
    :param password: The password for the database (string)
    """
    cnx = mysql.connector.connect(user=user, password=password)
    cursor = cnx.cursor()

    try:
        cursor.execute("USE {}".format(database))
    except mysql.connector.Error as err:
        LOG.info("Database {} does not exists.".format(database))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor=cursor, database=database)
            LOG.info("Database {} created successfully.".format(database))
            cnx.database = database
            create_tables(cursor=cursor, tables=tables)
        else:
            LOG.error(err)

    cursor.close()
    cnx.close()


def log_sql_query(sql_query):
    """
    Log the sql query

    :param sql_query: The sql query (string)
    """
    LOG.info('=== Begin SQL query ===')
    for line in sql_query.split('\n'):
        LOG.info(' SQL | %s' % line.strip())

    LOG.info('=== End SQL query ===')


class mysql_cursor(object):
    """
    A MySQL cursor object that automatically handles creating and closing the cursor and connection when used in a 'with' statement
    """
    def __init__(self, user, password, database, host='127.0.0.1', port=3306, commit=False):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self.cnx = None
        self.cursor = None
        self.commit = commit

    def __enter__(self):
        LOG.info('Creating mysql cursor to database %s @ %s:%s' % (self.database, self.host, self.port))
        self.cnx = mysql.connector.connect(user=self.user,
                                           password=self.password,
                                           database=self.database,
                                           host=self.host,
                                           port=self.port)
        self.cursor = self.cnx.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Make sure data is committed to the database
        if self.commit is True:
            LOG.info('Committing data')
            self.cnx.commit()

        LOG.info('Closing mysql cursor')
        self.cursor.close()
        self.cnx.close()
