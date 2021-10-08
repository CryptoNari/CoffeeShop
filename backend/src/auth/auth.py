import json
from os import abort
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fseduc.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
    Verify/Validate Request Header 
    RETURNS:
        JWT token
'''
def get_token_auth_header():
    # Check if Authorization Header is present
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'autorization_header_missing',
            'description': 'Autorization header is expected'
        }, 401)
    
    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    # Check if Header is malformed
    if len(header_parts) != 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Autorization header is invalid/malformed'
        }, 401)
    elif header_parts[0].lower() == 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Autorization header is no bearer token'
        }, 401)

    return header_parts[1]


'''
    Check User/token permissions 
    INPUTS:
        permissions: Needed Route permissions
        payload: decoded token 
    RETURNS:
        True/False
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_payload',
            'description': 'No Permissions included in token'
        }, 401)
    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'not_authorized',
            'description': 'Permission not included in token'
        }, 403)

    return True

'''
    Implement verify_decode_jwt(token) method
    INPUTS:
        token: Valid bearer token
    RETURNS:
        payload: decoded token
'''
def verify_decode_jwt(token):
    # Request Auth0 Public key
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    # Get data from token Header
    unverified_header = jwt.get_unverified_header(token)

    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


'''
    Implement @requires_auth(permission) decorator method
    INPUTS:
        permission: string permission (i.e. 'post:drink')
    RETURNS:
    Decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator