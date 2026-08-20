from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...core.base.formats.base_format import BaseTitle
	from ...core.base.parsers.components.manifest import ContentTypes

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПАРСЕРОВ <<<<< #
#==========================================================================================#
	
class AuthorizationRequired(Exception):
	"""Исключение: требуется авторизация."""

	def __init__(self, message: str):
		"""
		Исключение: требуется авторизация.

		:param message: Описание требования авторизации.
		:type message: str
		"""

		super().__init__(message) 

class ChapterNotFound(Exception):
	"""Исключение: глава не найдена."""

	def __init__(self, chapter_id: int | None = None, slug: str | None = None):
		"""
		Исключение: глава не найдена.

		:param chapter_id: ID главы.
		:type id: int | None
		:param slug: Алиас главы.
		:type slug: str | None
		"""

		ChapterIdentificator = ""

		if chapter_id:
			ChapterIdentificator = f" {chapter_id}"
		elif slug:
			ChapterIdentificator = f" \"{slug}\""

		super().__init__(f"Chapter{ChapterIdentificator} not found.") 

class ParsingError(Exception):
	"""Исключение: ошибка парсинга."""

	def __init__(self, description: str | None = None):
		"""
		Исключение: ошибка парсинга.

		:param description: Описание ошибки.
		:type description: str | None
		"""

		super().__init__(description or "Error occurs during parsing.") 

class TitleNotFound(Exception):
	"""Исключение: тайтл не найден."""

	def __init__(self, title: "BaseTitle"):
		"""
		Исключение: тайтл не найден.

		:param title: Тайтл.
		:type title: BaseTitle
		"""

		super().__init__(f"Title \"{title.slug}\" not found.") 

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

class UnsupportedFormat(Exception):
	"""Исключение: неподдерживаемый формат JSON."""

	def __init__(self, title_format: str | None = None):
		"""
		Исключение: неподдерживаемый формат JSON.

		:param title_format: Название формата.
		:type title_format: str | None
		"""

		title_format = f" \"{title_format}\"" if title_format else ""
		super().__init__(f"Unsupported format{title_format}.") 

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПАРСЕРОВ РАНОБЭ <<<<< #
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
