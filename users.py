from dataclasses import dataclass
import dataclasses
import uuid
import json
from redis import StrictRedis
from typing import Optional, Union


@dataclass
class User:
    id: str
    name: str


def create_user(id: str, name: str) -> User:
    return User(id=id, name=name)

def store_user(redis: StrictRedis, user: User, as_dict=False) -> Union[User, dict]:
    user_dict = dataclasses.asdict(user)
    redis.hset("users", user.id, json.dumps(user_dict))
    if as_dict:
        return user_dict
    return user


def delete_user(redis: StrictRedis, user_id: str) -> bool:
    return redis.hdel("users", user_id) > 0


def get_user(redis: StrictRedis, user_id: str, as_dict=False) -> Optional[Union[User, dict]]:
    user = redis.hget('users', user_id)
    if user:
        if as_dict:
            return json.loads(user)
        return User(**json.loads(user))
    return None


def get_users(redis: StrictRedis, as_dict=False) -> list[Union[User, dict]]:
    users = redis.hgetall('users')
    if as_dict:
        return [ json.loads(users[k])  for k in users.keys()]
    return [ User(**json.loads(users[k]))  for k in users.keys()]