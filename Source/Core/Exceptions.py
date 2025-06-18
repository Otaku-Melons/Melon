from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
	
class ParsingError(Exception):
	"""Исключение: ошибка парсинга."""

	def __init__(self):
		"""Исключение: ошибка парсинга."""

		self.__Message = "Unable to get data."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message

class TitleNotFound(Exception):
	"""Исключение: тайтл не найден в источнике."""

	def __init__(self, title: "BaseTitle"):
		"""
		Исключение: тайтл не найден в источнике.
			title – данные тайтла.
		"""

		self.__Message = f"Title \"{title.slug}\" not found."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message
	
class UnsupportedFormat(Exception):
	"""Исключение: неподдерживаемый формат JSON."""

	def __init__(self, format: str | None = None):
		"""
		Исключение: неподдерживаемый формат JSON.

		:param format: Название формата.
		:type format: str | None, optional
		"""

		format = f" \"{format}\"" if format else ""
		self.__Message = f"Unsupported format{format}."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ФОРМАТИРОВЩИКОВ КОНТЕНТА <<<<< #
#==========================================================================================#
	
class UnresolvedTag(Exception):
	"""Исключение: неразрешённый тег."""

	def __init__(self, tag: str):
		"""
		Исключение: неразрешённый тег.

		:param tag: Имя тега.
		:type tag: str
		"""

		self.__Message = f"Unresolved tag \"{tag}\"."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message
	
#==========================================================================================#
# >>>>> СИСТЕМНЫЕ ИСКЛЮЧЕНИЯ <<<<< #
#==========================================================================================#

class TempOwnerNotSpecified(Exception):
	"""Исключение: владалец временного каталога не определён."""

	def __init__(self):
		"""Исключение: неразрешённый тег."""

		self.__Message = f"Parser or extension not specified for temper. Unable to load directory."
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message