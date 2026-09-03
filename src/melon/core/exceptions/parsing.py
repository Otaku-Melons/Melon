from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..base.formats.base_format.data import BaseTitleData

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПРОЦЕССА ПАРСИНГА <<<<< #
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

	def __init__(self, title_data: "BaseTitleData"):
		"""
		Исключение: тайтл не найден.

		:param title: Данные тайтла..
		:type title: BaseTitleData
		"""

		super().__init__(f"Title \"{title_data.slug}\" not found.") 

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ ПРОЦЕССА ПАРСИНГА РАНОБЭ <<<<< #
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
