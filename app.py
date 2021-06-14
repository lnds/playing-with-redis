from flask import Flask
from redis import StrictRedis
from flask_restful import reqparse, fields, marshal_with, Resource, Api
import json

app = Flask(__name__)
redis = StrictRedis('redis', port=6379, charset='utf-8', decode_responses=True)
api = Api(app)

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', dest='id', required=True, type=str)
user_parser.add_argument('name', type=str, required=True)

user_fields = {
        'id': fields.String,
        'name': fields.String,
}

class Users(Resource):

    def get(self):
        users =  redis.hgetall('users')
        users = [ {k : json.loads(users[k]) } for k in users.keys()]
        return users, 201

    def post(self):
        args = user_parser.parse_args()
        app.logger.info('ARGS=%s', args)
        id = args['id']
        user = json.dumps({'id': args['id'], 'name': args['name']})
        app.logger.info("USER=%s", user)
        redis.hset("users", id, user)
        return user, 201

class User(Resource):

    def get(self, id):
        user = redis.hget('users', id)
        if user:
            return json.loads(user), 201
        return 'not-found', 404

    def delete(self, id):
        n = redis.hdel('users', id)
        if n == 0:
            return 'not-found', 404
        return id, 201

api.add_resource(Users, '/users')
api.add_resource(User, '/users/<id>')

@app.route('/')
def hello():
    redis.incr('hits')
    return "Hello visitor #{}".format(redis.get('hits').decode('utf-8'))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)