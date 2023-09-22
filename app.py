from flask import Flask, jsonify, request
from flask_openapi3 import OpenAPI
import csv
from db import DBContext, engine

from models import Store, Inventory, Employee

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title="book API", version="1.0.0")
app = OpenAPI(__name__, info=info)

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
    file = request.files["csvFile"]
    with DBContext() as db:
        csv_reader = csv.DictReader(file.stream)
        for row in csv_reader:
            entry = Inventory(
                store=row["Store"],
                date=row["Date"],
                flavor=row["Flavor"],
                is_season_flavor=row["Is Season Flavor"] == "Yes",
                quantity=int(row["Quantity"]),
                listed_by=row["Listed By"],
            )
            db.add(entry)
        db.commit()
    return (
        jsonify(
            {"message": "CSV uploaded and data added to the database successfully!"}
        ),
        201,
    )


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
