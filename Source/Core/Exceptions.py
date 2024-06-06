#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПАРСЕРОВ <<<<< #
#==========================================================================================#

class TitleNotFound(Exception):
	"""Исключение: тайтл не найден в источнике."""

	def __init__(self, slug: str):
		"""
		Исключение: тайтл не найден в источнике.
			slug – алиас.
		"""

		# Добавление данных в сообщение об ошибке.
		self.__Message = f"Title \"{slug}\" not found."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message