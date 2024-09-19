from Source.Core.Formats import BaseTitle

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПАРСЕРОВ <<<<< #
#==========================================================================================#

class BadSettings(Exception):
	"""Исключение: неверно определены настройки парсера."""

	def __init__(self, parser_name: str):
		"""
		Исключение: неверно определены настройки парсера.
			parser_name – название парсера.
		"""

		# Добавление данных в сообщение об ошибке.
		self.__Message = f"Error during parsing \"{parser_name}\" settings."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message

class TitleNotFound(Exception):
	"""Исключение: тайтл не найден в источнике."""

	def __init__(self, title: BaseTitle):
		"""
		Исключение: тайтл не найден в источнике.
			title – данные тайтла.
		"""

		# Добавление данных в сообщение об ошибке.
		self.__Message = f"Title \"{title.slug}\" not found."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message