from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

from typedefs.models import ApiProxyResponse
from logging import getLogger

P = ParamSpec("P")
R = TypeVar("R", bound=ApiProxyResponse[Any])

logger = getLogger(__name__)


def discord_command(
    func: Callable[P, R],
) -> Callable[P, dict[str, Any]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        response = func(*args, **kwargs)
        logger.info(f"{response=}")
        return response.to_dict()

    return wrapper
