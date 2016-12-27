import pymysql

def generate_db_link(host_in,unix_socket_in,user_in,passwd_in,datebase_in):
    conn = pymysql.connect(host=host_in, unix_socket=unix_socket_in, user=user_in, passwd=passwd_in)
    cursor = conn.cursor()
    cursor.execute("use "+datebase_in)

    return conn,cursor

#execute insert,update,delete sql
def execute_single_to_db(insert_sql,args_in,cursor):
    cursor.execute(insert_sql,args_in)
    cursor.connection.commit()

#execute insert,update,delete sql
def execute_many_to_db(insert_sql,args_in,cursor):
    num_execute = cursor.executemany(insert_sql,args_in)
    cursor.connection.commit()
    return num_execute

#execute select sql and get the result as list
def select_from_db(select_sql,args_in,cursor):
    output_list = []
    cursor.execute(select_sql,args_in)
    output_list = list(cursor.fetchall())
    return output_list

def close_db_link(conn,cursor):
    cursor.close()
    conn.close()