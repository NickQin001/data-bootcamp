import os
import sys
# import oracle library #make sure you install first
import cx_Oracle
#set all parameters **************************************
oracle_instant_client_abs_path = r"C:\instantclient-basic-windows.x64-21.7.0.0.0dbru\instantclient_21_7"  # noqa

try:
    if sys.platform.startswith("darwin"):
        lib_dir = os.path.abspath(oracle_instant_client_abs_path)
        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
    elif sys.platform.startswith("win32"):
        cx_Oracle.init_oracle_client(lib_dir=oracle_instant_client_abs_path)
except Exception as err:
    print(err)
    sys.exit(1)

class OracleDB(cx_Oracle.Connection):
    db_server = 'localhost'
    db_port = '1522'
    db_server_name = 'app12c'
    db_username = 'MASY_YQ2149' 
    db_password = 'MASY_YQ2149' 
    
    dsn_tns = cx_Oracle.makedsn(db_server, db_port, db_server_name)
    
    def __init__(self):
        super(OracleDB,self).__init__(user=self.db_username, password=self.db_password, dsn=self.dsn_tns)
        
    def get_connection(self):
        return self
    
    
if __name__ =="__main__":
    with OracleDB().get_connection() as connection:
        print("Successfully connected")