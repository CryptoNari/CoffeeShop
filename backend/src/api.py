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
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods={'GET'})
def retrieve_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    drinks_short = [drink.short() for drink in drinks]

    results = {
        'success': True,
        'drinks': drinks_short
    }

    return jsonify(results)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods={'GET'})
def retrieve_drink_detail():
    drinks = Drink.query.order_by(Drink.id).all()
    drinks_long = [drink.long() for drink in drinks]

    results = {
        'success': True,
        'drinks': drinks_long
    }

    return jsonify(results)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods={'POST'})
def create_drink():
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    drink = Drink(
        title=new_title,
        recipe=new_recipe
        )

    drink.insert()

    results = {
        'success': True,
        'drinks': drink.long()
    }

    return jsonify(results)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods={'PATCH'})
def update_drink(drink_id):
    body = request.get_json()
    patch_title = body.get('title', None)
    patch_recipe = body.get('recipe', None)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    drink.title = patch_title
    drink.recipe = patch_recipe
    drink.update()

    results = {
        'success': True,
        'drinks': drink.long()
    }

    return jsonify(results)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods={'DELETE'})
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        drink.delete()
        results = {
            'success': True,
            'delete': drink_id
        }
    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify(results)


# Error Handling
'''
Example error handling for unprocessable entity
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

