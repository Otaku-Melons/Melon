from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING

from dublib.Functions.Filesystem import ReadJSON

from Source.Core import Exceptions

if TYPE_CHECKING:
	from Source.Core.SystemObjects import SystemObjects

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ContentTypes(Enum):
	"""Перечисление типов контента."""

	Manga = "manga"
	Ranobe = "ranobe"

_BASE_MANIFEST: MappingProxyType = MappingProxyType({
	"domain": None,
	"content_types": [],
	"parent": None,
	"version": None,
	"melon_required_version": None
})

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ParserManifest:
	"""Манифест парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def parser_name(self) -> str:
		"""Имя парсера."""

		return self.__ParserName

	@property
	def original_domain(self) -> str:
		"""Оригинальный домен источника."""

		return self.__Data["domain"]

	@property
	def mirror(self) -> str | None:
		"""Домен зеркала."""

		return self.__Mirror

	@property
	def domain(self) -> str:
		"""Домен зеркала или источника."""

		return self.__Mirror or self.original_domain
	
	@property
	def content_types(self) -> tuple[ContentTypes, ...]:
		"""Типы поддерживаемого контента."""

		return tuple(ContentTypes(Value) for Value in self.__Data["content_types"])
	
	@property
	def parent_name(self) -> str | None:
		"""Имя родительского парсера."""

		return self.__Data["parent"]

	@property
	def melon_required_version(self) -> str | None:
		"""Требуемая версия Melon."""

		Version: str | None = self.__Data["melon_required_version"]

		if Version == "$from_parent" and self.parent_name:
			Version = self.__SystemObjects.driver.load_parser_manifest(self.parent_name).melon_required_version
		
		return Version

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Validate(self):
		"""
		Проверяет валидность манифеста.

		:raises BadManifest: Выбрасывается при ошибке валидации манифеста.
		"""
		
		for Key in _BASE_MANIFEST.keys():
			if Key not in self.__Data:
				raise Exceptions.System.BadManifest(f"Key \"{Key}\" not found.")

		if not self.__Data["domain"]:
			raise Exceptions.System.BadManifest("Domain must be specified.")

		if not self.__Data["content_types"]:
			raise Exceptions.System.BadManifest("Types must be specified.")
		for ContentType in self.__Data["content_types"]:
			if ContentType not in ("manga", "ranobe"):
				raise Exceptions.System.BadManifest(f"Unsupported content type \"{ContentType}\".")

		for Key in ("version", "melon_required_version"):
			if self.__Data[Key] == "$from_parent" and not self.__Data["parent"]:
				raise Exceptions.System.BadManifest("Parent must be specified if using \"$from_parent\".")

		if self.__Data["parent"] and self.__Data["parent"] not in self.__SystemObjects.driver.parsers_names:
			raise Exceptions.System.BadManifest("Parent \"" + self.__Data["parent"] + "\" not found.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects", parser_name: str):
		"""
		Манифест парсера.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param parser_name: Имя парсера.
		:type parser_name: str
		"""
		
		self.__SystemObjects = system_objects
		self.__ParserName = parser_name

		self.__Data = ReadJSON(f"Parsers/{self.__ParserName}/manifest.json")
		self.__Validate()

		self.__Mirror: str | None = None

	def set_mirror(self, mirror: str | None):
		"""
		Задаёт домен зеркала, подменяя его в манифесте. Не сохраняет изменения в файл.

		:param mirror: Домен.
		:type mirror: str | None
		"""

		self.__Mirror = mirror