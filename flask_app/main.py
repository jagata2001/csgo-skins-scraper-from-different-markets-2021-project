from flask import Flask, render_template, request, redirect, url_for,jsonify
from classes.database_skin_class import Database_skin
import json
from decimal import Decimal
app = Flask(__name__)

@app.route("/",methods=["get"])
def index():
    first_market_name = request.args.get('first_market_name', default = 'steam', type = str)
    second_market_name = request.args.get('second_market_name', default = 'steam', type = str)

    order_by = request.args.get('order_by', default = "name", type = str)
    market_for_order = request.args.get('market_for_order', default = "first", type = str)
    asc_desc = request.args.get('asc_desc', default = "asc", type = str)

    first_min_price = request.args.get('first_min_price', default = None, type = float)
    first_max_price = request.args.get('first_max_price', default = None, type = float)
    first_min_percentage = request.args.get('first_min_percentage', default = None, type = float)
    first_max_percentage = request.args.get('first_max_percentage', default = None, type = float)

    second_min_price = request.args.get('second_min_price', default = None, type = float)
    second_max_price = request.args.get('second_max_price', default = None, type = float)
    second_min_percentage = request.args.get('second_min_percentage', default = None, type = float)
    second_max_percentage = request.args.get('second_max_percentage', default = None, type = float)


    filters = {
        "prices":[
            first_min_price,
            first_max_price,
            second_min_price,
            second_max_price
        ],
        "percentages":[
            first_min_percentage,
            first_max_percentage,
            second_min_percentage,
            second_max_percentage
        ]
    }
    db = Database_skin("jagata","password","steam_skin_data")
    data = db.load_skin_data(
            first_market_name,second_market_name,
            order_by,market_for_order,asc_desc,
            filters
        )

    db.close()

    if len(data) >= 100:
        max_range = 100
    else:
        max_range = len(data)

    return render_template("index.html",data=data,max_range=max_range)

app.run(debug=True)
