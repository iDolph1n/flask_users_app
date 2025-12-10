from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.user_service import UserService
from app.schemas.user_schema import (
    UserSchema,
    UserCreateSchema,
    UserUpdateSchema,
    PaginationSchema
)
from app.utils.exceptions import AppException

# Blueprint
bp = Blueprint('users', __name__, url_prefix='/api/users')

# Схемы
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
pagination_schema = PaginationSchema()


@bp.route('', methods=['GET'])
def get_users():
    """
    GET /api/users
    Query params: page, per_page, search
    """
    try:
        # Валидация параметров
        params = pagination_schema.load(request.args)

        # Получаем данные
        users, metadata = UserService.get_all_users(
            page=params['page'],
            per_page=params['per_page'],
            search=params.get('search')
        )

        return jsonify({
            'success': True,
            'data': users_schema.dump(users),
            'metadata': metadata
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Ошибка валидации параметров',
            'details': e.messages
        }), 400
    except AppException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """GET /api/users/<int:user_id>"""
    try:
        user = UserService.get_user_by_id(user_id)
        return jsonify({
            'success': True,
            'data': user_schema.dump(user)
        }), 200

    except AppException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route('', methods=['POST'])
def create_user():
    """POST /api/users"""
    try:
        # Валидация входных данных
        data = user_create_schema.load(request.get_json())

        # Создание
        user = UserService.create_user(
            name=data['name'],
            email=data['email']
        )

        return jsonify({
            'success': True,
            'message': 'Пользователь успешно создан',
            'data': user_schema.dump(user)
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Ошибка валидации',
            'details': e.messages
        }), 400
    except AppException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """PUT /api/users/<id>"""
    try:
        data = user_update_schema.load(request.get_json() or {})

        if not data:
            return jsonify({
                'success': False,
                'error': 'Нет данных для обновления'
            }), 400

        user = UserService.update_user(user_id, **data)

        return jsonify({
            'success': True,
            'message': 'Пользователь обновлён',
            'data': user_schema.dump(user)
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Ошибка валидации',
            'details': e.messages
        }), 400
    except AppException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """DELETE /api/users/<id>?soft=true"""
    try:
        soft = request.args.get('soft', 'true').lower() == 'true'
        UserService.delete_user(user_id, soft_delete=soft)

        return jsonify({
            'success': True,
            'message': 'Пользователь удалён'
        }), 200

    except AppException as e:
        return jsonify(e.to_dict()), e.status_code
