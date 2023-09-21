from flask import Flask, jsonify, request
from flask_openapi3 import OpenAPI
from db import DBContext, engine
from models import Store, Inventory, Employee

app = Flask(__name__)
api = OpenAPI(app)

with open("frozono-open-api.json", "r") as f:
    spec = api.load_spec(f)

@app.route('/inventory', methods=['GET'])
def get_inventory():
    with DBContext() as db:
        entries = db.query(Inventory).all()
        return jsonify([entry.to_dict() for entry in entries])

@app.route('/inventory', methods=['POST'])
def create_inventory_entry():
    data = request.get_json()
    with DBContext() as db:
        entry = Inventory(
            store=data['Store'],
            date=data['Date'],
            flavor=data['Flavor'],
            is_season_flavor=data['Is Season Flavor'],
            quantity=data['Quantity'],
            listed_by=data['Listed By']
        )
        db.add(entry)
        db.commit()
    return jsonify(entry.to_dict()), 201

@app.route('/inventory/upload', methods=['POST'])
def upload_csv():
    # Aquí implementarías la lógica para cargar el CSV y agregar las entradas a la base de datos
    pass

@app.route('/inventory/<int:id>', methods=['GET'])
def get_inventory_by_id(id):
    with DBContext() as db:
        entry = db.query(Inventory).get(id)
        if not entry:
            return "Entry not found", 404
        return jsonify(entry.to_dict())

@app.route('/inventory/<int:id>', methods=['PUT'])
def update_inventory_entry(id):
    data = request.get_json()
    with DBContext() as db:
        entry = db.query(Inventory).get(id)
        if not entry:
            return "Entry not found", 404
        entry.quantity = data.get('Quantity', entry.quantity)
        entry.listed_by = data.get('Listed By', entry.listed_by)
        db.commit()
    return jsonify(entry.to_dict())

@app.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory_entry(id):
    with DBContext() as db:
        entry = db.query(Inventory).get(id)
        if not entry:
            return "Entry not found", 404
        db.delete(entry)
        db.commit()
    return "", 204

api.generate_routes()

if __name__ == '__main__':
    app.run(debug=True)
