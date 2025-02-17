from . import BaseChapter, BaseBranch, BaseTitle, By, Statuses
from Source.Core.ImagesDownloader import ImagesDownloader
from Source.Core.SystemObjects import SystemObjects
from Source.Core.Exceptions import ChapterNotFound

from dublib.Methods.Data import RemoveRecurringSubstrings
from dublib.Methods.Filesystem import ReadJSON
from dublib.Polyglot import HTML
from bs4 import BeautifulSoup
from time import sleep

import enum
import os

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ ТИПОВ <<<<< #
#==========================================================================================#

class ChaptersTypes(enum.Enum):
	"""Определения типов глав."""

	afterword = "afterword"
	art = "art"
	chapter = "chapter"
	epilogue = "epilogue"
	extra = "extra"
	glossary = "glossary"
	prologue = "prologue"
	trash = "trash"

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Chapter(BaseChapter):
	"""Глава ранобэ."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def paragraphs(self) -> list[str]:
		"""Список абзацев."""

		return self._Chapter["paragraphs"]
	
	@property
	def type(self) -> ChaptersTypes | None:
		"""Тип главы."""

		return ChaptersTypes[self._Chapter["type"]]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __DownloadImages(self, paragraph: BeautifulSoup):
		"""
		Скачивает иллюстрации из абзаца.
			paragraph – абзац.
		"""

		Parser = self.__Title.parser
		Images = paragraph.find_all("img")
		
		for Image in Images:
			Image: BeautifulSoup
			Message = "Done."
			
			if Image.has_attr("src"):
				Image.attrs = {"src": Image["src"]}
				Link = Image["src"]
				Filename = Link.split("/")[-1]
				Result = None

				print(f"Downloading image: \"{Filename}\"... ", end = "")
				
				Filename = Parser.image(Link)
				sleep(Parser.settings.common.delay)

				Directory = f"{Parser.settings.ranobe.images_directory}/{self.__Title.used_filename}/{self.id}"

				if Filename: 
					Path = f"{self._SystemObjects.temper.parser_temp}/{Filename}"

					if Parser.settings.filters.image.check_hash(Path):
						Message = "Filtered by MD5 hash."
						Image.decompose()
						os.remove(Path)

					else:
						if not os.path.exists(Directory): os.makedirs(Directory)
						Result = ImagesDownloader(self._SystemObjects).move_from_temp(Directory, Filename)

						if Result: Image["src"] = f"{Directory}/{Filename}"
						else: Message = "Error."

				else:
					Message = "Error."
					

				if Message != "Done." and Parser.settings.common.bad_image_stub:
					Image["src"] = Parser.settings.common.bad_image_stub
					Message += " Replaced by stub."

				print(Message)

			else: Image.decompose()

	def __GetLocalizedChapterWord(self) -> str | None:
		"""Возвращает слово в нижнем регистре, обозначающее главу."""

		Language = self.__Title.content_language
		Words = {
			None: None,
			"rus": "глава",
			"eng": "chapter"
		}
		Word = None
		if Language in Words.keys(): Word = Words[Language]

		return Word

	def __TryGetName(self, paragraph: str):
		"""
		Пытается получить название главы из абзаца.
			paragraph – абзац.
		"""

		if not self.name:
			LocalizedChapterWord = self.__GetLocalizedChapterWord()
			ChapterCounterLength = len(f"{LocalizedChapterWord} {self.number}")
			paragraph = paragraph[ChapterCounterLength:]
			paragraph = paragraph.strip()
			self.set_name(paragraph)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects, title: "Ranobe"):
		"""
		Глава ранобэ.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self._SystemObjects = system_objects
		self.__Title = title

		self._Chapter = {
			"id": None,
			"slug": None,
			"volume": None,
			"number": None,
			"name": None,
			"type": None,
			"is_paid": None,
			"translators": [],
			"paragraphs": []	
		}
		self._ParserSettings = system_objects.manager.parser_settings

		self._SetParagraphsMethod = self.set_paragraphs
		self._SetSlidesMethod = self._Pass

	def add_paragraph(self, paragraph: str):
		"""
		Добавляет абзац.
			paragraph – абзац в формате HTML.
		"""

		IsCorrect = True

		paragraph = self._ParserSettings.filters.text.clear(paragraph)
		Tag = BeautifulSoup(paragraph, "html.parser").find("p")
		self.__DownloadImages(Tag)
		if self._ParserSettings.common.pretty:

			#---> Редактирование абзаца.
			#==========================================================================================#
			
			if Tag.text:
				Align = ""
				InnerHTML = Tag.decode_contents().strip()
				if Tag.has_attr("align"): Align = " align=\"" + Tag["align"] + "\""
				InnerHTML = HTML(InnerHTML)
				InnerHTML.replace_tag("em", "i")
				InnerHTML.replace_tag("strong", "b")
				InnerHTML.replace_tag("strike", "s")
				InnerHTML.replace_tag("del", "s")
				InnerHTML.unescape()
				Tag = BeautifulSoup(f"<p{Align}>{InnerHTML.text}</p>", "html.parser")

			paragraph = str(Tag)
			paragraph = paragraph.replace("\u00A0", " ")
			paragraph = RemoveRecurringSubstrings(paragraph, " ")
			paragraph = paragraph.replace(" \n", "\n")
			paragraph = paragraph.replace("\n ", "\n")

			#---> Определение валидности абзаца.
			#==========================================================================================#
			
			if not Tag.text.strip(" \t\n.") and not Tag.find("img"):
				IsCorrect = False

			elif len(self._Chapter["paragraphs"]) < 4:
				Paragraph = Tag.text.rstrip(".!?…").lower()
				ChapterName = self.name.rstrip(".!?…").lower() if self.name else None
				LocalizedName = self.__Title.localized_name.rstrip(".!?…").lower() if self.__Title.localized_name else None
				LocalizedChapterWord = self.__GetLocalizedChapterWord()

				if ChapterName and Paragraph == ChapterName: IsCorrect = False
				elif LocalizedName and Paragraph == LocalizedName: IsCorrect = False
				elif LocalizedChapterWord and f"{LocalizedChapterWord} {self.number}" in Paragraph:
					IsCorrect = False
					self.__TryGetName(Tag.text)

		if IsCorrect: self._Chapter["paragraphs"].append(paragraph)

	def clear_paragraphs(self):
		"""Удаляет содержимое главы."""

		self._Chapter["paragraphs"] = list()

	def set_name(self, name: str | None):
		"""
		Задаёт название главы.
			name – название главы.
		"""

		if not name:
			self._Chapter["name"] = None
			return

		if name.endswith("..."):
			name = name.rstrip(".")
			name += "…"

		else: 
			name = name.rstrip(".–")

		name = name.replace("\u00A0", " ")
		name = name.lstrip(":")
		name = name.strip()
		self._Chapter["name"] = name

	def set_paragraphs(self, paragraphs: list[str]):
		"""
		Задаёт список абзацев.
			slides – список абзацев.
		"""

		for Paragraph in paragraphs: self.add_paragraph(Paragraph)

	def set_type(self, type: ChaptersTypes | None):
		"""
		Задаёт тип главы.
			type – тип.
		"""

		if type: self._Chapter["type"] = type.value
		else: self._Chapter["type"] = None

class Branch(BaseBranch):
	"""Ветвь."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def chapters(self) -> list[Chapter]:
		"""Список глав."""

		return self._Chapters
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, id: int):
		"""
		Ветвь.
			ID – уникальный идентификатор ветви.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self._ID = id
		self._Chapters: list[Chapter] = list()

	def add_chapter(self, chapter: Chapter):
		"""
		Добавляет главу в ветвь.
			chapter – глава.
		"""

		self._Chapters.append(chapter)

	def get_chapter_by_id(self, id: int) -> Chapter:
		"""
		Возвращает главу по её уникальному идентификатору.
			id – идентификатор главы.
		"""

		Data = None

		for CurrentChapter in self._Chapters:
			if CurrentChapter.id == id: Data = CurrentChapter

		if not Data: raise KeyError(id)

		return CurrentChapter
	
	def replace_chapter_by_id(self, chapter: Chapter, id: int):
		"""
		Заменяет главу по её уникальному идентификатору.
			id – идентификатор главы.
		"""

		IsSuccess = False

		for Index in range(len(self._Chapters)):

			if self._Chapters[Index].id == id:
				self._Chapters[Index] = chapter
				IsSuccess = True

		if not IsSuccess: raise KeyError(id)

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Ranobe(BaseTitle):
	"""Ранобэ."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def original_language(self) -> str | None:
		"""Оригинальный язык контента по стандарту ISO 639-3."""

		return self._Title["original_language"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Title = {
			"format": "melon-ranobe",
			"site": None,
			"id": None,
			"slug": None,
			"content_language": None,

			"localized_name": None,
			"eng_name": None,
			"another_names": [],
			"covers": [],

			"authors": [],
			"publication_year": None,
			"description": None,
			"age_limit": None,

			"original_language": None,
			"status": None,
			"is_licensed": None,
			
			"genres": [],
			"tags": [],
			"franchises": [],
			"persons": [],
			
			"branches": [],
			"content": {} 
		}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def merge(self):
		"""Объединяет данные описательного файла и текущей структуры данных."""

		Path = f"{self._ParserSettings.common.titles_directory}/{self._UsedFilename}.json"
		
		if os.path.exists(Path) and not self._SystemObjects.FORCE_MODE:
			LocalRanobe = ReadJSON(Path)
			LocalContent = dict()
			MergedChaptersCount = 0

			if LocalRanobe["format"] != "melon-ranobe":
				self._SystemObjects.logger.unsupported_format(self)
				return
			
			for BranchID in LocalRanobe["content"]:
				for CurrentChapter in LocalRanobe["content"][BranchID]: LocalContent[CurrentChapter["id"]] = CurrentChapter["paragraphs"]
			
			for BranchID in self._Title["content"]:
		
				for ChapterIndex in range(len(self._Title["content"][BranchID])):
				
					if self._Title["content"][BranchID][ChapterIndex]["id"] in LocalContent.keys():
						ChapterID = self._Title["content"][BranchID][ChapterIndex]["id"]

						if LocalContent[ChapterID]:
							self._Title["content"][BranchID][ChapterIndex]["paragraphs"] = LocalContent[ChapterID]
							MergedChaptersCount += 1

			self._SystemObjects.logger.merging_end(self, MergedChaptersCount)

		self._Branches = list()

		for CurrentBranchID in self._Title["content"].keys():
			BranchID = int(CurrentBranchID)
			NewBranch = Branch(BranchID)

			for ChapterData in self._Title["content"][CurrentBranchID]:
				NewChapter = Chapter(self._SystemObjects, self)
				NewChapter.set_dict(ChapterData)
				NewBranch.add_chapter(NewChapter)

			self.add_branch(NewBranch)

	def repair(self, chapter_id: int):
		"""
		Восстанавливает содержимое главы, заново получая его из источника.
			chapter_id – уникальный идентификатор целевой главы.
		"""

		print()
		SearchResult = self._FindChapterByID(chapter_id)

		if not SearchResult: raise ChapterNotFound(chapter_id)

		BranchData: Branch = SearchResult[0]
		ChapterData: Chapter = SearchResult[1]
		ChapterData.clear_paragraphs()
		self._Parser.amend(BranchData, ChapterData)

		if ChapterData.paragraphs: self._SystemObjects.logger.chapter_repaired(self, ChapterData)

	#==========================================================================================#
	# >>>>> МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_original_language(self, original_language: str | None):
		"""
		Задаёт оригинальный язык контента по стандарту ISO 639-3.
			original_language – код языка.
		"""

		if type(original_language) == str and len(original_language) != 3: raise TypeError(original_language)
		self._Title["original_language"] = original_language.lower() if original_language else None