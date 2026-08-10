class BuildingError(Exception):
	"""Исключение: ошибка сборки контента."""

	def __init__(self, message: str):
		"""
		Исключение: ошибка сборки контента.

		:param message: Описание ошибки.
		:type message: str
		"""

		super().__init__(message) 