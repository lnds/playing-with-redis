from dataclasses import dataclass
import dataclasses
from datetime import datetime, timedelta
import time
import json
import typing
from redis import StrictRedis
from typing import Union, Optional
import uuid
from users import User

LIFETIME=10

@dataclass
class Message:
    id: str
    subject: str
    body: str
    timestamp: int

def message_key(user: User, message: Union[Message, str]) -> str:
    if isinstance(message, Message):
        return f"usr:{user.id}:msg:{message.id}"
    return f"usr:{user.id}:message:{message}"

def unread_key(user: User):
    return f"unread:{user.id}"

def read_key(user: User):
    return f"read:{user.id}"    


def create_message(subject: str, body: str) -> Message:
    return Message(id=str(uuid.uuid4()), subject=subject, body=body, timestamp=time.time())


def send_message(redis: StrictRedis, user: User, message: Message) -> int:
    mkey = message_key(user, message)
    message_dict = dataclasses.asdict(message)
    redis.setex(mkey, timedelta(minutes=LIFETIME), value=json.dumps(message_dict))
    ukey = unread_key(user)
    redis.zadd(ukey, {mkey: message.timestamp})
    return redis.zcount(ukey, 0, message.timestamp+1)


def read_message(redis: StrictRedis, user: User, message_id: str) -> Optional[Message]:
    mkey = message_key(user, message_id)
    message = json.loads(redis.get(mkey))
    if message:
        ukey = unread_key(user)
        redis.zremrangebyscore(ukey, message.timestamp, message.timestamp)
        rkey = read_key(user)
        redis.zadd(rkey, message.timestamp, mkey)
    return message


def get_unread_messages(redis: StrictRedis, user: User) -> list[Message]:
    ukey = unread_key(user)
    return __get_messages_from(redis, ukey)

def get_read_messages(redis: StrictRedis, user: User) -> list[Message]:
    rkey = read_key(user)
    return __get_messages_from(redis, rkey)


def __get_messages_from(redis, key) -> list[Message]:
    result = []
    for mkey in redis.zrange(key, 0, -1, desc=True, withscores=False):
        message = redis.get(mkey)
        if message:
            result.append(json.loads(message))
        else:
            redis.zrem(key, mkey) # clean unexistent message (evicted by ttl perhaps)
    return result    
