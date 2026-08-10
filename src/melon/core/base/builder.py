import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...core.base.formats.base_format import BaseChapter, BaseTitle
	from ...core.base.parsers.base_parser import BaseParser

#==========================================================================================#
# >>>>> БАЗОВЫЙ СБОРЩИК <<<<< #
#==========================================================================================#

class BaseBuilder:
	"""Базовый сборщик."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenerateNameByTemplate(self, chapter: "BaseChapter", template: str) -> str:
		"""
		Генерирует название главы по шаблону. Если номер и имя главы не определены, в качестве названия будет использован ID.

		:param chapter: Глава.
		:type chapter: BaseChapter
		:return: Название главы.
		:rtype: str
		"""

		Replacements: dict[str, str] = {
			"ch_word": self._WordsDictionary.chapter.title() if self._WordsDictionary and self._WordsDictionary.chapter else "",
			"vol_word": self._WordsDictionary.volume.title() if self._WordsDictionary and self._WordsDictionary.volume else "",
			"id": str(chapter.id),
			"name": chapter.name or "",
			"ch_number": chapter.number or "",
			"vol_number": chapter.volume or "",
			"separator": ". " if chapter.name else ""
		}

		for Replacement in Replacements:
			Identificator: str = "{" + Replacement + "}"
			if Identificator in template:
				template = template.replace(Identificator, Replacements[Replacement])

			Pattern = "{" + f"if:{Replacement}:(.*)" + "}"
			Match = re.match(Pattern, template)
			Value =  Value = Match[0].split(":")[-1][:-1] if Match else ""
			template = re.sub(Pattern, Value, template)

		return template.strip()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, parser: "BaseParser", title: "BaseTitle"):
		"""
		Базовый сборщик.

		:param parser: Парсер.
		:type parser: BaseParser
		:param title: Тайтл.
		:type title: BaseTitle
		"""
		
		self._Parser = parser
		self._Title = title
		
		self._SystemObjects = self._Parser.source_operator.system_objects
		self._ParserSettings = self._Parser.settings
		self._Temper = self._SystemObjects.temper
		self._Printer = self._SystemObjects.printer

		self._Portals = parser.source_operator.entry_point.portals
		self._ParserTempDirectory = self._Temper.get_parser_temp_directory(self._Parser.manifest.parser_name)
		self._WordsDictionary = self._Parser.load_words_dictionary_preset(self._Title.content_language) if self._Title.content_language else None

		self._BuildSystem: str | None = None
		self._ChapterNameTemplate: str = "{ch_word} {ch_number}{if:name:. } {name}"
		self._VolumeNameTemplate: str = "{vol_word} {vol_number}"

		self._PostInitMethod()

	def set_chapter_name_template(self, template: str):
		"""
		Задаёт шаблон именования глав.

		:param template: Строковый шаблон, в котором подстроки `{number}` и `{name}` заменяются на номер и название главы соответственно.
		:type template: str
		"""

		self._ChapterNameTemplate = template

	def set_volume_name_template(self, template: str):
		"""
		Задаёт шаблон именования томов.

		:param template: Строковый шаблон, в котором подстрока `{number}` заменяется на номер тома.
		:type template: str
		"""

		self._VolumeNameTemplate = template