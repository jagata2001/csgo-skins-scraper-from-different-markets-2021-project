from classes.database_classes.database_connect_class import Database_connect

import psycopg2



class Database_setup(Database_connect):
    psql_commands = [
        """

            CREATE TABLE IF NOT EXISTS proxy_data (
                proxy_id SERIAL PRIMARY KEY,
                ip VARCHAR(15) NOT NULL UNIQUE,
                port VARCHAR(5) NOT NULL,
                protocol VARCHAR(6) NOT NULL,
                server_resp_time DECIMAL(9,6) NOT NULL,
                check_time TIMESTAMP NOT NULL,
                last_use TIMESTAMP

            )

        """,
        """
            CREATE TABLE IF NOT EXISTS steam_market_data (
                skin_id BIGSERIAL PRIMARY KEY,
                name VARCHAR(128) NOT NULL UNIQUE,
                best_offer_price DECIMAL(12,3),
                best_order_price DECIMAL(12,3),
                offer_last_update TIMESTAMP,
                order_last_update TIMESTAMP
            )

        """,
        """
            CREATE TABLE IF NOT EXISTS market_csgo_data (
                skin_id BIGSERIAL PRIMARY KEY,
                name VARCHAR(128) NOT NULL UNIQUE,
                best_offer_price DECIMAL(12,3),
                best_order_price DECIMAL(12,3),
                offer_last_update TIMESTAMP,
                order_last_update TIMESTAMP
            )

        """,
        """
            CREATE TABLE IF NOT EXISTS dmarket_data (
                skin_id BIGSERIAL PRIMARY KEY,
                name VARCHAR(128) NOT NULL UNIQUE,
                best_offer_price DECIMAL(12,3),
                best_order_price DECIMAL(12,3),
                offer_last_update TIMESTAMP,
                order_last_update TIMESTAMP
            )

        """
    ]
    def __init__(self,username,password,database):
        super().__init__(username,password,database)

    def execute_commands(self):
        cursor = self.conn.cursor()
        for command in self.psql_commands:
            cursor.execute(command)
        cursor.close()
        print("Successfully created non existence tables")

    def __del__(self):
        if self.conn != None:
            self.conn.close()
