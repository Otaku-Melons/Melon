from Source.Core.Objects import Objects

import os

class Collector:
	"""Менеджер коллекций."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadCollection(self) -> list[str]:
		"""Читает коллекцию."""

		# Коллекция.
		Collection = list()
		
		# Если файл коллекции существует и не включён режим перезаписи.
		if os.path.exists(self.__Path) and not self.__SystemObjects.FORCE_MODE:
			
			# Открытие потока чтения.
			with open(self.__Path, "r") as FileReader:
				# Буфер чтения.
				Buffer = FileReader.read().split("\n")

				# Для каждой строки.
				for Line in Buffer:
					# Очистка краевых символов.
					Line = Line.strip()
					# Если строка не пустая, добавить её в список алиасов.
					if Line: Collection.append(Line)

		return Collection

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: Objects, parser_name: str):
		"""
		Менеджер коллекций.
			system_objects – коллекция системных объектов;
			parser_name – название парсера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects
		# Путь к файлу коллекции.
		self.__Path = f"Parsers/{parser_name}/Collection.txt"
		# Коллекция алиасов.
		self.__Collection = self.__ReadCollection()

	def append(self, slugs: list[str]):
		"""
		Добавляет в коллекцию список алиасов.
			slugs – список алиасов.
		"""

		# Добавление алиасов.
		self.__Collection += slugs

	def save(self):
		"""Сохраняет коллекцию."""

		# Фильтрация дублей методом конвертации в набор.
		self.__Collection = list(set(self.__Collection))

		# Открытие потока записи.
		with open(self.__Path, "w") as FileWriter:
			# Для каждого алиаса.
			for Slug in self.__Collection: FileWriter.write(Slug + "\n")

		