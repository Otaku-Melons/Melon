from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Core.Base.Parsers.Components.Manifest import ContentTypes
	from Source.Core.Base.Formats.BaseFormat import BaseTitle

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПАРСЕРОВ <<<<< #
#==========================================================================================#
	
class ChapterNotFound(Exception):
	"""Исключение: глава не найдена."""

	def __init__(self, id: int | None = None, slug: str | None = None):
		"""
		Исключение: глава не найдена.

		:param id: ID главы.
		:type id: int | None
		:param slug: Алиас главы.
		:type slug: str | None
		"""

		ChapterIdentificator = ""

		if id:
			ChapterIdentificator = f" {id}"
		elif slug:
			ChapterIdentificator = f" \"{slug}\""

		super().__init__(f"Chapter{ChapterIdentificator} not found.") 

class TitleNotSetted(Exception):
	"""Исключение: не задан тайтл."""

	def __init__(self):
		"""Исключение: не задан тайтл."""

		super().__init__("Open title before using methods, that it requires.") 

class UnsupportedContent(Exception):
	"""Исключение: неподдерживаемый тип контента."""

	def __init__(self, content_type: "ContentTypes"):
		"""
		Исключение: неподдерживаемый тип контента.

		:param content_type: Тип контента.
		:type content_type: ContentTypes
		"""

		super().__init__(content_type.value) 









		

class AuthorizationRequired(Exception):
	"""Исключение: требуется авторизация."""

	def __init__(self, message: str):
		"""
		Исключение: требуется авторизация.

		:param message: Описание требования авторизации.
		:type message: str
		"""

		super().__init__(message) 

class BadEntryPoint(Exception):
	"""Исключение: ошибка точки входа."""

	def __init__(self, message: str | None):
		"""
		Исключение: ошибка точки входа.

		:param message: Текст альтернативного сообщения об ошибке.
		:type message: str | None
		"""

		if message: super().__init__(message) 
		else: super().__init__()

class BadSettings(Exception):
	"""Исключение: неверно определены настройки парсера."""

	def __init__(self, parser_name: str):
		"""
		Исключение: неверно определены настройки парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		super().__init__(f"Error during parsing \"{parser_name}\" settings.") 


	
class MergingError(Exception):
	"""Исключение: ошибка слияния контента."""

	def __init__(self, message: str | None = None):
		"""
		Исключение: ошибка слияния контента.

		:param message: Текст альтернативного сообщения об ошибке.
		:type message: str | None
		"""

		super().__init__(message or "Every chapter must have ID. Merging skipped.")

class ParsingError(Exception):
	"""Исключение: ошибка парсинга."""

	def __init__(self, description: str | None = None):
		"""
		Исключение: ошибка парсинга.

		:param description: Описание ошибки.
		:type description: str | None
		"""

		super().__init__(description or "Unable get data.") 

class TitleNotFound(Exception):
	"""Исключение: тайтл не найден в источнике."""

	def __init__(self, title: "BaseTitle"):
		"""
		Исключение: тайтл не найден в источнике.

		:param title: Данные тайтла.
		:type title: BaseTitle
		"""

		super().__init__(f"Title \"{title.slug}\" not found.") 
	
class UnsupportedFormat(Exception):
	"""Исключение: неподдерживаемый формат JSON."""

	def __init__(self, format: str | None = None):
		"""
		Исключение: неподдерживаемый формат JSON.

		:param format: Название формата.
		:type format: str | None
		"""

		format = f" \"{format}\"" if format else ""
		super().__init__(f"Unsupported format{format}.") 

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ФОРМАТИРОВЩИКОВ КОНТЕНТА <<<<< #
#==========================================================================================#
	
class FootnoteCompositionError(Exception):
	"""Исключение: ошибка композиции заметки."""

	def __init__(self, description: str):
		"""
		Исключение: ошибка композиции заметки.

		:param description: Описание ошибки.
		:type description: str
		"""

		super().__init__(description) 

class UnresolvedTag(Exception):
	"""Исключение: неразрешённый тег."""

	def __init__(self, tag: str):
		"""
		Исключение: неразрешённый тег.

		:param tag: Имя тега.
		:type tag: str
		"""

		super().__init__(f"Unresolved tag \"{tag}\".") 