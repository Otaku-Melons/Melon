from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.Methods.Filesystem import NormalizePath

import os

class Temper:
	"""Дескриптор каталога временных файлов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def parser_temp(self) -> str:
		"""Путь к выделенному для конкретного парсера каталогу временных файлов."""

		return self.get_parser_temp()

	@property
	def path(self) -> list[str]:
		"""Путь к корню каталога временных файлов."""

		if not os.path.exists(self.__Temp): os.makedirs(self.__Temp)

		return self.__Temp

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Дескриптор каталога временных файлов."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Temp = "Temp"
		self.__ParserName = None

	def clear_parser_temp(self, parser_name: str | None = None):
		"""
		Очищает выделенный для конкретного парсера каталог временных файлов.
			parser_name – название парсера.
		"""

		if not parser_name: parser_name = self.__ParserName
		Path = f"{self.__Temp}/{parser_name}"
		if os.path.exists(Path): RemoveDirectoryContent(Path)

	def get_parser_temp(self, parser_name: str | None = None) -> str:
		"""
		Возвращает путь к выделенному для конкретного парсера каталогу временных файлов.
			parser_name – название парсера.
		"""

		if not parser_name: parser_name = self.__ParserName
		Path = f"{self.__Temp}/{parser_name}"
		if not os.path.exists(Path): os.makedirs(Path)
		Path = NormalizePath(Path)
		
		return Path
	
	def select_parser(self, parser_name: str):
		"""Задаёт имя используемого парсера."""

		self.__ParserName = parser_name