from typing import Literal, override

from ..base_format.data import BaseTitleData, ExtraField
from .chapter import Chapter
from .enums import Types

class TitleData(BaseTitleData[Chapter]):
	"""Данные тайтла."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def format(self) -> Literal["melon-manga"]:
		"""Формат данных."""

		return "melon-manga"

	@property
	def title_type(self) -> Types | None:
		"""Тип тайтла."""

		TypeValue = self._data.get("type")
		if TypeValue:
			return Types(TypeValue)
		
		return None

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@override
	def _export_chapter_type(self) -> type[Chapter]:
		"""
		Экспортирует тип главы.

		:return: Тип главы.
		:rtype: type[Chapter]
		"""

		return Chapter

	@override
	def _export_extra_fields(self) -> tuple[ExtraField, ...]:
		"""
		Экспортирует последовательность дополнительных корневых полей данных.

		:return: Последовательность дополнительных корневых полей данных.
		:rtype: tuple[ExtraField, ...]
		"""

		manga_type = ExtraField(
			after_key = "slug",
			name = "type",
			value = None
		)

		return (manga_type,)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_title_type(self, title_type: Types | None):
		"""
		Задаёт тип тайтла.

		:param title_type: Тип тайтла.
		:type title_type: Types | None
		"""

		self._data["type"] = title_type.value if title_type else None