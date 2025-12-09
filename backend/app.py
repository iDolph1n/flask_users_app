from flask import Flask, jsonify, request
from flask_cors import CORS
from database import Database

app = Flask(__name__)
CORS(app)  # CORS для фронтенда

db = Database()

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = db.get_all_users()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = db.get_user_by_id(user_id)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()

        # Валидация данных
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Name and email are required'}), 400

        name = data['name'].strip()
        email = data['email'].strip()

        if not name or not email:
            return jsonify({'error': 'Name and email cannot be empty'}), 400

        # Добавить пользователя
        user_id = db.add_user(name, email)

        if user_id:
            return jsonify({
                'message': 'User created successfully',
                'id': user_id,
                'name': name,
                'email': email
            }), 201
        else:
            return jsonify({'error': 'Email already exists'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Тест пользователи при первом запуске
    users = db.get_all_users()
    if len(users) == 0:
        db.add_user('Иван Иванов', 'ivan@example.com')
        db.add_user('Мария Петрова', 'maria@example.com')
        db.add_user('Алексей Сидоров', 'alexey@example.com')
        print('Тестовые пользователи добавлены')

    app.run(debug=True, port=5000)
