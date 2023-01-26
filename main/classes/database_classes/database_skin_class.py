try:
    from classes.database_classes.database_connect_class import Database_connect
except:
    from database_connect_class import Database_connect

import psycopg2

class Database_skin(Database_connect):
    def __init__(self,username,password,database):
        super().__init__(username,password,database)

    def insert_skin_data_from_steam_market(self,data,type):
        if type == "offer":
            insert_price_column = "best_offer_price"
            insert_time_update_column = "offer_last_update"
        elif "order":
            insert_price_column = "best_order_price"
            insert_time_update_column = "order_last_update"
        sql_command = f"""
                    INSERT INTO steam_market_data(name,{insert_price_column},{insert_time_update_column})
                        VALUES (%s,%s,NOW())
                    ON CONFLICT (name)
                        DO UPDATE SET
                                {insert_price_column}=EXCLUDED.{insert_price_column},
                                {insert_time_update_column}=NOW()
                            WHERE steam_market_data.name=EXCLUDED.name
                      """
        cursor = self.conn.cursor()
        cursor.executemany(sql_command,data)
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount

    def insert_skin_data_from_market_csgo(self,data,type):
        if type == "offer":
            insert_price_column = "best_offer_price"
            insert_time_update_column = "offer_last_update"
        elif "order":
            insert_price_column = "best_order_price"
            insert_time_update_column = "order_last_update"
        sql_command = f"""
                    INSERT INTO market_csgo_data(name,{insert_price_column},{insert_time_update_column})
                        VALUES (%s,%s,NOW())
                    ON CONFLICT (name)
                        DO UPDATE SET
                                {insert_price_column}=EXCLUDED.{insert_price_column},
                                {insert_time_update_column}=NOW()
                            WHERE market_csgo_data.name=EXCLUDED.name
                      """
        cursor = self.conn.cursor()
        cursor.executemany(sql_command,data)
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount
    def insert_skin_data_from_dmarket(self,data):
        sql_command = f"""
                    INSERT INTO dmarket_data(name,best_offer_price,best_order_price,offer_last_update,order_last_update)
                        VALUES (%s,%s,%s,NOW(),NOW())
                    ON CONFLICT (name)
                        DO UPDATE SET
                                best_offer_price=EXCLUDED.best_offer_price,
                                best_order_price=EXCLUDED.best_order_price,
                                offer_last_update=NOW(),
                                order_last_update=NOW()
                            WHERE dmarket_data.name=EXCLUDED.name
                      """
        cursor = self.conn.cursor()
        cursor.executemany(sql_command,data)
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount

    def select_all_skin_names(self):
        sql_command = f"""
                    SELECT sm.name FROM steam_market_data AS sm
                        UNION
                    SELECT mc.name FROM market_csgo_data AS mc;
                  """
        cursor = self.conn.cursor()
        cursor.execute(sql_command)
        result = cursor.fetchall()
        cursor.close()


        return [name[0] for name in result]


if __name__ == "__main__":
    skin_db = Database_skin("jagata","password","steam_skin_data")
    skin_db.select_all_skin_names()
