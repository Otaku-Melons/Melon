from Source.Core.Base.Formats.Ranobe import Chapter, Branch, Ranobe
from .BaseParser import *

class RanobeParser(BaseParser):
	"""Базовый парсер ранобэ."""

	def __init__(self, system_objects: "SystemObjects", title: Ranobe | None = None):
		"""
		Базовый парсер манги.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		super().__init__(system_objects, title)

	def amend(self, branch: Branch, chapter: Chapter):
		"""
		Дополняет главу дайными о слайдах.
			branch – данные ветви;\n
			chapter – данные главы.
		"""

		pass

	def set_title(self, title: Ranobe):
		"""
		Задаёт данные тайтла.
			title – данные тайтла.
		"""

		self._Title = title