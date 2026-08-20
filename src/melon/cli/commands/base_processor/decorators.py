from functools import wraps
from typing import Any, Callable

from ....core import exceptions

def catch_base_exceptions(method: Callable[..., Any]) -> Callable[..., Any]:
	"""
	Декоратор: отлавливает базовые исключения.

	:param method: Метод.
	:type method: Callable[..., Any]
	:return: Обёрнутый в декоратор метод.
	:rtype: Callable[..., Any]
	"""

	@wraps(method)
	def wrapper(*args: Any, **kwargs: Any) -> Any:
		try:
			return method(*args, **kwargs)
		except exceptions.system.ParserNotFound:
			return False

	return wrapper