from typing import override

from ..base_format.controller import BaseTitleController
from .data import TitleData

class Ranobe(BaseTitleController[TitleData]):
	"""Контроллер тайтла."""

	@override
	def _export_data_type(self) -> type[TitleData]:
		"""
		Экспортирует тип данных тайтла.

		:return: Тип данных тайтла.
		:rtype: type[TitleData]
		"""

		return TitleData