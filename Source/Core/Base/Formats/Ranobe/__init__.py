from typing import Any, Sequence, cast

from Source.Core.Base.Formats.BaseFormat import BaseBranch, BaseChapter, BaseTitle

from ...Parsers.Components.WordsDictionary import CheckLanguageCode
from .Elements import Blockquote, Header, Image, Paragraph
from .Enums import ChaptersTypes

#==========================================================================================#
# >>>>> ВНУТРЕННИЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Chapter(BaseChapter):
	"""Глава ранобэ."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def footnotes(self) -> tuple[str, ...]:
		"""Последовательность заметок."""

		return tuple(self._Data["footnotes"])

	@property
	def paragraphs(self) -> tuple[str, ...]:
		"""Последовательность абзацев."""

		return tuple(self._Data["paragraphs"])
	
	@property
	def type(self) -> ChaptersTypes | None:
		"""Тип главы."""

		return ChaptersTypes[self._Data["type"]]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _Clear(self):
		"""Очищает контент главы."""

		self._Data["paragraphs"] = []
		self._Data["footnotes"] = []

	def _IsEmpty(self) -> bool:
		"""
		Проверяет, пустая ли глава.

		:return: Состояние: пуста ли глава.
		:rtype: bool
		"""

		return not bool(self._Data["paragraphs"])

	def _FromDict(self, data: dict):
		"""
		Заполняет данные главы из словаря.

		:param data: Словарь данных главы.
		:type data: dict
		"""

		self._Data = self._Data | data

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Data["paragraphs"] = []
		self._Data["footnotes"] = []

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_element(self, element: "Paragraph | Image | Header | Blockquote"):
		"""
		Добавляет элемент в главу.

		:param element: Элемент главы.
		:type element: Paragraph | Image | Header | Blockquote
		:raise TypeError: Выбрасывается при передаче неподдерживаемого элемента.
		"""

		if type(element) not in (Paragraph, Image, Header, Blockquote):
			raise TypeError("Unsupported element.")

		if type(element) in (Paragraph, Blockquote, Header):
			element = cast(Paragraph | Blockquote | Header, element)
			self._Data["paragraphs"].append(element.to_html(footnotes_offset = len(self.footnotes)))
			for CurrentNote in element.footnotes:
				self._Data["footnotes"].append(CurrentNote.to_html())

		else:
			self._Data["paragraphs"].append(element.to_html())

	def set_elements(self, elements: "Sequence[Paragraph | Image | Header | Blockquote]"):
		"""
		Задаёт набор элементов главы.

		:param elements: Набор элементов главы.
		:type elements: Sequence[Paragraph | Image | Header | Blockquote]
		"""

		for Element in elements: self.add_element(Element)

	def set_type(self, type: ChaptersTypes | None):
		"""
		Задаёт тип главы.

		:param type: Тип главы.
		:type type: ChaptersTypes | None
		"""

		self._Data["type"] = type.value if type else None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Ranobe(BaseTitle):
	"""Ранобэ."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТАЙТЛА <<<<< #
	#==========================================================================================#

	@property
	def original_language(self) -> str | None:
		"""Оригинальный язык контента по стандарту ISO 639-3."""

		return self._Data["original_language"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenerateTitleData(self) -> dict[str, Any]:
		"""
		Генерирует базовое словарное представление тайтла.

		:return: Базовое словарное представление тайтла.
		:rtype: dict[str, Any]
		"""

		TitleData = super()._GenerateTitleData()

		return {
			"original_language": None
		} | TitleData

	def _Merge(self, chapter: Chapter, data: dict[str, Any]):
		"""
		Задаёт новое содержимое для главы, используя словарь её данных.

		:param chapter: Глава.
		:type chapter: Chapter
		:param data: Словарь данных главы.
		:type data: dict[str, Any]
		"""

		ContentData: dict = {
			"paragraphs": data["paragraphs"],
			"footnotes": data["footnotes"]
		}

		chapter.from_dict(ContentData)

	def _ParseBranchesToObjects(self):
		"""Преобразует данные ветвей в объекты."""

		self._Branches.clear()

		for BranchID in self._Data["content"]:
			BranchBuffer = BaseBranch(int(BranchID))

			for CurrentChapter in self._Data["content"][BranchID]:
				ChapterBuffer = Chapter(self._Parser, CurrentChapter["id"])
				ChapterBuffer.from_dict(CurrentChapter)
				BranchBuffer.add_chapter(ChapterBuffer)

			self._Branches[BranchBuffer.id] = BranchBuffer

	#==========================================================================================#
	# >>>>> МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_original_language(self, language_code: str | None):
		"""
		Задаёт оригинальный язык контента по стандарту ISO 639-3.

		:param language_code: Код языка.
		:type language_code: str | None
		:raise ValueError: Выбрасывается при несоответствии кода языка стандарту.
		"""

		if language_code:
			CheckLanguageCode(language_code)
		self._Data["original_language"] = language_code.lower() if language_code else None