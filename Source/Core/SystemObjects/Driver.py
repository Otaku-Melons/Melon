from Source.Core.Base.Parsers.Components import ParserManifest
from Source.Core.Base.EntryPoint import BaseEntryPoint

from dublib.Methods.Filesystem import ListDir

from typing import TYPE_CHECKING
from pathlib import Path
import importlib

if TYPE_CHECKING:
	from Source.Core.SystemObjects import SystemObjects

class Driver:
	"""Драйвер парсеров."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def parsers_names(self) -> tuple[str, ...]:
		"""Последовательность названий всех установленных парсеров."""

		# To-Do: проверка каталогов на соответствие парсерной структуре?
		return tuple(ListDir("Parsers"))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Драйвер парсеров.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""

		self.__SystemObjects = system_objects

	def get_entry_point(self, parser_name: str) -> BaseEntryPoint:
		"""
		Инициализирует точку входа для указанного парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Точка входа в модуль парсера.
		:rtype: BaseEntryPoint
		:raises FileNotFoundError: Файл точки входа в парсер не найден.
		"""

		ParserMainPath = Path(f"Parsers/{parser_name}/main.py")
		if not ParserMainPath.exists():
			raise FileNotFoundError(ParserMainPath)

		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		ParserManifest = self.load_parser_manifest(parser_name)

		EntryPoint = BaseEntryPoint(self.__SystemObjects, ParserManifest)
		if hasattr(Module, "EntryPoint"): EntryPoint = Module.EntryPoint(self.__SystemObjects, ParserManifest)

		return EntryPoint
	
	def load_parser_manifest(self, parser_name: str) -> ParserManifest:
		"""
		Загружает манифест парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Манифест парсера.
		:rtype: ParserManifest
		:raises FileNotFoundError: Файл манифеста не найден.
		"""

		ManifestPath = Path(f"Parsers/{parser_name}/manifest.json")
		if not ManifestPath.exists():
			raise FileNotFoundError(ManifestPath)
		
		return ParserManifest(self.__SystemObjects, parser_name)