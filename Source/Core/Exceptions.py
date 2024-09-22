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

		self.__Message = f"Error during parsing \"{parser_name}\" settings."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message

class ChapterNotFound(Exception):
	"""Исключение: глава не найдена."""

	def __init__(self, chapter: int):
		"""
		Исключение: глава не найдена.
			chapter – идентификатор главы.
		"""

		self.__Message = f"Chapter {chapter} not found."
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

		self.__Message = f"Title \"{title.slug}\" not found."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message