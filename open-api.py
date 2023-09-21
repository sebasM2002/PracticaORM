from flask import Flask
from flask_openapi3 import OpenAPI

app = Flask(__name__)
api = OpenAPI(app)

app = Flask(__name__)
api = OpenAPI(app)

with open("frozono-open-api.json", "r") as f:
    spec = api.load_spec(f)

api.generate_routes()