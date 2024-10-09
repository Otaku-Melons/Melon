from . import BaseChapter, BaseBranch, BaseTitle, By, Statuses
from Source.Core.SystemObjects import SystemObjects
from Source.Core.Exceptions import ChapterNotFound

from dublib.Methods.Data import ReplaceDictionaryKey, Zerotify
from dublib.Methods.JSON import ReadJSON, WriteJSON

import enum
import os

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Chapter(BaseChapter):
	"""Глава."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def slides(self) -> list[dict]:
		"""Список слайдов."""

		return self._Chapter["slides"]
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects):
		"""
		Глава.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._SystemObjects = system_objects
		self._Chapter = {
			"id": None,
			"volume": None,
			"number": None,
			"name": None,
			"is_paid": None,
			"translators": [],
			"slides": []	
		}

	def add_slide(self, link: str, width: int | None = None, height: int | None = None):
		"""
		Добавляет данные о слайде.
			link – ссылка на слайд;\n
			width – ширина слайда;\n
			height – высота слайда.
		"""

		ParserSettings = self._SystemObjects.manager.parser_settings
		SlideInfo = {
			"index": len(self._Chapter["slides"]) + 1,
			"link": link,
			"width": width,
			"height": height
		}

		if width and height and ParserSettings.filters.image.check_sizes(width, height):
			return

		if not ParserSettings.common.sizing_images: 
			del SlideInfo["width"]
			del SlideInfo["height"]

		self._Chapter["slides"].append(SlideInfo)

	def clear_slides(self):
		"""Удаляет данные слайдов."""

		self._Chapter["slides"] = list()

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

		#---> Генерация динамических свойств.
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

class Types(enum.Enum):
	"""Определения типов манги."""

	manga = "manga"
	manhwa = "manhwa"
	manhua = "manhua"
	oel = "oel"
	western_comic = "western_comic"
	russian_comic = "russian_comic"
	indonesian_comic = "indonesian_comic"

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Manga(BaseTitle):
	"""Манга."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def type(self) -> Types | None:
		"""Тип тайтла."""

		return self._Title["type"]

	#==========================================================================================#
	# >>>>> LEGACY-КОНВЕРТЕРЫ <<<<< #
	#==========================================================================================#

	def __FromLegacy(self, manga: dict) -> dict:
		"""
		Форматирует мангу из устаревшего формата.
			manga – словарное описание манги.
		"""

		Types = {
			"UNKNOWN": None,
			"MANGA": "manga",
			"MANHWA": "manhwa",
			"MANHUA": "manhua",
			"WESTERN_COMIC": "western_comic",
			"RUS_COMIC": "russian_comic",
			"INDONESIAN_COMIC": "indonesian_comic",
			"MANGA": "manga",
			"OEL": "oel"
		}
		Statuses = {
			"UNKNOWN": None,
			"ANNOUNCED": "announced",
			"ONGOING": "ongoing",
			"ABANDONED": "dropped",
			"COMPLETED": "completed"
		}
		manga["content_language"] = None
		manga = ReplaceDictionaryKey(manga, "ru-name", "localized_name")
		manga = ReplaceDictionaryKey(manga, "en-name", "eng_name")
		manga = ReplaceDictionaryKey(manga, "another-names", "another_names")
		manga = ReplaceDictionaryKey(manga, "author", "authors")
		manga = ReplaceDictionaryKey(manga, "publication-year", "publication_year")
		manga = ReplaceDictionaryKey(manga, "age-rating", "age_limit")
		manga = ReplaceDictionaryKey(manga, "is-licensed", "is_licensed")
		manga = ReplaceDictionaryKey(manga, "series", "franchises")
		manga = ReplaceDictionaryKey(manga, "chapters", "content")
		manga["format"] = "melon-manga"
		manga["authors"] = manga["authors"].split(", ") if manga["authors"] else list()
		manga["type"] = Types[manga["type"]]
		manga["status"] = Statuses[manga["status"]]

		for BranchID in manga["content"]:

			for ChapterIndex in range(len(manga["content"][BranchID])):
				Buffer = manga["content"][BranchID][ChapterIndex]
				Buffer = ReplaceDictionaryKey(Buffer, "is-paid", "is_paid")
				Buffer = ReplaceDictionaryKey(Buffer, "translator", "translators")
				Buffer["translators"] = Buffer["translators"].split(", ") if Buffer["translators"] else list()
				manga["content"][BranchID][ChapterIndex] = Buffer

		return manga

	def __ToLegacy(self, manga: dict) -> dict:
		"""
		Форматирует мангу в устаревший формат.
			manga – словарное описание манги.
		"""

		Types = {
			None: "UNKNOWN",
			"manga": "MANGA",
			"manhwa": "MANHWA",
			"manhua": "MANHUA",
			"western_comic": "WESTERN_COMIC",
			"russian_comic": "RUS_COMIC",
			"indonesian_comic": "INDONESIAN_COMIC",
			"oel": "OEL"
		}
		Statuses = {
			None: "UNKNOWN",
			"announced": "ANNOUNCED",
			"ongoing": "ONGOING",
			"dropped": "ABANDONED",
			"completed": "COMPLETED"
		}
		del manga["content_language"]
		manga = ReplaceDictionaryKey(manga, "localized_name", "ru-name")
		manga = ReplaceDictionaryKey(manga, "eng_name", "en-name")
		manga = ReplaceDictionaryKey(manga, "another_names", "another-names")
		manga = ReplaceDictionaryKey(manga, "authors", "author")
		manga = ReplaceDictionaryKey(manga, "publication_year", "publication-year")
		manga = ReplaceDictionaryKey(manga, "age_limit", "age-rating")
		manga = ReplaceDictionaryKey(manga, "is_licensed", "is-licensed")
		manga = ReplaceDictionaryKey(manga, "franchises", "series")
		manga = ReplaceDictionaryKey(manga, "content", "chapters")
		manga["format"] = "dmp-v1"
		manga["author"] = Zerotify(", ".join(manga["author"]))
		manga["type"] = Types[manga["type"]]
		manga["status"] = Statuses[manga["status"]]

		for Index in range(len(manga["genres"])): manga["genres"][Index] = manga["genres"][Index].lower()
		for Index in range(len(manga["tags"])): manga["tags"][Index] = manga["tags"][Index].lower()

		for BranchID in manga["chapters"]:

			for ChapterIndex in range(len(manga["chapters"][BranchID])):
				Buffer = manga["chapters"][BranchID][ChapterIndex]
				Buffer = ReplaceDictionaryKey(Buffer, "is_paid", "is-paid")
				Buffer = ReplaceDictionaryKey(Buffer, "translators", "translator")
				Buffer["translator"] = ", ".join(Buffer["translator"]) if Buffer["translator"] else None
				manga["chapters"][BranchID][ChapterIndex] = Buffer

		return manga

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Title = {
			"format": "melon-manga",
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

			"type": None,
			"status": None,
			"is_licensed": None,
			
			"genres": [],
			"tags": [],
			"franchises": [],
			
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
			LocalManga = ReadJSON(Path)
			if LocalManga["format"] != "melon-manga": LocalManga = self.__FromLegacy(LocalManga)
			LocalContent = dict()
			MergedChaptersCount = 0
			
			for BranchID in LocalManga["content"]:
				for CurrentChapter in LocalManga["content"][BranchID]: LocalContent[CurrentChapter["id"]] = CurrentChapter["slides"]
			
			for BranchID in self._Title["content"]:
		
				for ChapterIndex in range(len(self._Title["content"][BranchID])):
				
					if self._Title["content"][BranchID][ChapterIndex]["id"] in LocalContent.keys():
						ChapterID = self._Title["content"][BranchID][ChapterIndex]["id"]

						if LocalContent[ChapterID]:
							self._Title["content"][BranchID][ChapterIndex]["slides"] = LocalContent[ChapterID]
							MergedChaptersCount += 1

			self._SystemObjects.logger.info("Title: \"" + self._Title["slug"] + f"\" (ID: " + str(self._Title["id"]) + f"). Merged chapters count: {MergedChaptersCount}.")

		elif self._SystemObjects.FORCE_MODE:
			self._SystemObjects.logger.info("Title: \"" + self._Title["slug"] + "\" (ID: " + str(self._Title["id"]) + "). Local data removed.")

		self._Branches = list()

		for CurrentBranchID in self._Title["content"].keys():
			BranchID = int(CurrentBranchID)
			NewBranch = Branch(BranchID)

			for ChapterData in self._Title["content"][CurrentBranchID]:
				NewChapter = Chapter(self._SystemObjects)
				NewChapter.set_dict(ChapterData)
				NewBranch.add_chapter(NewChapter)

			self.add_branch(NewBranch)

	def open(self, identificator: int | str, selector_type: By = By.Filename):
		"""
		Считывает локальный описательный файл.
			identificator – идентификатор тайтла;\n
			selector_type – тип указателя на тайтл.
		"""

		Data = None
		Directory = self._ParserSettings.common.titles_directory

		if selector_type == By.Filename:
			Path = f"{Directory}/{identificator}.json"

			if os.path.exists(Path):
				Data = ReadJSON(f"{Directory}/{identificator}.json")
				
			else:
				self._SystemObjects.logger.critical("Couldn't open file.")
				raise FileNotFoundError(Path)

		if selector_type == By.Slug:
			LocalTitles = os.listdir(Directory)
			LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))

			for File in LocalTitles:
				Path = f"{Directory}/{File}"

				if os.path.exists(Path):
					Buffer = ReadJSON(Path)

					if Buffer["slug"] == identificator:
						Data = Buffer
						break

		if selector_type == By.ID:
			LocalTitles = os.listdir(Directory)
			LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))

			for File in LocalTitles:
				Path = f"{Directory}/{File}"

				if os.path.exists(Path):
					Buffer = ReadJSON(Path)

					if Buffer["id"] == identificator:
						Data = Buffer
						break

		if Data:
			self._Title = Data
			if self._Title["format"] != "melon-manga": self._Title = self.__FromLegacy(Data)
			
		else: raise FileNotFoundError(identificator + ".json")

	def repair(self, chapter_id: int):
		"""
		Восстанавливает содержимое главы, заново получая его из источника.
			chapter_id – уникальный идентификатор целевой главы.
		"""

		SearchResult = self._FindChapterByID(chapter_id)

		if not SearchResult:
			self._SystemObjects.logger.title_not_found(self)
			raise ChapterNotFound(chapter_id)

		BranchData: Branch = SearchResult[0]
		ChapterData: Chapter = SearchResult[1]
		ChapterData.clear_slides()
		self._Parser.amend(BranchData, ChapterData)

		if ChapterData.slides: self._SystemObjects.logger.chapter_repaired(self, ChapterData)

	def save(self):
		"""Сохраняет данные манги в описательный файл."""

		for BranchID in self._Title["content"].keys(): self._Title["content"][BranchID] = sorted(self._Title["content"][BranchID], key = lambda Value: (list(map(int, Value["volume"].split("."))), list(map(int, Value["number"].split("."))))) 
		
		if self._IsLegacy:
			self._Title = self.__ToLegacy(self._Title)
			self._SystemObjects.logger.info("Title: \"" + self._Title["slug"] + "\". Converted to legacy format.")

		self._CheckStandartPath(self._ParserSettings.common.titles_directory)
		WriteJSON(f"{self._ParserSettings.common.titles_directory}/{self._UsedFilename}.json", self._Title)
		self._SystemObjects.logger.info(f"Title: \"{self.slug}\" (ID: {self.id}). Saved.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_type(self, type: Types | None):
		"""
		Задаёт типп манги.
			type – тип.
		"""

		if type: self._Title["type"] = type.value
		else: self._Title["type"] = None