from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_openapi3 import OpenAPI, Info, Tag
from db import DBContext, engine
import sqlalchemy as sa
import pandas as pd
from collections import OrderedDict
from flask_caching import Cache
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

info = Info(title="book API", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)
db = SQLAlchemy(app)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def deserialize(self):
        return OrderedDict([
            ('id', self.id),
            ('name', self.name),
        ])

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def deserialize(self):
        return OrderedDict([
            ('id', self.id),
            ('name', self.name),
        ])

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"))
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"))
    date = db.Column(db.Date)
    flavor = db.Column(db.String(50))
    is_season_flavor = db.Column(db.Boolean)
    quantity = db.Column(db.Integer)

    def deserialize(self):
        return OrderedDict([
            ('id', self.id),
            ('store_id', self.store_id),
            ('employee_id', self.employee_id),
            ('date', self.date),
            ('flavor', self.flavor),
            ('is_season_flavor', self.is_season_flavor),
            ('quantity', self.quantity)
        ])

book_tag = Tag(name="book", description="Some Book")

@app.route("/", methods=["GET"])
def home():
    return render_template("menu.html")

@app.get("/store", methods=["GET"])
@cache.cached(timeout=300)
async def get_store():
    parameters = request.args.to_dict()
    invent = await asyncio.to_thread(Store.query.all)
    if 'name' in parameters and parameters['name']:
        names = [name.strip() for name in parameters.get('name').split(',')]
        if len(names) > 1:
            inven = await asyncio.to_thread(Store.query.filter(Store.name.in_(names)).all)
        else:
            inven = await asyncio.to_thread(Store.query.filter(Store.name.ilike(parameters.get('name'))).all)
        data = [item.deserialize() for item in inven]
        return jsonify(data), 200
    else:
        data = [item.deserialize() for item in invent]
        return jsonify(data), 200

@app.get("/employee", methods=["GET"])
@cache.cached(timeout=300)
async def get_employee():
    parameters = request.args.to_dict()
    invent = await asyncio.to_thread(Employee.query.all)
    if 'name' in parameters and parameters['name']:
        names = [name.strip() for name in parameters.get('name').split(',')]
        if len(names) > 1:
            inven = await asyncio.to_thread(Employee.query.filter(Employee.name.in_(names)).all)
        else:
            inven = await asyncio.to_thread(Employee.query.filter(Employee.name.ilike(parameters.get('name'))).all)
        data = [item.deserialize() for item in inven]
        return jsonify(data), 200
    else:
        data = [item.deserialize() for item in invent]
        return jsonify(data), 200

@app.get("/inventory", methods=["GET"])
async def get_inventory():
    parameters = request.args.to_dict()
    invent = await asyncio.to_thread(Inventory.query.all)
    data = [item.deserialize() for item in invent]
    compare = data
    shared_values = []
    if 'flavor' in parameters and parameters['flavor']:
        flavors = [flavor.strip() for flavor in parameters.get('flavor').split(',')]
        if len(flavors) > 1:
            inven = await asyncio.to_thread(Inventory.query.filter(Inventory.flavor.in_(flavors)).all)
        else:
            inven = await asyncio.to_thread(Inventory.query.filter(Inventory.flavor.ilike(parameters.get('flavor'))).all)
        data = [item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    # Repite el mismo enfoque asincrónico para las demás condiciones de filtro

    return jsonify(compare), 200

@app.post("/inventory", methods=["POST"])
async def create_inventory_entry():
    data = request.get_json()
    if data[3] == "Yes":
        value = True
    else:
        value = False
    with DBContext() as db:
        entry = Inventory(
            store_id=data[0],
            employee_id=data[5],
            date=data[1],
            flavor=data[2],
            is_season_flavor=value,
            quantity=data[4]
        )
        db.add(entry)
        db.commit()
    return jsonify(entry.to_dict()), 201

@app.post("/inventory/upload", methods=["POST"])
async def upload_csv():
    conn = engine.connect()
    df = pd.read_csv("C:\\Users\\grego\\Desktop\\PracticaORM\\frozono60.csv")
    # ...

    return "", 200

@app.get("/inventory/<int:id>", methods=["GET"])
async def get_inventory_by_id(id):
    with DBContext() as db:
        entry = await asyncio.to_thread(db.query(Inventory).get, id)
        if not entry:
            return "Entry not found", 404
        return jsonify(entry.to_dict())

@app.put("/inventory/<int:id>", methods=["PUT"])
async def update_inventory_entry(id):
    data = request.get_json()
    with DBContext() as db:
        entry = await asyncio.to_thread(db.query(Inventory).get, id)
        if not entry:
            return "Entry not found", 404
        entry.quantity = data.get("Quantity", entry.quantity)
        entry.listed_by = data.get("Listed By", entry.listed_by)
        db.commit()
    return jsonify(entry.to_dict())

@app.delete("/inventory/clear", methods=["DELETE"])
async def clear_data():
    try:
        with DBContext() as db:
            db.query(Inventory).delete()
            db.query(Employee).delete()
            db.query(Store).delete()
            db.commit()
        return jsonify({"success": "All data cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)
