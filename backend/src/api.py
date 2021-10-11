from logging import ERROR
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
    Endpoint GET /drinks
'''


@app.route('/drinks', methods={'GET'})
def retrieve_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_short = [drink.short() for drink in drinks]

        results = {
            'success': True,
            'drinks': drinks_short
        }
    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify(results)


'''
    Endpoint GET /drinks-detail
'''


@app.route('/drinks-detail', methods={'GET'})
@requires_auth('get:drinks-detail')
def retrieve_drink_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_long = [drink.long() for drink in drinks]

        results = {
            'success': True,
            'drinks': drinks_long
        }
    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify(results)


'''
    Endpoint POST /drinks
'''


@app.route('/drinks', methods={'POST'})
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        body = request.get_json()
        if 'title' in body and 'recipe' in body:
            new_title = body.get('title')
            new_recipe = body.get('recipe')
        else:
            abort(400)

        drink_check = (
            Drink.query
            .filter(Drink.title == new_title)
            .one_or_none()
        )

        if drink_check:
            raise AuthError({
                'code': 'invalid_title',
                'description': 'Drink title is already in use'
            }, 422)
        else:
            drink = Drink(
                title=new_title,
                recipe=json.dumps([new_recipe])
                )

            drink.insert()

            results = {
                'success': True,
                'drinks': [drink.long()]
            }
    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify(results)


'''
    Endpoint PATCH /drinks/<drink_id>
        <drink_id> is the existing Drink id
'''


@app.route('/drinks/<drink_id>', methods={'PATCH'})
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        drink = (
            Drink.query
            .filter(Drink.id == drink_id)
            .one_or_none()
        )
        # ID not found
        if drink is None:
            abort(404)

        # Update Drink
        body = request.get_json()
        if 'title' in body:
            drink.title = body.get('title')
        if 'recipe' in body:
            drink.recipe = json.dumps([body.get('recipe')])

        drink.update()

        results = {
            'success': True,
            'drinks': [drink.long()]
        }

    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify(results)


'''
    Endpoint DELETE /drinks/<drink_id>
        <drink_id> is the existing Drink id
'''


@app.route('/drinks/<drink_id>', methods={'DELETE'})
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        # ID not found
        if drink is None:
            abort(404)
        # Delete ID
        drink.delete()
        results = {
            'success': True,
            'delete': drink_id
        }
    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify(results)


'''
Error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def server_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.description
    }), error.status_code
