from . import BaseChapter, BaseBranch, BaseTitle, By, Statuses
from Source.Core.ImagesDownloader import ImagesDownloader
from Source.Core.SystemObjects import SystemObjects
from Source.Core.Exceptions import ChapterNotFound

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Methods.Data import RemoveRecurringSubstrings
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.Methods.System import Clear
from dublib.Polyglot import HTML
from bs4 import BeautifulSoup
from time import sleep

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
	def paragraphs(self) -> list[str]:
		"""Список абзацев."""

		return self._Chapter["paragraphs"]
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

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
		Глава.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__SystemObjects = system_objects
		self.__Title = title

		self._Chapter = {
			"id": None,
			"volume": None,
			"number": None,
			"name": None,
			"is_paid": None,
			"translators": [],
			"paragraphs": []	
		}
		self.__ParserSettings = system_objects.manager.parser_settings

	def add_paragraph(self, paragraph: str):
		"""
		Добавляет абзац.
			paragraph – абзац в формате HTML.
		"""

		IsCorrect = True
		paragraph = self.__ParserSettings.filters.text.clear(paragraph)
		
		if self.__ParserSettings.common.pretty:

			#---> Редактирование абзаца.
			#==========================================================================================#
			paragraph = paragraph.strip()
			Tag = BeautifulSoup(paragraph, "html.parser").find("p")
			
			if Tag.text:
				Align = ""
				InnerHTML = Tag.decode_contents().strip()
				if Tag.has_attr("align"): Align = " align=\"" + Tag["align"] + "\""
				InnerHTML = HTML(InnerHTML)
				InnerHTML.replace_tag("em", "i")
				InnerHTML.replace_tag("strong", "b")
				InnerHTML.unescape()
				Tag = BeautifulSoup(f"<p{Align}>{InnerHTML.text}</p>", "html.parser")

			paragraph = str(Tag)
			paragraph = paragraph.replace("\u00A0", " ")
			paragraph = RemoveRecurringSubstrings(paragraph, " ")
			paragraph = paragraph.replace(" \n", "\n")
			paragraph = paragraph.replace("\n ", "\n")

			#---> Определение валидности абзаца.
			#==========================================================================================#
			
			if not Tag.text.strip():
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
			name = name.rstrip(".")

		name = name.replace("\u00A0", " ")
		name = name.lstrip(":")
		name = name.strip()
		self._Chapter["name"] = name

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

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Ranobe(BaseTitle):
	"""Ранобэ."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Title["localized_name"]

	@property
	def eng_name(self) -> str | None:
		"""Название на английском."""

		return self._Title["eng_name"]

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self._Title["another_names"]

	@property
	def content_language(self) -> str | None:
		"""Язык контента по стандарту ISO 639-3."""

		return self._Title["content_language"]

	@property
	def covers(self) -> list[dict]:
		"""Список описаний обложки."""

		return self._Title["covers"]

	@property
	def authors(self) -> list[str]:
		"""Список авторов."""

		return self._Title["authors"]

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return self._Title["publication_year"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self._Title["description"]

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return self._Title["age_limit"]

	@property
	def genres(self) -> list[str]:
		"""Список жанров."""

		return self._Title["genres"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return self._Title["tags"]

	@property
	def franchises(self) -> list[str]:
		"""Список франшиз."""

		return self._Title["franchises"]

	@property
	def original_language(self) -> str | None:
		"""Оригинальный язык контента по стандарту ISO 639-3."""

		return self._Title["original_language"]

	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return self._Title["status"]

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return self._Title["is_licensed"]

	@property
	def branches(self) -> list[Branch]:
		"""Список ветвей тайтла."""

		return self.__Branches

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CalculateEmptyChapters(self) -> int:
		"""Подсчитывает количество глав без контента во всех ветвях."""

		EmptyChaptersCount = 0
		for Branch in self.__Branches: EmptyChaptersCount += Branch.empty_chapters_count

		return EmptyChaptersCount

	def __CheckStringsList(self, data: list[str]):
		"""
		Проверяет, содержит ли список только строки.
			data – список объектов.
		"""

		for Element in data:
			if type(Element) != str: raise TypeError(Element)

	def __FindChapterByID(self, chapter_id: int) -> tuple[Branch, Chapter] | None:
		"""
		Возвращает данные ветви и главы для указанного ID.
			chapter_id – уникальный идентификатор главы.
		"""

		BranchResult = None
		ChapterResult = None

		for CurrentBranch in self.__Branches:

			for CurrentChapter in CurrentBranch.chapters:

				if CurrentChapter.id == chapter_id:
					BranchResult = CurrentBranch
					ChapterResult = CurrentChapter
					break

		Result = (BranchResult, ChapterResult) if ChapterResult else None

		return Result

	def __InitializeRequestor(self) -> WebRequestor:
		"""
		Инициализирует модуль WEB-запросов.
			proxy – данные о прокси.
		"""

		ParserSettings = self.__SystemObjects.manager.get_parser_settings()
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.requests.enable_proxy_protocol_switching(True)
		Config.set_retries_count(2)
		WebRequestorObject = WebRequestor(Config)

		if ParserSettings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = ParserSettings.proxy.host,
			port = ParserSettings.proxy.port,
			login = ParserSettings.proxy.login,
			password = ParserSettings.proxy.password
		)

		return WebRequestorObject

	def __PrintAmendingProgress(self, message: str, current_state: int, max_state: int):
		"""
		Выводит в консоль прогресс дополнение глав информацией о содержимом.
			message – сообщение из внешнего обработчика;\n
			current_state – индекс текущей дополняемой главы;\n
			max_state – количество глав, которые необходимо дополнить.
		"""

		Clear()
		print(f"{message}\nAmending: {current_state} / {max_state}")

	def __UpdateBranchesInfo(self):
		"""Обновляет информацию о ветвях."""

		Branches = list()
		for CurrentBranch in self.__Branches: Branches.append({"id": CurrentBranch.id, "chapters_count": CurrentBranch.chapters_count })
		self._Title["branches"] = sorted(Branches, key = lambda Value: Value["chapters_count"], reverse = True) 

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, system_objects: SystemObjects):
		"""
		Манга.
			system_objects – коллекция системных объектов.
		"""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__SystemObjects = system_objects

		self.__ParserSettings = self.__SystemObjects.manager.get_parser_settings()
		self.__Branches: list[Branch] = list()
		self.__UsedFilename = None
		self.__Parser = None

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

			"original_language": None,
			"status": None,
			"is_licensed": None,
			
			"genres": [],
			"tags": [],
			"franchises": [],
			
			"branches": [],
			"content": {} 
		}

	def amend(self, message: str):
		"""
		Дополняет содержимое подробной информацией.
			message – сообщение для внутреннего обработчика.
		"""

		ChaptersToAmendCount = self.__CalculateEmptyChapters()
		AmendedChaptersCount = 0
		ProgressIndex = 0

		for CurrentBranch in self.__Branches:

			for CurrentChapter in CurrentBranch.chapters:
				if CurrentChapter.is_empty:
					ProgressIndex += 1
					self.__Parser.amend(CurrentBranch, CurrentChapter)

					if CurrentChapter.paragraphs:
						AmendedChaptersCount += 1
						self.__SystemObjects.logger.chapter_amended(self, CurrentChapter)

					self.__PrintAmendingProgress(message, ProgressIndex, ChaptersToAmendCount)
					sleep(self.__ParserSettings.common.delay)

		self.__SystemObjects.logger.amending_end(self, AmendedChaptersCount)

	def download_covers(self, message: str):
		"""
		Скачивает обложки.
			message – сообщение для внутреннего обработчика.
		"""

		Requestor = self.__InitializeRequestor()
		CoversDirectory = f"{self.__ParserSettings.common.covers_directory}/{self.__UsedFilename}/"
		if not os.path.exists(CoversDirectory): os.makedirs(CoversDirectory)
		Clear()
		print(message)

		for CoverIndex in range(len(self._Title["covers"])):
			Filename = self._Title["covers"][CoverIndex]["link"].split("/")[-1]
			print(f"Downloading cover: \"{Filename}\"... ", end = "")
			Result = ImagesDownloader(self.__SystemObjects, Requestor).image(
				url = self._Title["covers"][CoverIndex]["link"],
				directory = CoversDirectory,
				filename = self._Title["covers"][CoverIndex]["filename"],
				is_full_filename = True
			)
			print(Result.message)
			sleep(0.25)

	def merge(self):
		"""Объединяет данные описательного файла и текущей структуры данных."""

		Path = f"{self.__ParserSettings.common.titles_directory}/{self.__UsedFilename}.json"
		
		if os.path.exists(Path) and not self.__SystemObjects.FORCE_MODE:
			LocalManga = ReadJSON(Path)
			LocalContent = dict()
			MergedChaptersCount = 0
			
			for BranchID in LocalManga["content"]:
				for CurrentChapter in LocalManga["content"][BranchID]: LocalContent[CurrentChapter["id"]] = CurrentChapter["paragraphs"]
			
			for BranchID in self._Title["content"]:
		
				for ChapterIndex in range(len(self._Title["content"][BranchID])):
				
					if self._Title["content"][BranchID][ChapterIndex]["id"] in LocalContent.keys():
						ChapterID = self._Title["content"][BranchID][ChapterIndex]["id"]

						if LocalContent[ChapterID]:
							self._Title["content"][BranchID][ChapterIndex]["paragraphs"] = LocalContent[ChapterID]
							MergedChaptersCount += 1

			self.__SystemObjects.logger.info("Title: \"" + self._Title["slug"] + f"\" (ID: " + str(self._Title["id"]) + f"). Merged chapters count: {MergedChaptersCount}.")

		elif self.__SystemObjects.FORCE_MODE:
			self.__SystemObjects.logger.info("Title: \"" + self._Title["slug"] + "\" (ID: " + str(self._Title["id"]) + "). Local data removed.")

		self.__Branches = list()

		for CurrentBranchID in self._Title["content"].keys():
			BranchID = int(CurrentBranchID)
			NewBranch = Branch(BranchID)

			for ChapterData in self._Title["content"][CurrentBranchID]:
				NewChapter = Chapter(self.__SystemObjects, self)
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
		Directory = self.__ParserSettings.common.titles_directory

		if selector_type == By.Filename:
			Path = f"{Directory}/{identificator}.json"

			if os.path.exists(Path):
				Data = ReadJSON(f"{Directory}/{identificator}.json")
				
			else:
				self.__SystemObjects.logger.critical("Couldn't open file.")
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

		if Data: self._Title = Data
		else: raise FileNotFoundError(identificator + ".json")

	def parse(self, message: str | None = None):
		"""
		Получает основные данные тайтла.
			message – сообщение для внутреннего обработчика.
		"""
		
		Clear()
		message = message or ""
		if message: print(f"{message}\nParsing data...")
		self.__Parser.parse()
		self.__UsedFilename = str(self.id) if self.__ParserSettings.common.use_id_as_filename else self.slug

	def repair(self, chapter_id: int):
		"""
		Восстанавливает содержимое главы, заново получая его из источника.
			chapter_id – уникальный идентификатор целевой главы.
		"""

		SearchResult = self.__FindChapterByID(chapter_id)

		if not SearchResult:
			self.__SystemObjects.logger.title_not_found(self)
			raise ChapterNotFound(chapter_id)

		BranchData: Branch = SearchResult[0]
		ChapterData: Chapter = SearchResult[1]
		ChapterData.clear_slides()
		self.__Parser.amend(BranchData, ChapterData)

		if ChapterData.slides: self.__SystemObjects.logger.chapter_repaired(self, ChapterData)

	def save(self):
		"""Сохраняет данные манги в описательный файл."""

		for BranchID in self._Title["content"].keys(): self._Title["content"][BranchID] = sorted(self._Title["content"][BranchID], key = lambda Value: (list(map(int, Value["volume"].split("."))), list(map(int, Value["number"].split("."))))) 
		WriteJSON(f"{self.__ParserSettings.common.titles_directory}/{self.__UsedFilename}.json", self._Title)
		self.__SystemObjects.logger.info("Title: \"" + self._Title["slug"] + "\" (ID: " + str(self._Title["id"]) + "). Saved.")

	def set_parser(self, parser: any):
		"""Задаёт парсер для вызова методов."""

		self.__Parser = parser

	#==========================================================================================#
	# >>>>> МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str):
		"""
		Добавляет альтернативное название.
			another_name – название.
		"""
		
		if another_name != self._Title["localized_name"] and another_name != self._Title["eng_name"]: self._Title["another_names"].append(another_name)

	def add_cover(self, link: str, filename: str | None = None, width: int | None = None, height: int | None = None):
		"""
		Добавляет обложку.
			link – ссылка на изображение;\n
			filename – имя локального файла;\n
			width – ширина обложки;\n
			height – высота обложки.
		"""

		if not filename: filename = link.split("/")[-1]
		CoverInfo = {
			"link": link,
			"filename": filename,
			"width": width,
			"height": height
		}

		if not self.__ParserSettings.common.sizing_images: 
			del CoverInfo["width"]
			del CoverInfo["height"]

		self._Title["covers"].append(CoverInfo)

	def add_author(self, author: str):
		"""
		Добавляет автора.
			author – автор.
		"""

		if author not in self._Title["authors"]: self._Title["authors"].append(author)

	def add_genre(self, genre: str):
		"""
		Добавляет жанр.
			genre – жанр.
		"""

		if genre not in self._Title["genres"]: self._Title["genres"].append(genre)

	def add_tag(self, tag: str):
		"""
		Добавляет тег.
			tag – тег.
		"""

		if tag not in self._Title["tags"]: self._Title["tags"].append(tag)

	def add_franshise(self, franshise: str):
		"""
		Добавляет франшизу.
			franshise – франшиза.
		"""

		if franshise not in self._Title["franshises"]: self._Title["franshises"].append(franshise)

	def add_branch(self, branch: Branch):
		"""
		Добавляет ветвь.
			branch – ветвь.
		"""

		if branch not in self.__Branches: self.__Branches.append(branch)
		self._Title["content"] = dict()
		for CurrentBranch in self.__Branches: self._Title["content"][str(CurrentBranch.id)] = CurrentBranch.to_list()
		self.__UpdateBranchesInfo()

	def set_site(self, site: str):
		"""
		Задаёт домен источника.
			site – домен сайта.
		"""

		self._Title["site"] = site

	def set_id(self, id: int):
		"""
		Задаёт целочисленный уникальный идентификатор тайтла.
			id – идентификатор.
		"""

		self._Title["id"] = id

	def set_slug(self, slug: str):
		"""
		Задаёт алиас манги.
			slug – алиас.
		"""

		self._Title["slug"] = slug

	def set_content_language(self, content_language: str | None):
		"""
		Задаёт язык контента по стандарту ISO 639-3.
			content_language – код языка.
		"""

		if type(content_language) == str and len(content_language) != 3: raise TypeError(content_language)
		self._Title["content_language"] = content_language.lower() if content_language else None

	def set_localized_name(self, localized_name: str | None):
		"""
		Задаёт главное название манги на русском.
			ru_name – название на русском.
		"""

		self._Title["localized_name"] = localized_name

	def set_eng_name(self, eng_name: str | None):
		"""
		Задаёт главное название манги на английском.
			en_name – название на английском.
		"""

		self._Title["eng_name"] = eng_name

	def set_another_names(self, another_names: list[str]):
		"""
		Задаёт список альтернативных названий на любых языках.
			another_names – список названий.
		"""

		self.__CheckStringsList(another_names)
		self._Title["another_names"] = another_names

	def set_covers(self, covers: list[dict]):
		"""
		Задаёт список описаний обложек.
			covers – список названий.
		"""

		self._Title["covers"] = covers

	def set_authors(self, authors: list[str]):
		"""
		Задаёт список авторов.
			covers – список авторов.
		"""

		self.__CheckStringsList(authors)
		self._Title["authors"] = authors

	def set_publication_year(self, publication_year: int | None):
		"""
		Задаёт год публикации манги.
			publication_year – год.
		"""

		self._Title["publication_year"] = publication_year

	def set_description(self, description: str | None):
		"""
		Задаёт описание манги.
			description – описание.
		"""

		self._Title["description"] = description

	def set_age_limit(self, age_limit: int | None):
		"""
		Задаёт возрастной рейтинг.
			age_limit – возрастной рейтинг.
		"""

		self._Title["age_limit"] = age_limit

	def set_genres(self, genres: list[str]):
		"""
		Задаёт список жанров.
			genres – список жанров.
		"""

		self.__CheckStringsList(genres)
		self._Title["genres"] = genres

	def set_tags(self, tags: list[str]):
		"""
		Задаёт список тегов.
			tags – список тегов.
		"""

		self.__CheckStringsList(tags)
		self._Title["tags"] = tags

	def set_franchises(self, franchises: list[str]):
		"""
		Задаёт список франшиз.
			franchises – список франшиз.
		"""

		self.__CheckStringsList(franchises)
		self._Title["franchises"] = franchises

	def set_original_language(self, original_language: str | None):
		"""
		Задаёт оригинальный язык контента по стандарту ISO 639-3.
			original_language – код языка.
		"""

		if type(original_language) == str and len(original_language) != 3: raise TypeError(original_language)
		self._Title["original_language"] = original_language.lower() if original_language else None

	def set_status(self, status: Statuses | None):
		"""
		Задаёт статус манги.
			status – статус.
		"""

		if status: self._Title["status"] = status.value
		else: self._Title["status"] = None
		
	def set_is_licensed(self, is_licensed: bool | None):
		"""
		Задаёт статус лицензирования манги.
			is_licensed – статус лицензирования.
		"""

		self._Title["is_licensed"] = is_licensed