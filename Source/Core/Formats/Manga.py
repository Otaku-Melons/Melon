from Source.Core.ImagesDownloader import ImagesDownloader
from Source.Core.SystemObjects import SystemObjects
from Source.Core.ParserSettings import Proxy
from . import By, Statuses

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Methods.Data import ReplaceDictionaryKey, Zerotify
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.Methods.System import Clear
from time import sleep

import enum
import os

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

FORMAT_NAME = "melon-manga"

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Chapter:
	"""Глава."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def id(self) -> int | None:
		"""Уникальный идентификатор главы."""

		return self.__Chapter["id"]
	
	@property
	def volume(self) -> str | None:
		"""Номер тома."""

		return self.__Chapter["volume"]
	
	@property
	def number(self) -> str | None:
		"""Номер главы."""

		return self.__Chapter["number"]
	
	@property
	def name(self) -> str | None:
		"""Название главы."""

		return self.__Chapter["name"]
	
	@property
	def is_paid(self) -> bool | None:
		"""Состояние: платная ли глава."""

		return self.__Chapter["is_paid"]
	
	@property
	def translators(self) -> list[str]:
		"""Список ников переводчиков."""

		return self.__Chapter["translators"]
	
	@property
	def slides(self) -> list[dict]:
		"""Список слайдов."""

		return self.__Chapter["slides"]
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Глава."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Chapter = {
			"id": None,
			"volume": None,
			"number": None,
			"name": None,
			"is_paid": None,
			"translators": [],
			"slides": []	
		}

	def __getitem__(self, key: str) -> bool | int | list | str | None:
		"""
		Возвращает значение ключа из словаря данных главы. Не рекомендуется к использованию!
			key – ключ данных.
		"""

		return self.__Chapter[key]

	def add_extra_data(self, key: str, value: any):
		"""
		Добавляет дополнительные данные о главе.
			key – ключ для доступа;\n
			value – значение.
		"""

		self.__Chapter[key] = value

	def add_translator(self, translator: str):
		"""
		Добавляет переводчика.
			translator – ник переводчика.
		"""

		self.__Chapter["translator"].append(translator)

	def add_slide(self, link: str, width: int | None = None, height: int | None = None):
		"""
		Добавляет данные о слайде.
			link – ссылка на слайд;\n
			width – ширина слайда;\n
			height – высота слайда.
		"""

		SlideInfo = {
			"index": len(self.__Chapter["slides"]) + 1,
			"link": link,
			"width": width,
			"height": height
		}
		if not width: del SlideInfo["width"]
		if not height: del SlideInfo["height"]
		self.__Chapter["slides"].append(SlideInfo)

	def remove_extra_data(self, key: str):
		"""
		Удаляет дополнительные данные о главе.
			key – ключ для доступа.
		"""

		del self.__Chapter[key]

	def set_dict(self, dictionary: dict):
		"""
		Задаёт словарь, используемый в качестве хранилища данных главы.
			dictionary – словарь данных главы.
		"""

		ImportantKeys = ["id", "volume", "number", "name", "is_paid", "translators", "slides"]
		ImportantKeysTypes = [
			[int, None],
			[str, None],
			[str, None],
			[str, None],
			[bool, None],
			[list],
			[list]
		]

		for KeyIndex in range(len(ImportantKeys)):
			if ImportantKeys[KeyIndex] not in dictionary.keys(): raise KeyError(ImportantKeys[KeyIndex])
			if type(ImportantKeys[KeyIndex]) not in ImportantKeysTypes[KeyIndex]: raise TypeError(ImportantKeys)

		self.__Chapter == dictionary.copy()

	def set_id(self, id: int | None):
		"""
		Задаёт уникальный идентификатор главы.
			ID – идентификатор.
		"""

		self.__Chapter["id"] = id

	def set_is_paid(self, is_paid: bool | None):
		"""
		Указывает, является ли глава платной.
			is_paid – состояние: платная ли глава.
		"""

		self.__Chapter["is_paid"] = is_paid

	def set_name(self, name: int | None):
		"""
		Задаёт название главы.
			name – название главы.
		"""

		self.__Chapter["name"] = name

	def set_number(self, number: str | None):
		"""
		Задаёт номер главы.
			number – номер главы.
		"""

		self.__Chapter["number"] = str(number)

	def set_volume(self, volume: str | None):
		"""
		Задаёт номер тома.
			volume – номер тома.
		"""

		self.__Chapter["volume"] = str(volume)

	def to_dict(self) -> dict:
		"""Возвращает словарь данных главы."""

		return self.__Chapter.copy()

class Branch:
	"""Ветвь тайтла."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def chapters_count(self) -> int:
		"""Количество глав."""

		return len(self.__Chapters)

	@property
	def empty_chapters_count(self) -> int:
		"""Количество глав без контента."""

		EmptyChaptersCount = 0

		for CurrentChapter in self.__Chapters:
			if not CurrentChapter.slides: EmptyChaptersCount += 1

		return EmptyChaptersCount

	@property
	def id(self) -> int:
		"""Уникальный идентификатор ветви."""

		return self.__ID
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, id: int):
		"""
		Ветвь тайтла.
			ID – уникальный идентификатор ветви.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__ID = id
		self.__Chapters: list[Chapter] = list()

	def get_chapter_by_id(self, id: int) -> Chapter:
		"""
		Возвращает главу по её уникальному идентификатору.
			id – идентификатор главы.
		"""

		Data = None

		for CurrentChapter in self.__Chapters:
			if CurrentChapter.id == id: Data = CurrentChapter

		if not Data: raise KeyError(id)

		return CurrentChapter
	
	def replace_chapter_by_id(self, chapter: Chapter, id: int):
		"""
		Заменяет главу по её уникальному идентификатору.
			id – идентификатор главы.
		"""

		IsSuccess = False

		for Index in range(len(self.__Chapters)):

			if self.__Chapters[Index].id == id:
				self.__Chapters[Index] = chapter
				IsSuccess = True

		if not IsSuccess: raise KeyError(id)
	
	def to_list(self) -> list[dict]:
		"""Возвращает список словарей данных глав, принадлежащих текущей ветви."""

		BranchList = list()
		for CurrentChapter in self.__Chapters: BranchList.append(CurrentChapter.to_dict())

		return BranchList

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

class Manga:
	"""Манга."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def format(self) -> str:
		"""Формат структуры данных."""

		return self.__Title["format"]

	@property
	def site(self) -> str:
		"""Домен целевого сайта."""

		return self.__Title["site"]

	@property
	def id(self) -> int:
		"""Целочисленный уникальный идентификатор тайтла."""

		return self.__Title["id"]

	@property
	def slug(self) -> int:
		"""Алиас."""

		return self.__Title["slug"]

	@property
	def content_language(self) -> str | None:
		"""Код языка контента по стандарту ISO 639-3."""

		return self.__Title["content_language"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self.__Title["localized_name"]

	@property
	def eng_name(self) -> str | None:
		"""Название на английском."""

		return self.__Title["eng_name"]

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Title["another_names"]

	@property
	def covers(self) -> list[dict]:
		"""Список описаний обложки."""

		return self.__Title["covers"]

	@property
	def authors(self) -> list[str]:
		"""Список авторов."""

		return self.__Title["authors"]

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return self.__Title["publication_year"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self.__Title["description"]

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return self.__Title["age_limit"]

	@property
	def genres(self) -> list[str]:
		"""Список жанров."""

		return self.__Title["genres"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return self.__Title["tags"]

	@property
	def franchises(self) -> list[str]:
		"""Список франшиз."""

		return self.__Title["franchises"]

	@property
	def type(self) -> Types | None:
		"""Тип тайтла."""

		return self.__Title["type"]

	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return self.__Title["status"]

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return self.__Title["is_licensed"]

	@property
	def branches(self) -> list[Branch]:
		"""Список ветвей тайтла."""

		return self.__Branches

	#==========================================================================================#
	# >>>>> LEGACY-КОНВЕРТЕРЫ <<<<< #
	#==========================================================================================#

	def __FromLegacy(manga: dict) -> dict:
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

	def __ToLegacy(manga: dict) -> dict:
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
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckStringsList(self, data: list[str]):
		"""
		Проверяет, содержит ли список только строки.
			data – список объектов.
		"""

		for Element in data:
			if type(Element) != str: raise TypeError(Element)

	def __InitializeRequestor(self) -> WebRequestor:
		"""
		Инициализирует модуль WEB-запросов.
			proxy – данные о прокси.
		"""

		ParserSettings = self.__SystemObjects.manager.get_parser_settings(self.__SystemObjects.PARSER_NAME)
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

	def __UpdateBranchesInfo(self):
		"""Обновляет информацию о ветвях."""

		Branches = list()
		for CurrentBranch in self.__Branches: Branches.append({"id": CurrentBranch.id, "chapters_count": CurrentBranch.chapters_count })
		self.__Title["branches"] = sorted(Branches, key = lambda Value: Value["chapters_count"], reverse = True) 

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
		self.__Branches: list[Branch] = list()
		self.__Title = {
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

	def amend(self, amending_method: function, message: str):
		"""
		Дополняет содержимое подробной информацией.
			amending_method – указатель на метод из парсера для дополнения;\n
			message – сообщение для внутреннего обработчика.
		"""

		self.__Title["content"] = amending_method(self.__Title["content"], message)

	def download_covers(self, directory: str, used_filename: str, message: str):
		"""
		Скачивает обложки.
			directory – директория хранения;\n
			used_filename – используемое имя описательного файла;\n
			message – сообщение для внутреннего обработчика.
		"""

		Requestor = self.__InitializeRequestor()
		CoversDirectory = f"{directory}/{used_filename}/"
		if not os.path.exists(CoversDirectory): os.makedirs(CoversDirectory)
		Clear()
		print(message)

		for CoverIndex in range(len(self.__Title["covers"])):
			Filename = self.__Title["covers"][CoverIndex]["link"].split("/")[-1]
			print(f"Downloading cover: \"{Filename}\"... ", end = "")
			Result = ImagesDownloader(self.__SystemObjects, Requestor).image(
				url = self.__Title["covers"][CoverIndex]["link"],
				directory = CoversDirectory,
				filename = self.__Title["covers"][CoverIndex]["filename"],
				is_full_filename = True
			)
			print(Result.message)
			sleep(0.25)

	def merge(self, directory: str, filename: str):
		"""
		Объединяет данные описательного файла и текущей структуры данных.
			directory – директория хранения;\n
			filename – имя файла.
		"""

		if os.path.exists(f"{directory}/{filename}.json") and not self.__SystemObjects.FORCE_MODE:
			LocalManga = ReadJSON(f"{directory}/{filename}.json")
			if LocalManga["format"] != "melon-manga": LocalManga = LegacyManga.from_legacy(LocalManga)
			LocalContent = dict()
			MergedChaptersCount = 0
			
			for BranchID in LocalManga["content"]:
				for Chapter in LocalManga["content"][BranchID]: LocalContent[Chapter["id"]] = Chapter["slides"]
			
			for BranchID in self.__Title["content"]:
		
				for ChapterIndex in range(len(self.__Title["content"][BranchID])):
				
					if self.__Title["content"][BranchID][ChapterIndex]["id"] in LocalContent.keys():
						ChapterID = self.__Title["content"][BranchID][ChapterIndex]["id"]

						if LocalContent[ChapterID]:
							self.__Title["content"][BranchID][ChapterIndex]["slides"] = LocalContent[ChapterID]
							MergedChaptersCount += 1

			self.__SystemObjects.logger.info("Title: \"" + self.__Title["slug"] + f"\" (ID: " + str(self.__Title["id"]) + f"). Merged chapters count: {MergedChaptersCount}.")

		elif self.__SystemObjects.FORCE_MODE:
			self.__SystemObjects.logger.info("Title: \"" + self.__Title["slug"] + "\" (ID: " + str(self.__Title["id"]) + "). Local data removed.")

	def open(self, directory: str, identificator: int | str, selector_type: By = By.Filename):
		"""
		Считывает локальный описательный файл.
			directory – директория хранения;\n
			identificator – идентификатор тайтла;\n
			selector_type – тип указателя на тайтл.
		"""

		Data = None

		if selector_type == By.Filename:
			Path = f"{directory}/{identificator}.json"

			if os.path.exists(Path):
				Data = ReadJSON(f"{directory}/{identificator}.json")
				
			else:
				self.__SystemObjects.logger.critical("Couldn't open file.")
				raise FileNotFoundError(Path)

		if selector_type == By.Slug:
			LocalTitles = os.listdir(directory)
			LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))

			for File in LocalTitles:
				Path = f"{directory}/{File}"

				if os.path.exists(Path):
					Buffer = ReadJSON(Path)

					if Buffer["slug"] == identificator:
						Data = Buffer
						break

		if selector_type == By.ID:
			LocalTitles = os.listdir(directory)
			LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))

			for File in LocalTitles:
				Path = f"{directory}/{File}"

				if os.path.exists(Path):
					Buffer = ReadJSON(Path)

					if Buffer["id"] == identificator:
						Data = Buffer
						break

		if Data:
			self.__Title = Data
			if self.__Title["format"] != "melon-manga": self.__Title = self.__FromLegacy(Data)
			
		else: raise FileNotFoundError(identificator)

	def repair(self, repairing_method: any, chapter_id: int):
		"""
		Заново получает данные о слайдах в главе.
			repairing_method – указатель на метод из парсера для восстановления;\n
			chapter_id – идентификатор целевой главы.
		"""

		self.__Title["content"] = repairing_method(self.__Title["content"], chapter_id)

	def save(self, directory: str, filename: str, legacy: bool = False):
		"""
		Сохраняет данные манги в описательный файл.
			directory – директория хранения;\n
			filename – имя файла;\n
			legacy – указывает, нужно ли форматировать описательный файл в устаревший формат.
		"""

		Content = dict()
		for CurrentBranch in self.__Branches: Content[str(CurrentBranch.id)] = CurrentBranch.to_list()
		self.__Title["content"] = Content

		for BranchID in self.__Title["content"].keys(): self.__Title["content"][BranchID] = sorted(self.__Title["content"][BranchID], key = lambda Value: (list(map(int, Value["volume"].split("."))), list(map(int, Value["number"].split("."))))) 
		if legacy: self.__Title = self.__ToLegacy(self.__Title)
		if legacy: self.__SystemObjects.logger.info("Title: \"" + self.__Title["slug"] + "\". Converted to legacy format.")
		WriteJSON(f"{directory}/{filename}.json", self.__Title)
		self.__SystemObjects.logger.info("Title: \"" + self.__Title["slug"] + "\" (ID: " + str(self.__Title["id"]) + "). Saved.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str):
		"""
		Добавляет альтернативное название.
			another_name – название.
		"""
		
		if another_name != self.__Title["localized_name"] and another_name != self.__Title["eng_name"]: self.__Title["another_names"].append(another_name)

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
		if not width: del CoverInfo["width"]
		if not height: del CoverInfo["height"]
		self.__Title["covers"].append(CoverInfo)

	def add_author(self, author: str):
		"""
		Добавляет автора.
			author – автор.
		"""

		if author not in self.__Title["authors"]: self.__Title["authors"].append(author)

	def add_genre(self, genre: str):
		"""
		Добавляет жанр.
			genre – жанр.
		"""

		if genre not in self.__Title["genres"]: self.__Title["genres"].append(genre)

	def add_tag(self, tag: str):
		"""
		Добавляет тег.
			tag – тег.
		"""

		if tag not in self.__Title["tags"]: self.__Title["tags"].append(tag)

	def add_franshise(self, franshise: str):
		"""
		Добавляет франшизу.
			franshise – франшиза.
		"""

		if franshise not in self.__Title["franshises"]: self.__Title["franshises"].append(franshise)

	def add_branch(self, branch: Branch):
		"""
		Добавляет ветвь.
			branch – ветвь.
		"""

		if branch not in self.__Branches: self.__Branches.append(branch)
		self.__UpdateBranchesInfo()

	def set_site(self, site: str):
		"""
		Задаёт домен источника.
			site – домен сайта.
		"""

		self.__Title["site"] = site

	def set_id(self, id: int):
		"""
		Задаёт целочисленный уникальный идентификатор тайтла.
			id – идентификатор.
		"""

		self.__Title["id"] = id

	def set_slug(self, slug: str):
		"""
		Задаёт алиас манги.
			slug – алиас.
		"""

		self.__Title["slug"] = slug

	def set_content_language(self, content_language: str | None):
		"""
		Задаёт язык контента по стандарту ISO 639-3.
			content_language – код языка.
		"""

		if type(content_language) == str and len(content_language) != 3: raise TypeError(content_language)
		self.__Title["content_language"] = content_language.lower() if content_language else None

	def set_localized_name(self, localized_name: str | None):
		"""
		Задаёт главное название манги на русском.
			ru_name – название на русском.
		"""

		self.__Title["localized_name"] = localized_name

	def set_en_name(self, en_name: str | None):
		"""
		Задаёт главное название манги на английском.
			en_name – название на английском.
		"""

		self.__Title["en_name"] = en_name

	def set_another_names(self, another_names: list[str]):
		"""
		Задаёт список альтернативных названий на любых языках.
			another_names – список названий.
		"""

		self.__CheckStringsList(another_names)
		self.__Title["another_names"] = another_names

	def set_covers(self, covers: list[dict]):
		"""
		Задаёт список описаний обложек.
			covers – список названий.
		"""

		self.__Title["covers"] = covers

	def set_authors(self, authors: list[str]):
		"""
		Задаёт список авторов.
			covers – список авторов.
		"""

		self.__CheckStringsList(authors)
		self.__Title["authors"] = authors

	def set_publication_year(self, publication_year: int | None):
		"""
		Задаёт год публикации манги.
			publication_year – год.
		"""

		self.__Title["publication_year"] = publication_year

	def set_description(self, description: str | None):
		"""
		Задаёт описание манги.
			description – описание.
		"""

		self.__Title["description"] = description

	def set_age_limit(self, age_limit: int | None):
		"""
		Задаёт возрастной рейтинг.
			age_limit – возрастной рейтинг.
		"""

		self.__Title["age_limit"] = age_limit

	def set_genres(self, genres: list[str]):
		"""
		Задаёт список жанров.
			genres – список жанров.
		"""

		self.__CheckStringsList(genres)
		self.__Title["genres"] = genres

	def set_tags(self, tags: list[str]):
		"""
		Задаёт список тегов.
			tags – список тегов.
		"""

		self.__CheckStringsList(tags)
		self.__Title["tags"] = tags

	def set_franchises(self, franchises: list[str]):
		"""
		Задаёт список франшиз.
			franchises – список франшиз.
		"""

		self.__CheckStringsList(franchises)
		self.__Title["franchises"] = franchises

	def set_type(self, type: Types | None):
		"""
		Задаёт типп манги.
			type – тип.
		"""

		if type: self.__Title["type"] = type.value
		else: self.__Title["type"] = None

	def set_status(self, status: Statuses | None):
		"""
		Задаёт статус манги.
			status – статус.
		"""

		if status: self.__Title["status"] = status.value
		else: self.__Title["status"] = None
		
	def set_is_licensed(self, is_licensed: bool | None):
		"""
		Задаёт статус лицензирования манги.
			is_licensed – статус лицензирования.
		"""

		self.__Title["is_licensed"] = is_licensed