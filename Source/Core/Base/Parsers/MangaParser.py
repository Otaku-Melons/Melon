from Source.Core.Base.Formats.Manga import Chapter, Branch, Manga
from .BaseParser import *

class MangaParser(BaseParser):
	"""Базовый парсер манги."""

	def __init__(self, system_objects: "SystemObjects", title: Manga | None = None):
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

	def set_title(self, title: Manga):
		"""
		Задаёт данные тайтла.
			title – данные тайтла.
		"""

		self._Title = title