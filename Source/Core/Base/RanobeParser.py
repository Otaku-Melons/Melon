from Source.Core.Formats.Ranobe import Chapter, Branch, Ranobe
from .BaseParser import *

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

TYPE = Ranobe

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class RanobeParser(BaseParser):
	"""Базовый парсер ранобэ."""

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects, title: Ranobe | None = None):
		"""
		Базовый парсер манги.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self._SystemObjects = system_objects
		self._Title = title

		self._Temper = self._SystemObjects.temper
		self._Portals = self._SystemObjects.logger.portals
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

	def set_title(self, title: Ranobe):
		"""
		Задаёт данные тайтла.
			title – данные тайтла.
		"""

		self._Title = title