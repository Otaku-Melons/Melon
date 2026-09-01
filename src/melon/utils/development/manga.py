from ...core.base.formats.base_format.branch import Branch
from ...core.base.formats.manga.chapter import Chapter
from ...core.base.parsers.base_manga_parser import BaseMangaParser

class Parser(BaseMangaParser):
	"""Парсер."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _Amend(self, branch: Branch, chapter: Chapter) -> str | None:
		"""
		Дополняет главу дайными о контенте.

		:param branch: Ветвь.
		:type branch: Branch
		:param chapter: Глава.
		:type chapter: Chapter
		:return: Дополнительное необязательное сообщение о дополнении.
		:rtype: str | None
		"""

		pass

	def _Parse(self):
		"""Получает основные данные тайтла."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _PreSaver(self):
		"""Запускается непосредственно перед сохранением тайтла."""

		pass
