from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Plant

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plants.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
CORS(app)


@app.route("/plants", methods=["GET"])
def get_plants():
    """Get all plants with optional filtering."""
    plants = Plant.query.all()
    return jsonify([plant.to_dict() for plant in plants]), 200


@app.route("/plants/<int:id>", methods=["GET"])
def get_plant(id):
    """Get a single plant by ID."""
    plant = Plant.query.get(id)
    if not plant:
        return jsonify({"error": "Plant not found"}), 404
    return jsonify(plant.to_dict()), 200


@app.route("/plants", methods=["POST"])
def create_plant():
    """Create a new plant."""
    data = request.get_json()
    
    if not data or not all(key in data for key in ["name", "image", "price"]):
        return jsonify({"error": "Missing required fields: name, image, price"}), 400
    
    try:
        plant = Plant(
            name=data["name"],
            image=data["image"],
            price=data["price"],
            is_in_stock=data.get("is_in_stock", True)
        )
        db.session.add(plant)
        db.session.commit()
        return jsonify(plant.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route("/plants/<int:id>", methods=["PATCH"])
def update_plant(id):
    """Update a plant partially."""
    plant = Plant.query.get(id)
    if not plant:
        return jsonify({"error": "Plant not found"}), 404

    data = request.get_json()
    for attr in data:
        if hasattr(plant, attr):
            setattr(plant, attr, data[attr])

    db.session.commit()
    return jsonify(plant.to_dict()), 200


@app.route("/plants/<int:id>", methods=["DELETE"])
def delete_plant(id):
    """Delete a plant by ID."""
    plant = Plant.query.get(id)
    if not plant:
        return jsonify({"error": "Plant not found"}), 404

    db.session.delete(plant)
    db.session.commit()
    return "", 204


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
