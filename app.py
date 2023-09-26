from flask import Flask, jsonify, request
from flask_openapi3 import OpenAPI
import csv
from db import DBContext, engine
import sqlalchemy as sa

from models import Store, Inventory, Employee
from flask_openapi3 import Info, Tag
import pandas as pd

info = Info(title="book API", version="1.0.0")
app = OpenAPI(__name__, info=info)
count = 0

# with open("frozono-open-api.json", "r") as f:
#     spec = api.load_spec(f)

book_tag = Tag(name="book", description="Some Book")


@app.get("/inventory", methods=["GET"], tags=[book_tag])
def get_inventory():
    """
    SDSF inventory
    """
    with DBContext() as db:
        entries = db.query(Inventory).all()
        return jsonify([entry.to_dict() for entry in entries])


@app.post("/inventory", methods=["POST"])
def create_inventory_entry():
    data = request.get_json()
    with DBContext() as db:
        entry = Inventory(
            store=data["Store"],
            date=data["Date"],
            flavor=data["Flavor"],
            is_season_flavor=data["Is Season Flavor"],
            quantity=data["Quantity"],
            listed_by=data["Listed By"],
        )
        db.add(entry)
        db.commit()
    return jsonify(entry.to_dict()), 201


@app.post("/inventory/upload", methods=["POST"])
def upload_csv():
    conn = engine.connect()
    df=pd.read_csv("C:\\Users\\sebas\\Desktop\\PracticaORM\\PracticaORM\\frozono.csv")
    df = df.drop(df.columns[6], axis=1)
    df = df.dropna()
    df = df.reset_index(drop=True)

    df2 = df[" Listed By"].unique()
    df3 = df["Store"].unique()

    if count == 0:   
        data = pd.DataFrame({'name': df2})
        data.to_sql('employee', conn, if_exists='append', index=False)

        data = pd.DataFrame({'name': df3})
        data.to_sql('store', conn, if_exists='append', index=False)

        storeFK = pd.read_sql('SELECT * FROM store', conn)
        storeData = pd.DataFrame({'name': df["Store"]})
        merge_store = storeData.merge(storeFK, on='name', how='left', sort=False)

        employeeFK = pd.read_sql('SELECT * FROM employee', conn)
        employeeData = pd.DataFrame({'name': df[" Listed By"]})
        merge_employee = employeeData.merge(employeeFK, on='name', how='left', sort=False)

        data = pd.DataFrame({'store_id': merge_store["id"] , 'employee_id': merge_employee["id"] , 'date': df[" Date"] , 'flavor': df[" Flavor"] , 'is_season_flavor': df[" Is Season Flavor"] , 'quantity': df[" Quantity"]})
        data.to_sql('inventory', conn, if_exists="append", index=False)


    conn.close()
    return "",204

@app.get("/inventory/<int:id>", methods=["GET"])
def get_inventory_by_id(id):
    with DBContext() as db:
        entry = db.query(Inventory).get(id)
        if not entry:
            return "Entry not found", 404
        return jsonify(entry.to_dict())


@app.put("/inventory/<int:id>", methods=["PUT"])
def update_inventory_entry(id):
    data = request.get_json()
    with DBContext() as db:
        entry = db.query(Inventory).get(id)
        if not entry:
            return "Entry not found", 404
        entry.quantity = data.get("Quantity", entry.quantity)
        entry.listed_by = data.get("Listed By", entry.listed_by)
        db.commit()
    return jsonify(entry.to_dict())


@app.delete("/inventory/<int:id>", methods=["DELETE"])
def delete_inventory_entry(id):
    with DBContext() as db:
        entry = db.query(Inventory).get(id)
        if not entry:
            return "Entry not found", 404
        db.delete(entry)
        db.commit()
    return "", 204


# api.generate_routes()

if __name__ == "__main__":
    app.run(debug=True)
