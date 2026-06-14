class TempOwnerNotSpecified(Exception):
	"""Исключение: владалец временного каталога не определён."""

	def __init__(self):
		"""Исключение: владалец временного каталога не определён."""

		super().__init__("Parser or extension not specified for temper. Unable to load directory.") 
	
class BadManifest(Exception):
	"""Исключение: неверное определение манифеста."""

	def __init__(self, message: str):
		"""
		Исключение: неверное определение манифеста.

		:param message: Сообщение об ошибке.
		:type message: str
		"""

		super().__init__(message) 