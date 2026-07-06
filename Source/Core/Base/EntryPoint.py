from .SourceOperator import BaseSourceOperator

from Source.Core.Base.Formats.Components.Functions import SafelyReadTitleJSON
from Source.Core.Base.Parsers.Components.Manifest import ContentTypes
from Source.Core.Base.Parsers.Components import ParserSettings

from dataclasses import dataclass
from typing import TYPE_CHECKING
import importlib

from dulwich import errors, porcelain

if TYPE_CHECKING:
	from Source.Core.Base.Parsers.Components import ParserManifest
	from Source.Core.SystemObjects.Temper import SharedData
	from Source.Core.SystemObjects.Printer import Portals
	from Source.Core.SystemObjects import SystemObjects

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class FileTypingResult:
	"""Результат определения типа файла тайтла."""

	slug: str
	content_type: ContentTypes

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseEntryPoint:
	"""Базовая точка входа в модуль парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def manifest(self) -> "ParserManifest":
		"""Манифест парсера."""

		return self._Manifest

	@property
	def parser_name(self) -> str:
		"""Имя парсера."""

		return self._Manifest.parser_name

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._Portals

	@property
	def settings(self) -> ParserSettings:
		"""Настройки парсера."""

		return self._ParserSettings

	@property
	def shared_data(self) -> "SharedData":
		"""Разделяемые в контексте сессий одного парсера данные."""
		
		return self._SharedData

	@property
	def source_operator(self) -> BaseSourceOperator:
		"""Оператор источника."""

		return self._SourceOperator

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self._SystemObjects

	@property
	def version(self) -> str | None:
		"""Версия парсера."""

		try:
			ParserTags = porcelain.tag_list(f"Parsers/{self._Manifest.parser_name}")
		except errors.NotGitRepository:
			return None
		
		if ParserTags:
			return ParserTags[-1].decode().lstrip("v")
		
		return None

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects", manifest: "ParserManifest"):
		"""
		Базовая точка входа в модуль парсера.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param manifest: Манифест парсера.
		:type manifest: ParserManifest
		:param settings: Настройки парсера.
		:type settings: ParserSettings
		"""

		self._SystemObjects = system_objects
		self._Manifest = manifest
		self._SharedData = self._SystemObjects.temper.load_parser_shared_data(self._Manifest.parser_name)
		self._Portals = self._SystemObjects.printer.get_parser_portals(self._Manifest.parser_name)

		Module = importlib.import_module(f"Parsers.{self._Manifest.parser_name}.main")

		self._ParserSettings = ParserSettings(self._Manifest.parser_name)
		self._SourceOperator: BaseSourceOperator = Module.SourceOperator(self)

		self._PostInitMethod()

	def get_content_type_by_file(self, filename: str) -> FileTypingResult:
		"""
		Определяет тип контента по файлу.

		:param filename: Имя файла с расширением или без него.
		:type filename: str
		:return: Результат определения типа файла тайтла.
		:rtype: FileTypingResult
		"""

		if not filename.endswith(".json"):
			filename += ".json"

		FilePath = self.settings.directories.titles / filename
		TitleData = SafelyReadTitleJSON(FilePath)
		Type: str = TitleData["format"]
		TypeName: str = Type.split("-")[1]
		
		return FileTypingResult(TitleData["slug"], ContentTypes(TypeName))