from Source.Core.SystemObjects import SystemObjects

import os

class Collector:
	"""Менеджер коллекций."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadCollection(self) -> list[str]:
		"""Читает коллекцию."""

		Collection = list()
		
		if os.path.exists(self.__Path) and not self.__SystemObjects.FORCE_MODE:
			
			with open(self.__Path, "r") as FileReader:
				Buffer = FileReader.read().split("\n")

				for Line in Buffer:
					Line = Line.strip()
					if Line: Collection.append(Line)

		return Collection

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects):
		"""
		Менеджер коллекций.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__SystemObjects = system_objects
		self.__Path = system_objects.temper.get_parser_temp() + "/Collection.txt"
		self.__Collection = self.__ReadCollection()

	def append(self, slugs: list[str]):
		"""
		Добавляет в коллекцию список алиасов.
			slugs – список алиасов.
		"""

		self.__SystemObjects.logger.titles_collected(len(slugs))
		self.__Collection += slugs

	def save(self, sort: bool = False):
		"""
		Сохраняет коллекцию.
			sort – указывает, нужно ли сортировать алиасы в алфавитном порядке.
		"""

		self.__Collection = list(set(self.__Collection))
		if sort: self.__Collection = sorted(self.__Collection)

		with open(self.__Path, "w") as FileWriter:
			for Slug in self.__Collection: FileWriter.write(Slug + "\n")