from Source.Core.Base.Formats.Components.Structs import ContentTypes
from Source.Core.Base.Formats.Ranobe import Ranobe
from Source.Core.Base.Formats.Manga import Manga
from Source.Core.Exceptions import BadManifest

from dublib.Methods.Filesystem import ReadJSON

from types import MappingProxyType

from dulwich.contrib.release_robot import get_current_version, get_recent_tags

Manifest = MappingProxyType({
	"object": "parser",
	"site": None,
	"content_type": None,
	"melon_version": None
})

class ParserManifest:
	"""Манифест парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def content_struct(self) -> Manga | Ranobe:
		"""Структура, описывающая контент парсера."""

		return self.__ContentStructs[self.__Data["content_type"]]

	@property
	def latest_git_tag(self) -> str | None:
		"""Имя самого свежего тега Git."""

		LatestTag = None
		try: LatestTag = get_recent_tags(f"Parsers/{self.__ParserName}")[0][0]
		except (TypeError, IndexError): pass
		
		return LatestTag

	@property
	def name(self) -> str:
		"""Имя парсера."""

		return self.__ParserName
	
	@property
	def type(self) -> ContentTypes:
		"""Тип контента."""

		return self.__Data["content_type"]
	
	@property
	def site(self) -> str:
		"""Домен сайта."""

		return self.__Data["site"]

	@property
	def version(self) -> str | None:
		"""Версия парсера."""
		
		Version = None
		try: Version = get_current_version(f"Parsers/{self.__ParserName}")
		except TypeError: pass
		
		return Version

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Validate(self):
		"""Проверяет валидность манифеста."""
		
		for Key in Manifest.keys():
			if Key not in self.__Data.keys(): raise BadManifest(f"Key \"{Key}\" not found.")

		if self.__Data["object"] != "parser": raise BadManifest("Parser manifest required, not other object.")
		if not self.__Data["site"]: raise BadManifest("Site must be specified.")

		if not self.__Data["content_type"]: raise BadManifest("Type must be specified.")
		if self.__Data["content_type"] not in ("manga", "ranobe", "anime"): raise BadManifest("Unsupported content type.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, parser_name: str):
		"""
		Манифест парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		self.__ParserName = parser_name

		self.__ContentStructs = {
			ContentTypes.Manga: Manga,
			ContentTypes.Ranobe: Ranobe
		}

		self.__Data = ReadJSON(f"Parsers/{parser_name}/manifest.json")
		self.__Validate()

		self.__Data["content_type"] = ContentTypes(self.__Data["content_type"])