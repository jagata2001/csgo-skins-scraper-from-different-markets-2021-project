from classes.database_classes.database_connect_class import Database_connect

import psycopg2


class Database_proxy(Database_connect):
    def __init__(self,username,password,database):
        super().__init__(username,password,database)

    def insert_proxy_data_into_database(self,values):
        sql_command = f"""
                    INSERT INTO proxy_data(ip,port,protocol,server_resp_time,check_time)
                        VALUES  (%s,%s,%s,%s,%s)
                    ON CONFLICT (ip)
                        DO UPDATE SET
                                port=EXCLUDED.port,protocol=EXCLUDED.protocol,
                                server_resp_time=EXCLUDED.server_resp_time,
                                check_time=EXCLUDED.check_time
                            WHERE proxy_data.ip=EXCLUDED.ip;
                     """
        cursor = self.conn.cursor()
        cursor.executemany(sql_command,values)
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount

    def count_proxy(self):
        sql_command = f"""
                    SELECT COUNT(*) FROM proxy_data
                        WHERE AGE(NOW(),last_use)>'15 minutes' or last_use is NULL
                     """
        cursor = self.conn.cursor()
        cursor.execute(sql_command)
        result = cursor.fetchone()
        cursor.close()
        return result[0]

    def select_proxy_for_steam_market(self,limit=5000):
        sql_command = f"""
                    SELECT ip,port,protocol FROM proxy_data
                        WHERE (AGE(NOW(),last_use)>'15 minutes' or last_use is NULL)
                        ORDER BY check_time DESC limit %s;
                       """
        cursor = self.conn.cursor()
        cursor.execute(sql_command,(limit,))
        result = cursor.fetchall()
        cursor.close()
        return result
    def update_proxy_after_use(self,ip):
        sql_command = f"""
                    UPDATE proxy_data set last_use=NOW() WHERE ip=%s
                     """
        cursor = self.conn.cursor()
        cursor.execute(sql_command,(ip,))
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount
