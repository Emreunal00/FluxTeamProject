from flask import Blueprint, request, jsonify

users_blueprint = Blueprint('users', __name__)

# Sample user data
users = []

@users_blueprint.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@users_blueprint.route('/users', methods=['POST'])
def add_user():
    user_data = request.json
    users.append(user_data)
    return jsonify({"message": "User added successfully"}), 201
