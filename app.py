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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get("per_page", default=3, type=int)
    parameters = request.args.to_dict()
    paginated_query = Store.query.paginate(page=page, per_page=per_page, error_out=False)
    invent = paginated_query.items
    if 'name' in parameters and parameters['name']:
        names = [name.strip() for name in parameters.get('name').split(',')]
        if len(names) > 1:
            inven = Store.query.filter(Store.name.in_(names)).all
        else:
            inven = Store.query.filter(Store.name.ilike(parameters.get('name'))).all
        data = [item.deserialize() for item in inven]
        return jsonify(data), 200
    else:
        data = [item.deserialize() for item in invent]
        return jsonify(data), 200

@app.get("/employee", methods=["GET"])
@cache.cached(timeout=300)
async def get_employee():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get("per_page", default=3, type=int)
    parameters = request.args.to_dict()
    paginated_query = Employee.query.paginate(page=page, per_page=per_page, error_out=False)
    invent = paginated_query.items
    if 'name' in parameters and parameters['name']:
        names = [name.strip() for name in parameters.get('name').split(',')]
        if len(names) > 1:
            inven = Employee.query.filter(Employee.name.in_(names)).all
        else:
            inven = Employee.query.filter(Employee.name.ilike(parameters.get('name'))).all
        data = [item.deserialize() for item in inven]
        return jsonify(data), 200
    else:
        data = [item.deserialize() for item in invent]
        return jsonify(data), 200 

@app.get("/inventory", methods=["GET"])
async def get_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get("per_page", default=50, type=int)
    parameters = request.args.to_dict()
    paginated_query = Inventory.query.paginate(page=page, per_page=per_page, error_out=False)
    invent = paginated_query.items
    data = [item.deserialize() for item in invent]
    compare = data
    shared_values = []
    
    if 'flavor' in parameters and parameters['flavor']:
        flavors=[flavor.strip() for flavor in parameters.get('flavor').split(',')]
        if len(flavors)> 1:
            inven = Inventory.query.filter(Inventory.flavor.in_(flavors)).all()
        else:
            inven = Inventory.query.filter(Inventory.flavor.ilike(parameters.get('flavor')))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    if 'employee_id' in parameters and parameters['employee_id']:
        employee=[employee.strip() for employee in parameters.get('employee_id').split(',')]
        if len(employee)> 1:
            inven = Inventory.query.filter(Inventory.employee_id.in_(employee)).all()
        else:
            inven = Inventory.query.filter(Inventory.employee_id == parameters.get('employee_id'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()  
    
    if 'store_id' in parameters and parameters['store_id']:
        store=[store.strip() for store in parameters.get('store_id').split(',')]
        if len(store)> 1:
            inven = Inventory.query.filter(Inventory.store_id.in_(store)).all()
        else:
            inven = Inventory.query.filter(Inventory.store_id == parameters.get('store_id'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear() 


    if 'quantity[gte]' in parameters and parameters['quantity[gte]']:
        inven = Inventory.query.filter(Inventory.quantity >= parameters.get('quantity[gte]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    if 'quantity[lte]' in parameters and parameters['quantity[lte]']:
        inven = Inventory.query.filter(Inventory.quantity <= parameters.get('quantity[lte]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    if 'quantity[lt]' in parameters and parameters['quantity[lt]']:
        inven = Inventory.query.filter(Inventory.quantity < parameters.get('quantity[lt]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()
        
        
    if 'quantity[gt]' in parameters and parameters['quantity[gt]']:
        inven = Inventory.query.filter(Inventory.quantity > parameters.get('quantity[gt]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    if 'quantity[eq]' in parameters and parameters['quantity[eq]']:
        inven = Inventory.query.filter(Inventory.quantity == parameters.get('quantity[eq]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()


    if 'date' in parameters and parameters['date']:
        inven = Inventory.query.filter(Inventory.date == parameters.get('date'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()
    
    if 'date[gte]' in parameters and parameters['date[gte]']:
        inven = Inventory.query.filter(Inventory.date >= parameters.get('date[gte]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    if 'date[lte]' in parameters and parameters['date[lte]']:
        inven = Inventory.query.filter(Inventory.date <= parameters.get('date[lte]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

    if 'date[lt]' in parameters and parameters['date[lt]']:
        inven = Inventory.query.filter(Inventory.date < parameters.get('date[lt]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()
        
        
    if 'date[gt]' in parameters and parameters['date[gt]']:
        inven = Inventory.query.filter(Inventory.date > parameters.get('date[gt]'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()
    
    if 'is_season_flavor' in parameters and parameters['is_season_flavor']:
        inven = Inventory.query.filter(Inventory.is_season_flavor == parameters.get('is_season_flavor'))
        data=[item.deserialize() for item in inven]
        for tuple in data:
            if tuple in compare:
                shared_values.append(tuple)
        compare.clear()
        compare = compare + shared_values
        shared_values.clear()

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
    df=pd.read_csv("C:\\Users\\grego\\Desktop\\PracticaORM\\frozono60.csv")

    df2 = df["Listed By"].unique()

    df3 = df["Store"] .unique()
    print (df3)
    with DBContext() as db:
        for store in df3:
            entry = Store(
                name = store
                )
            db.add(entry)

        for employee in df2:
            entry2 = Employee(
                name = employee
                )
            db.add(entry2)
        db.commit()
        storeFK = pd.read_sql('SELECT * FROM store', conn)
        storeData = pd.DataFrame({'name': df["Store"]})
        merge_store = storeData.merge(storeFK, on='name', how='left', sort=False)

        employeeFK = pd.read_sql('SELECT * FROM employee', conn)
        employeeData = pd.DataFrame({'name': df["Listed By"]})
        merge_employee = employeeData.merge(employeeFK, on='name', how='left', sort=False)

        df["Store"] = merge_store["id"]
        df["Listed By"] = merge_employee["id"]
    
        for index, rows in df.iterrows():
            if rows[3] == "Yes":
                value = True
            else:
                value = False
            entry3 = Inventory(
                store_id = rows[0],
                employee_id = rows[5],
                date = rows[1],
                flavor = rows[2],
                is_season_flavor = value,
                quantity = rows[4]
            )
            db.add(entry3)
        db.commit()
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
