from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.Methods.Filesystem import NormalizePath

import os

class Temper:
	"""Дескриптор каталога временных файлов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def builder_temp(self) -> str:
		"""Путь к выделенному для сборки контента каталогу временных файлов."""

		return self.get_builder_temp()

	@property
	def extension_temp(self) -> str:
		"""Путь к выделенному для конкретного расширения каталогу временных файлов."""

		return self.get_extension_temp()

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
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Дескриптор каталога временных файлов."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Temp = "Temp"
		self.__Extension = None
		self.__ParserName = None

	def clear_parser_temp(self, parser_name: str | None = None):
		"""
		Очищает выделенный для конкретного парсера каталог временных файлов.
			parser_name – название парсера.
		"""

		if not parser_name: parser_name = self.__ParserName
		Path = f"{self.__Temp}/{parser_name}"
		if os.path.exists(Path): RemoveDirectoryContent(Path)

	def get_builder_temp(self, parser_name: str | None = None) -> str:
		"""
		Возвращает путь к выделенному для сборки контента каталогу временных файлов.
			parser_name – имя парсера.
		"""

		if not parser_name: parser_name = self.__ParserName
		ParserTemp = self.get_parser_temp(parser_name)
		Path = f"{ParserTemp}/build"
		if not os.path.exists(Path): os.makedirs(Path)
		Path = NormalizePath(Path)
		
		return Path

	def get_parser_temp(self, parser_name: str | None = None) -> str:
		"""
		Возвращает путь к выделенному для конкретного парсера каталогу временных файлов.
			parser_name – имя парсера.
		"""

		if not parser_name: parser_name = self.__ParserName
		Path = f"{self.__Temp}/{parser_name}"
		if not os.path.exists(Path): os.makedirs(Path)
		Path = NormalizePath(Path)

		return Path
	
	def get_extension_temp(self, parser_name: str | None = None, extension: str | None = None) -> str:
		"""
		Возвращает путь к выделенному для конкретного расшриения каталогу временных файлов.
			parser_name – имя парсера;\n
			extension – расширение.
		"""

		if not parser_name: parser_name = self.__ParserName
		if not extension: extension = self.__Extension
		ParserTemp = self.get_parser_temp(parser_name)
		Path = f"{ParserTemp}/extensions/{extension}"
		if not os.path.exists(Path): os.makedirs(Path)
		Path = NormalizePath(Path)
		
		return Path
	
	def select_extension(self, extension: str):
		"""Задаёт имя используемого расширения."""

		self.__Extension = extension

	def select_parser(self, parser_name: str):
		"""Задаёт имя используемого парсера."""

		self.__ParserName = parser_name