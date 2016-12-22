import pymysql

def generate_db_link(host_in,unix_socket_in,user_in,passwd_in,datebase_in):
    conn = pymysql.connect(host=host_in, unix_socket=unix_socket_in, user=user_in, passwd=passwd_in)
    cursor = conn.cursor()
    cursor.execute("use "+datebase_in)

    return conn,cursor

def execute_single_to_db(insert_sql,args_in,cursor):
    cursor.execute(insert_sql,args_in)
    cursor.connection.commit()

def execute_many_to_db(insert_sql,args_in,cursor):
    cursor.executemany(insert_sql,args_in)
    cursor.connection.commit()

def close_db_link(conn,cursor):
    cursor.close()
    conn.close()