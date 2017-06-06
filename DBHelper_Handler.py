# Coded by : Pranav Sharan
# Purpose  : Handles calls made by CentralPage.html and fetches data from database
import re

from flask import Flask, render_template, request
import psycopg2

app = Flask('__name__')
user = ""
password = ""

try:
    pattern = re.compile("username\s*")
    with open('credentials.txt') as fp:
        for line in fp:
            if pattern.search(line):
                y = line.strip().split(":")
                user = y[1]
    fp.close()

    pattern = re.compile("password\s*")
    with open('credentials.txt') as fp:
        for line in fp:
            if pattern.search(line):
                y = line.strip().split(":")
                password = y[1]
    fp.close()

except Exception as e:
    print "File error: ", e


dbname = 'postgres'
sw_dbname = 'database_helper'
table_data = []
table_names = []
table_meta = []


def get_credentials():
    try:
        pattern = re.compile("username\s*")
        with open('credentials.txt') as fp:
            for line in fp:
                if pattern.search(line):
                    y = line.strip().split(":")
                    user = y[1]
        fp.close()

        pattern = re.compile("password\s*")
        with open('credentials.txt') as fp:
            for line in fp:
                if pattern.search(line):
                    y = line.strip().split(":")
                    password = y[1]
        fp.close()

    except Exception as e :
        print "File error: ",e

# Create the application database
def create_database():
    con = psycopg2.connect(
        "dbname='" + dbname + "' user='" + user + "'port=5433 host='localhost' password='" + password + "'")
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (sw_dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (sw_dbname,))  # Create the database
        print 'A database created'
    else:
        print 'A database named {0} already exists'.format(sw_dbname)

    # Clean up
    cur.close()
    con.commit()
    con.close()


def CreateTable(query):
    con = psycopg2.connect(
        "dbname='" + sw_dbname + "' user='" + user + "'port=5433 host='localhost' password='" + password + "'")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    cur.close()
    con.close()


@app.route('/')
@app.route('/CentralPage.html')
def getTablesInfo():
    print ("Initial")
    create_database()
    con = psycopg2.connect(
        "dbname='" + sw_dbname + "' user='" + user + "'port=5433 host='localhost' password='" + password + "'")
    cur = con.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
    rows = cur.fetchall()
    table_names = []
    print rows
    for row in rows:
        print row
        if row is None:
            pass
        else:
            table_names.extend(row)
    con.commit()
    cur.close()
    con.close()
    return render_template('CentralPage.html', table_names=table_names, table_data=table_data)


@app.route('/CentralPage.html', methods=['POST', 'GET'])
def getTableSchema():
    table_data = []
    text = ""
    table_name = ""
    delete_table = ""
    column_datatype = []
    insert_table = ""

    delete_table = request.form['DeleteTable']
    insert_table = request.form['InsertTable']
    insert_table_query = request.form['InsertTableQuery']

    print ("Here")
    try:
        text = request.form['GetQuery']
    except Exception as e:
        print (e)

    if text=="":
        print ("Do not insert")
    else:
        processed_text = text.upper()
        CreateTable(processed_text)

    table_name = request.form.get('getTableName')
    print ("Table Name:")
    print (table_name)
    con = psycopg2.connect(
        "dbname='" + sw_dbname + "' user='" + user + "'port=5433 host='localhost' password='" + password + "'")

    if delete_table != "YES":
        cur = con.cursor()
        cur.execute(
            "select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = '%s' " % table_name)
        rows = cur.fetchall()
        for row in rows:
            table_data.extend(row)
            print row
        con.commit()
        cur.close()

        cur = con.cursor()
        cur.execute(
            "select data_type from INFORMATION_SCHEMA.COLUMNS where table_name = '%s' " % table_name)
        rows = cur.fetchall()
        for row in rows:
            column_datatype.extend(row)
            print row
        con.commit()
        cur.close()

    if delete_table == "YES":
        cur = con.cursor()
        cur.execute(
            "DROP TABLE %s;" % table_name)
        con.commit()
        cur.close()
    else:
        print("Do not delete")

    if insert_table == "Yes":
        cur = con.cursor()
        cur.execute(
            insert_table_query)
        con.commit()
        cur.close()
    else:
        print("Do not insert")

    cur = con.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
    rows = cur.fetchall()
    table_names = []
    print rows
    for row in rows:
        print row
        if row is None:
            pass
        else:
            table_names.extend(row)
    con.commit()
    cur.close()

    rows = []
    if table_name != "" and delete_table != "YES":
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM %s;" % table_name)
        rows = cur.fetchall()
        table_meta = []
        print rows
        for row in rows:
            print row
            if row is None:
                pass
            else:
                table_meta.extend(row)
        con.commit()
        cur.close()

    con.close()

    #print (table_meta)
    #Get table data
    return render_template('CentralPage.html', table_data=table_data, table_names=table_names, table_meta=rows, table_name=table_name, column_datatype=column_datatype)


if __name__ == '__main__':
    app.run(debug=True)