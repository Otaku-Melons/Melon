from Source.Core.Formats.Manga import Chapter, Branch, Manga
from .BaseParser import *

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

TYPE = Manga

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class MangaParser(BaseParser):
	"""Базовый парсер манги."""

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects, title: Manga | None = None):
		"""
		Базовый парсер манги.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._SystemObjects = system_objects
		self._Title = title

		self._Logger = self._SystemObjects.logger
		self._Settings = self._SystemObjects.manager.get_parser_settings()
		self._Requestor = self._InitializeRequestor()

		self._PostInitMethod()

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