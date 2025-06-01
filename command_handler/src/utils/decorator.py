from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec
from typedefs.models import ApiProxyResponse

P = ParamSpec("P")
R = TypeVar("R", bound=ApiProxyResponse[Any])


def discord_command(
    func: Callable[P, R],
) -> Callable[P, dict[str, Any]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        response = func(*args, **kwargs)
        return response.to_dict()

    return wrapper
