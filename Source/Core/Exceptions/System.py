class BadManifest(Exception):
	"""Исключение: неверное определение манифеста."""

	def __init__(self, message: str):
		"""
		Исключение: неверное определение манифеста.

		:param message: Сообщение об ошибке.
		:type message: str
		"""

		super().__init__(message)


class ParserAlreadyExists(Exception):
	"""Исключение: парсер уже существует."""

	def __init__(self, parser_name: str):
		"""
		Исключение: парсер уже существует.

		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		super().__init__(parser_name) 

class ParserNotFound(Exception):
	"""Исключение: парсер не найден."""

	def __init__(self, parser_name: str):
		"""
		Исключение: парсер не найден.

		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		super().__init__(parser_name) 