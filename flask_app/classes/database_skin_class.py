from classes.database_connect_class import Database_connect

import psycopg2

class Database_skin(Database_connect):
    def __init__(self,username,password,database):
        super().__init__(username,password,database)
        self.table_names = {
            "steam":"steam_market_data",
            "marketcsgo":"market_csgo_data",
            "dmarket":"dmarket_data"
        }
        self.asc_desc_dict = {
            "ASC":"ASC",
            "DESC":"DESC"
        }

    def load_skin_data(self,first_market_name,second_market_name,order_by,market_for_order,asc_desc,filters):
        order_by_col = {

                "name":"name",
                "best_offer_price":"best_offer_price",
                "best_order_price":"best_order_price",
                "offer_last_update":"offer_last_update",
                "order_last_update":"order_last_update",
                "percentage":"percentage"

        }
        try:
            first = self.table_names[first_market_name]
            second = self.table_names[second_market_name]
        except KeyError:
            first = "steam_market_data"
            second = "market_csgo_data"

        if market_for_order == "first":
            market_for_order = "fr"
        else:
            market_for_order = "sc"

        try:
            order_by = order_by_col[order_by]
        except KeyError:
            order_by = "name"
        try:
            asc_desc = self.asc_desc_dict[asc_desc.upper()]
        except KeyError:
            asc_desc = "ASC"

        if order_by == "percentage":
            order_text = f"{market_for_order}_{order_by} {asc_desc}"
        else:
            order_text = f"{market_for_order}.{order_by} {asc_desc}"

        ### filters  prices###
        prices = filters["prices"]

        where_clause_price = f""
        operators = [">=","<="]
        start = 0
        for i in range(len(prices)):
            operator = operators[i%2]
            if i < 2:
                if prices[i] != None:
                    if start != 0:
                        where_clause_price+=f" AND "
                    where_clause_price+=f"fr.best_offer_price{operator}{prices[i]}"
                    start+=1
            else:
                if prices[i] != None:
                    if start != len(prices)-1 and start != 0:
                        where_clause_price +=f" AND "
                    where_clause_price+=f"sc.best_offer_price{operator}{prices[i]}"
                    start+=1

        ###############

        ### filters  percentage###
        percentages = filters["percentages"]

        where_clause_percentage = f""
        operators = [">=","<="]
        start = 0
        for i in range(len(percentages)):
            operator = operators[i%2]
            if i < 2:
                if percentages[i] != None:
                    if start != 0:
                        where_clause_percentage+=f" AND "
                    where_clause_percentage+=f"""
                            CASE
                                WHEN sc.best_offer_price = 0
                                    THEN 0
                                ELSE
                                    ROUND( (((sc.best_offer_price-fr.best_offer_price)*100)/sc.best_offer_price),3)::float
                            END{operator}{percentages[i]}
                        """
                    start+=1
            else:
                if percentages[i] != None:
                    if start != len(percentages)-1 and start != 0:
                        where_clause_percentage +=f" AND "
                    where_clause_percentage+=f"""
                                CASE
                                    WHEN fr.best_offer_price = 0
                                        THEN 0
                                    ELSE
                                        ROUND( (((fr.best_offer_price-sc.best_offer_price)*100)/fr.best_offer_price),3)::float
                                END{operator}{percentages[i]}
                            """
                    start+=1

        if where_clause_price != "" and where_clause_percentage != "":
            where_clause = f"AND {where_clause_price} AND  {where_clause_percentage}"
        elif where_clause_price != "":
            where_clause = f"AND {where_clause_price}"
        elif where_clause_percentage != "":
            where_clause = f"AND {where_clause_percentage}"
        else:
            where_clause = f""
        ###############
        sql_commad = f"""
                    SELECT
                        fr.name,
                        fr.best_offer_price::float,
                        CASE
                            WHEN sc.best_offer_price = 0
                                THEN 0
                            ELSE
                                ROUND( (((sc.best_offer_price-fr.best_offer_price)*100)/sc.best_offer_price),3)::float
                        END as fr_percentage,
                        CAST(DATE_TRUNC('seconds',AGE(NOW(),fr.offer_last_update)) AS VARCHAR),
                        sc.best_offer_price::float,
                        CASE
                            WHEN fr.best_offer_price = 0
                                THEN 0
                            ELSE
                                ROUND( (((fr.best_offer_price-sc.best_offer_price)*100)/fr.best_offer_price),3)::float
                        END as sc_percentage,
                        CAST(DATE_TRUNC('seconds',AGE(NOW(),sc.offer_last_update)) AS VARCHAR)
                    FROM {first} AS fr JOIN {second} AS sc
                        ON fr.name = sc.name
                        WHERE
                            fr.best_offer_price IS NOT NULL
                                AND
                            sc.best_offer_price IS NOT NULL
                                {where_clause}
                        ORDER BY {order_text};
                      """

        cursor = self.conn.cursor()
        cursor.execute(sql_commad)
        result = cursor.fetchall()
        cursor.close()
        return result
