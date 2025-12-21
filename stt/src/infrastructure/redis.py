from typing import Any

from config import RedisConfig
from redis.asyncio import Redis


def new_redis_client(redis_config: RedisConfig) -> Redis[Any]:
    return Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        password=redis_config.password
    )