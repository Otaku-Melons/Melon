from dublib.Methods import ReadJSON

import importlib
import os

class ParsersManager:
	"""Менеджер парсеров."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def parsers_names(self) -> list[str]:
		"""Список названий доступных парсеров."""

		# Получение списка каталогов в директории парсеров.
		Parsers = os.listdir("Source/Parsers")
		# Удаление директории шаблонов.
		if "Templates" in Parsers: Parsers.remove("Templates")

		return Parsers

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер парсеров."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# 
		pass

	def get_parser_settings(self, parser_name: str) -> str:
		"""
		Возвращает словарь настроек парсера.
			parser_name – название парсера.
		"""

		return ReadJSON(f"Source/Parsers/{parser_name}/settings.json")

	def get_parser_site(self, parser_name: str) -> str:
		"""
		Возвращает поддерживаемый парсером сайт.
			parser_name – название парсера.
		"""

		# Импорт парсера.
		Module = importlib.import_module(f"Source.Parsers.{parser_name}.main")

		return Module.SITE

	def get_parser_struct(self, parser_name: str) -> str:
		"""
		Возвращает объектную структуру выходных данных парсера.
			parser_name – название парсера.
		"""

		# Импорт парсера.
		Module = importlib.import_module(f"Source.Parsers.{parser_name}.main")

		return Module.STRUCT

	def get_parser_version(self, parser_name: str) -> str:
		"""
		Возвращает версию парсера.
			parser_name – название парсера.
		"""

		# Импорт парсера.
		Module = importlib.import_module(f"Source.Parsers.{parser_name}.main")

		return Module.VERSION

	def launch(self, parser_name: str) -> any:
		"""
		Запускает парсер и возвращает его объект.
			parser_name – название парсера.
		"""

		# Инициализация парсера.
		Module = importlib.import_module(f"Source.Parsers.{parser_name}.main")
		Parser = Module.Parser()

		return Parser