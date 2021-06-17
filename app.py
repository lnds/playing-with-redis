from flask import Flask
from redis import StrictRedis
from flask_restful import reqparse, fields, marshal_with, Resource, Api
import json
from datetime import datetime
import users
import messages

app = Flask(__name__)
redis = StrictRedis('redis', port=6379, charset='utf-8', decode_responses=True)
api = Api(app)

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', type=str, required=True)
user_parser.add_argument('name', type=str, required=True)

class UsersResource(Resource):

    def get(self):
        return users.get_users(redis, as_dict=True), 201

    def post(self):
        args = user_parser.parse_args()
        user = users.create_user(args['id'], args['name'])
        return users.store_user(redis, user, as_dict=True), 201
        
class UserResource(Resource):

    def get(self, id):
        user = users.get_user(redis, id, as_dict=True)
        if not user:
            return 'not-foud', 404
        return user, 201

    def delete(self, id):
        if users.delete_user(redis, id):
            return id, 201
        return 'not-found', 404

api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/users/<id>')


notifications_parser = reqparse.RequestParser()
notifications_parser.add_argument('subject', type=str, required=True)
notifications_parser.add_argument('body', type=str, required=True)


class Send(Resource):

    def post(self, user_id):
        user = users.get_user(redis, user_id)
        if user is None:
            return 'no-user', 404

        args = notifications_parser.parse_args()
        message = messages.create_message(args['subject'], args['body'])
        return messages.send_message(redis, user, message), 201


api.add_resource(Send, '/messages/<user_id>/send')        


class Unread(Resource):

    def get(self, user_id):
        user = users.get_user(redis, user_id)
        if user is None:
            return 'no-user', 404
        return messages.get_unread_messages(redis, user), 201


api.add_resource(Unread, '/messages/<user_id>/unread')   

class Read(Resource):

    def get(self, user_id):
        user = users.get_user(redis, user_id)
        if user is None:
            return 'no-user', 404
        return messages.get_read_messages(redis, user), 201

api.add_resource(Read, '/messages/<user_id>/read')   

@app.route('/')
def hello():
    redis.incr('hits')
    return "Hello visitor #{}".format(redis.get('hits').decode('utf-8'))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)