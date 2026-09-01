from ...core.base.formats.ranobe_old import Branch, Chapter
from ...core.base.parsers.base_ranobe_parser import BaseRanobeParser

class Parser(BaseRanobeParser):
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
