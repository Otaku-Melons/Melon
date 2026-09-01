from ...parsers.components.words_dictionary import CheckLanguageCode
from ..base_format.data import BaseTitleData, ExtraField
from .chapter import Chapter

class TitleData(BaseTitleData[Chapter]):
	"""Данные тайтла."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def original_language(self) -> str | None:
		"""Оригинальный язык контента по стандарту ISO 639-3."""

		return self._data["original_language"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _export_chapter_type(self) -> type[Chapter]:
		"""
		Экспортирует тип главы.

		:return: Тип главы.
		:rtype: type[Chapter]
		"""

		return Chapter

	def _export_extra_fields(self) -> tuple[ExtraField, ...]:
		"""
		Экспортирует последовательность дополнительных корневых полей данных.

		:return: Последовательность дополнительных корневых полей данных.
		:rtype: tuple[ExtraField, ...]
		"""

		manga_type = ExtraField(
			after_key = "slug",
			name = "original_language",
			value = None
		)

		return (manga_type,)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_original_language(self, language_code: str | None):
		"""
		Задаёт оригинальный язык контента по стандарту ISO 639-3.

		:param language_code: Код языка.
		:type language_code: str | None
		:raise ValueError: Выбрасывается при несоответствии кода языка стандарту.
		"""

		if language_code: CheckLanguageCode(language_code)
		self._data["original_language"] = language_code.lower() if language_code else None