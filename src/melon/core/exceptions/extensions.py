class ExtensionNotFound(Exception):
	"""Исключение: расширение не найдено."""

	def __init__(self, extension_name: str):
		"""
		Исключение: расширение не найдено.

		:param extension_name: Имя расширения.
		:type extension_name: str
		"""

		super().__init__(extension_name) 
