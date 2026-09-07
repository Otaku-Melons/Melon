class MultipleParsersDeniedForCommand(Exception):
	"""Исключение: команде запрещено использование нескольких парсеров."""

	def __init__(self, command_name: str):
		"""
		Исключение: команде запрещено использование нескольких парсеров.

		:param command_name: Название команды.
		:type command_name: str
		"""

		super().__init__(command_name) 