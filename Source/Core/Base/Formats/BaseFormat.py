from Source.Core.Base.Formats.Components.WordsDictionary import CheckLanguageCode
from abc import ABC, abstractmethod

from .Components.Functions import SafelyReadTitleJSON
from .Components.Structs import ChapterSearchResult
from .Components.Enums import By, Statuses

from Source.Core.Base.Parsers.Components.ImagesDownloader import ImageResolution
from Source.Core import Exceptions

from dublib.Methods.Data import RemoveRecurringSubstrings, Zerotify
from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from typing import Any, cast, Sequence, TYPE_CHECKING
from pathlib import Path
from os import PathLike
import hashlib
import json
import os

if TYPE_CHECKING:
	from Source.Core.Base.Parsers.BaseParser import BaseParser
	from Source.Core.SystemObjects import SystemObjects

#==========================================================================================#
# >>>>> ВНУТРЕННИЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Cover:
	"""Обложка."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def link(self) -> str:
		"""Ссылка на изображение."""

		return self.__Link
	
	@property
	def resolution(self) -> ImageResolution | None:
		"""Разрешение изображения."""

		return self.__Resolution

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, link: str):
		"""
		Обложка.

		:param link: Ссылка на обложку.
		:type link: str
		"""

		self.__Link: str = link
		self.__Resolution: ImageResolution | None = None

	def set_resolution(self, resolution: ImageResolution):
		"""
		Задаёт разрешение обложки.

		:param resolution: Разрешение обложки.
		:type resolution: ImageResolution
		"""

		self.__Resolution = resolution

	def to_dict(self) -> dict[str, str | int | None]:
		"""
		Преобразует контейнер в словарное представление.

		:return: Словарное представление данных обложки.
		:rtype: dict[str, str | int | None]
		"""

		Buffer: dict = {
			"link": self.__Link,
			"width": None,
			"height": None
		}

		if self.__Resolution:
			Buffer["width"] = self.__Resolution.width
			Buffer["height"] = self.__Resolution.height

		return Buffer

class Person:
	"""Данные персонажа."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def name(self) -> str:
		"""Имя."""

		return self.__Data["name"]

	@property
	def another_names(self) -> list[str]:
		"""Альтернативные имена."""

		return self.__Data["another_names"]

	@property
	def images(self) -> list[dict]:
		"""Список данных портретов."""

		return self.__Data["images"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self.__Data["description"]
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, name: str):
		"""
		Данные персонажа.
			name – имя персонажа.
		"""

		self.__Data = {
			"name": name,
			"another_names": [],
			"images": [],
			"description": None
		}

	def add_another_name(self, another_name: str):
		"""
		Добавляет альтернативное имя.
			another_name – имя.
		"""
		
		another_name = another_name.strip()
		if another_name and another_name != self.name and another_name not in self.another_names: self.__Data["another_names"].append(another_name)

	def add_image(self, link: str, width: int | None = None, height: int | None = None):
		"""
		Добавляет иллюстрацию персонажа.

		:param link: Ссылка на изображение.
		:type link: str
		:param width: Ширина изображения.
		:type width: int
		:param height: Высота изображения.
		:type height: int
		"""

		CoverInfo: dict[str, int | str | None] = {
			"link": link,
			"width": width,
			"height": height
		}

		self.__Data["images"].append(CoverInfo)

	def set_description(self, description: str | None):
		"""
		Задаёт описание персонажа.

		:param description: Описание.
		:type description: str | None
		"""

		self.__Data["description"] = Zerotify(description)

	def to_dict(self, sizing_images: bool = True) -> dict:
		"""
		Возвращает словарное представление данных персонажа.

		:param sizing_images: Указывает, нужно ли указать размеры изображений персонажа.
		:type sizing_images: bool
		:return: Словарное представление данных персонажа.
		:rtype: dict
		"""

		Data = self.__Data.copy()

		if not sizing_images:
			for Index in range(len(Data["images"])):
				del Data["images"][Index]["width"]
				del Data["images"][Index]["height"]

		return Data

class BaseChapter(ABC):
	"""Базовая глава."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def id(self) -> int:
		"""Уникальный идентификатор главы."""

		return self._Data["id"]
	
	@property
	def slug(self) -> str | None:
		"""Алиас главы."""

		return self._Data["slug"]

	@property
	def volume(self) -> str | None:
		"""Номер тома."""

		return self._Data["volume"]
	
	@property
	def number(self) -> str | None:
		"""Номер главы."""

		return self._Data["number"]
	
	@property
	def name(self) -> str | None:
		"""Название главы."""

		return self._Data["name"]

	@property
	def is_empty(self) -> bool:
		"""Состояние: пуста ли глава."""

		return self._IsEmpty()

	@property
	def is_paid(self) -> bool | None:
		"""Состояние: платная ли глава."""

		return self._Data["is_paid"]
	
	@property
	def workers(self) -> tuple[str]:
		"""Набор идентификаторов лиц, адаптировавших контент."""

		return tuple(self._Data["workers"])
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PrettyNumber(self, number: float | int | str | None) -> str | None:
		"""
		Преобразует номер главы или тома в корректное значение.

		:param number: Номер главы или тома.
		:type number: float | int | str | None
		:return: Откорректированный номер.
		:rtype: str | None
		"""

		if number is None: number = ""
		elif type(number) is not str: number = str(number)
		if "-" in number: number = number.split("-")[0]
		number = number.strip("\t .\n")
		Number = cast(str | None, Zerotify(number))

		return Number

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _Clear(self):
		"""Очищает контент главы."""

		pass

	@abstractmethod
	def _FromDict(self, data: dict):
		"""
		Заполняет данные главы из словаря.

		:param data: Словарь данных главы.
		:type data: dict
		"""

		pass

	@abstractmethod
	def _IsEmpty(self) -> bool:
		"""
		Проверяет, пустая ли глава.

		:return: Состояние: пуста ли глава.
		:rtype: bool
		"""

		return False

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _PreFormatter(self):
		"""Метод, запускающийся перед генерацией словарного представления объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, parser: "BaseParser", chapter_id: int):
		"""
		Базовая глава.

		:param parser: Парсер.
		:type parser: BaseParser
		:param chapter_id: ID главы.
		:type chapter_id: int
		"""

		self.__Parser = parser

		self._Data: dict[str, Any] = {
			"id": chapter_id,
			"slug": None,
			"volume": None,
			"number": None,
			"name": None,
			"is_paid": None,
			"workers": []
		}

		self._PostInitMethod()

	def add_extra_data(self, key: str, value: Any):
		"""
		Добавляет дополнительные данные о главе.

		:param key: Ключ.
		:type key: str
		:param value: Значение.
		:type value: Any
		"""

		self._Data[key] = value

	def add_worker(self, worker: str):
		"""
		Добавляет идентификатор лица, адаптировавшего контент.

		:param worker: Идентификатор.
		:type worker: str
		"""

		if worker not in self._Data["workers"]:
			self._Data["workers"].append(worker)

	def clear(self):
		"""Удаляет содержимое главы."""

		self._Clear()

	def from_dict(self, data: dict):
		"""
		Заполняет данные главы из словаря.

		:param data: Словарь данных главы.
		:type data: dict
		"""

		self._FromDict(data)

	def remove_extra_data(self, key: str):
		"""
		Удаляет дополнительные данные главы.

		:param key: Ключ, под которым хранятся дополнительные данные.
		:type key: str
		"""

		if key in self._Data:
			del self._Data[key]

	def set_is_paid(self, is_paid: bool | None):
		"""
		Указывает, является ли глава платной.

		:param is_paid: Состояние: платная ли глава.
		:type is_paid: bool | None
		"""

		self._Data["is_paid"] = is_paid

	def set_name(self, name: str | None):
		"""
		Задаёт название главы.

		:param name: Название главы.
		:type name: str | None
		"""

		name = Zerotify(name)
		if name: name = name.strip()
		
		if name and self.__Parser.settings.common.pretty:
			if name.endswith("..."): name = name.rstrip(".") + "…"
			else: name = name.rstrip(".–")
		
			name = name.replace("\u00A0", " ")
			name = RemoveRecurringSubstrings(name, " ")

			name = name.rstrip(":.")

		self._Data["name"] = name

	def set_number(self, number: float | int | str | None):
		"""
		Задаёт номер главы.

		:param number: Номер главы.
		:type number: float | int | str | None
		"""
		
		self._Data["number"] = self._PrettyNumber(number)

	def set_workers(self, workers: Sequence[str]):
		"""
		Задаёт идентификаторы лиц, адаптировавших контент.

		:param workers: Набор идентификаторов.
		:type workers: Sequence[str]
		"""

		for Worker in workers:
			self.add_worker(Worker)

	def set_slug(self, slug: str | None):
		"""
		Задаёт алиас главы.

		:param slug: Алиас главы.
		:type slug: str | None
		"""

		self._Data["slug"] = slug

	def set_volume(self, volume: float | int | str | None):
		"""
		Задаёт номер тома, к которому принадлежит глава.

		:param volume: Номер тома.
		:type volume: float | int | str | None
		"""

		self._Data["volume"] = self._PrettyNumber(volume)

	def to_dict(self) -> dict:
		"""Возвращает копию словаря данных главы."""

		self._PreFormatter()

		return self._Data.copy()
	
class BaseBranch(ABC):
	"""Базовая ветвь."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def chapters(self) -> tuple[BaseChapter, ...]:
		"""Последовательность глав."""

		return tuple(self._Chapters)

	@property
	def chapters_count(self) -> int:
		"""Количество глав."""

		return len(self._Chapters)

	@property
	def empty_chapters_count(self) -> int:
		"""Количество глав без контента."""

		return sum(1 for CurrentChapter in self._Chapters if CurrentChapter.is_empty)

	@property
	def id(self) -> int:
		"""Уникальный идентификатор ветви."""

		return self._ID

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, branch_id: int):
		"""
		Базовая ветвь.

		:param branch_id: ID ветви.
		:type branch_id: int
		"""

		self._ID = branch_id
		self._Chapters: list[BaseChapter] = list()

	def add_chapter(self, chapter: BaseChapter):
		"""
		Добавляет главу в ветвь. Если глава с таким ID уже существует, добавление не происходит.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:raises ParsingError: Выбрасывается при отсутствии у добавляемой главы ID.
		"""

		if chapter.id is None: raise Exceptions.Parsers.ParsingError("Chapter must have unique ID.")
		if chapter.id in tuple(Value.id for Value in self._Chapters): return
		self._Chapters.append(chapter)

	def get_chapter_by_id(self, id: int) -> BaseChapter:
		"""
		Возвращает главу по её уникальному идентификатору.

		:param id: ID главы.
		:type id: int
		:raises KeyError: Выбрасывается при отсутствии главы в ветви.
		:return: Глава.
		:rtype: BaseChapter
		"""

		SearchResult: BaseChapter | None = None

		for CurrentChapter in self._Chapters:
			if CurrentChapter.id == id:
				SearchResult = CurrentChapter
				break

		if not SearchResult: raise KeyError(id)

		return SearchResult
	
	def remove_chapter(self, id: int):
		"""
		Удаляет главу из ветви.

		:param id: ID главы.
		:type id: int
		:raises KeyError: ВЫбрасывается при отсутствии главы в ветви.
		"""
		
		TargetChapter = self.get_chapter_by_id(id)
		self._Chapters.remove(TargetChapter)

	def replace_chapter_by_id(self, chapter: BaseChapter, id: int):
		"""
		Заменяет главу в ветви по её ID.

		:param chapter: Новая глава.
		:type chapter: BaseChapter
		:param id: ID заменяемой главы.
		:type id: int
		:raises KeyError: Выбрасывается при отсутствии заменяемой главы в ветви.
		"""

		IsSuccess = False

		for Index in range(len(self._Chapters)):

			if self._Chapters[Index].id == id:
				self._Chapters[Index] = chapter
				IsSuccess = True

		if not IsSuccess: raise KeyError(id)
	
	def reverse(self):
		"""Инвертирует порядок глав в ветви."""

		self._Chapters = list(reversed(self._Chapters))

	def sort(self):
		"""
		По умолчанию помещает главы в порядке возрастания их нумерации.

		Переопределите данный метод для использования иных алгоритмов сортировки.
		"""

		self._Chapters = list(sorted(
			self._Chapters,
			key = lambda Value: (
				list(map(int, Value.volume.split(".") if Value.volume else "")),
				list(map(int, Value.number.split(".") if Value.number else ""))
			)
		))

	def to_list(self) -> list[dict]:
		"""Возвращает список словарей данных глав, принадлежащих текущей ветви."""

		BranchList = list()
		for CurrentChapter in self._Chapters: BranchList.append(CurrentChapter.to_dict())

		return BranchList
	
#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseTitle(ABC):
	"""Базовый тайтл."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def empty_chapters_count(self) -> int:
		"""Количество глав без контента во всех ветвях."""

		return sum(Branch.empty_chapters_count for Branch in self._Branches)

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТАЙТЛА <<<<< #
	#==========================================================================================#

	@property
	def site(self) -> str | None:
		"""Домен целевого сайта."""

		return self._Data["site"]

	@property
	def id(self) -> int | None:
		"""Целочисленный уникальный идентификатор тайтла."""

		return self._Data["id"]

	@property
	def slug(self) -> str | None:
		"""Алиас."""

		return self._Data["slug"]
	
	@property
	def content_language(self) -> str | None:
		"""Код языка контента по стандарту ISO 639-3."""

		return self._Data["content_language"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Data["localized_name"]

	@property
	def eng_name(self) -> str | None:
		"""Название на английском."""

		return self._Data["eng_name"]

	@property
	def another_names(self) -> tuple[str, ...]:
		"""Последовательность альтернативных названий."""

		return tuple(self._Data["another_names"])
	
	@property
	def covers(self) -> tuple[Cover, ...]:
		"""Последовательность описаний обложки."""

		return tuple(self._Covers)

	@property
	def authors(self) -> tuple[str, ...]:
		"""Последовательность авторов."""

		return tuple(self._Data["authors"])

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return self._Data["publication_year"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self._Data["description"]

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return self._Data["age_limit"]

	@property
	def genres(self) -> tuple[str, ...]:
		"""Последовательность жанров."""

		return tuple(self._Data["genres"])

	@property
	def tags(self) -> tuple[str, ...]:
		"""Последовательность тегов."""

		return tuple(self._Data["tags"])

	@property
	def franchises(self) -> tuple[str, ...]:
		"""Последовательность франшиз."""

		return tuple(self._Data["franchises"])
	
	@property
	def perons(self) -> tuple[Person, ...]:
		"""Последовательность персонажей."""

		return tuple(self._Persons)
	
	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return self._Data["status"]

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return self._Data["is_licensed"]

	@property
	def branches(self) -> tuple[BaseBranch, ...]:
		"""Последовательность ветвей тайтла."""

		return tuple(self._Branches)
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def _IsLocalFileEqual(self) -> bool:
		"""
		Проверяет, идентичны ли данные тайтла локальным данным.

		:return: Возвращает `True`, если данные идентичны, или `False` в противном случа и при отсутствии локального файла.
		:rtype: bool
		"""

		if not self._DataPath or not self._DataPath.exists(): return False

		LocalHasher = hashlib.sha256(str(ReadJSON(self._DataPath)).encode())
		MemoryHasher = hashlib.sha256(str(self._Data).encode())

		return LocalHasher.hexdigest() == MemoryHasher.hexdigest()

	def _SearchFileInDirectory(self, directory: str | PathLike[str], identificator: str, type: By) -> dict | None:
		"""
		Находит файл JSON в директории по идентификатору определённого типа.

		:param directory: Путь к каталогу файлов.
		:type directory: str | PathLike[str]
		:param identificator: Идентификатор: ID или алиас.
		:type identificator: str
		:param type: Тип идентификатора: `By.Slug` или `By.ID`.
		:type type: By
		:return: Содержимое файла или `None` при отсутствии оного или ошибке.
		:rtype: dict | None
		"""

		for Element in os.scandir(directory):
			if not Element.is_file() or not Element.name.endswith(".json"):
				continue

			try: 
				Data = SafelyReadTitleJSON(Element.path)
				if Data.get(type.value) == identificator:
					return Data

			except (json.JSONDecodeError, Exceptions.Parsers.UnsupportedFormat): pass

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ПРЕОБРАЗОВАНИЯ СЛОВАРНОЙ СТРУКТУРЫ <<<<< #
	#==========================================================================================#

	def _ParseCovers(self):
		"""Парсит обложки в объектные представления."""

		self._Covers.clear()

		for CoverData in self._Data["covers"]:
			CoverData = cast(dict, CoverData)
			Buffer = Cover(CoverData["link"])
			Width, Height = CoverData.get("width"), CoverData.get("height")

			if all((Width, Height)):
				Buffer.set_resolution(ImageResolution(cast(int, Width), cast(int, Height)))

			self._Covers.append(Buffer)

	def _ParsePersons(self):
		"""Парсит персонажей в объектные представления."""

		self._Persons.clear()

		for PersonData in self._Data["persons"]:
			CoverData = cast(dict, PersonData)
			Buffer = Person(CoverData["name"])
			
			AnotherNames = CoverData.get("another_names") or tuple()
			Images = CoverData.get("images") or tuple()
			Description = CoverData.get("description")

			for AnotherName in AnotherNames:
				Buffer.add_another_name(AnotherName)

			for ImageData in Images:
				ImageData = cast(dict, ImageData)
				Buffer.add_image(ImageData["link"], ImageData.get("width"), ImageData.get("height"))

			if Description:
				Buffer.set_description(Description)

			self._Persons.append(Buffer)

	def _UpdateBranchesInfo(self):
		"""Обновляет информацию о ветвях во внутреннем словарном хранилище тайтла."""

		Branches = list()
		for CurrentBranch in self._Branches: Branches.append({"id": CurrentBranch.id, "chapters_count": CurrentBranch.chapters_count})
		self._Data["branches"] = sorted(Branches, key = lambda Value: Value["chapters_count"], reverse = True)

	def _UpdateContent(self, brach_id: int | None = None, sorting: bool = True):
		"""
		Обновляет контент во внутреннем словарном хранилище данных тайтла.

		:param brach_id: Если указать ID ветви, будет обновлена только одна ветвь.
		:type brach_id: int | None
		:param sorting: Указывает, нужно ли провести сортировку глав на основе их нумерации.
		:type sorting: bool
		"""

		for CurrentBranch in self._Branches:
			if brach_id and brach_id == CurrentBranch.id or not brach_id:
				if sorting: CurrentBranch.sort()
				self._Data["content"][str(CurrentBranch.id)] = CurrentBranch.to_list()
				if brach_id: break

	def _UpdateCovers(self):
		"""Обновляет данные обложек во внутреннем словарном хранилище данных тайтла."""

		for CurrentCover in self._Covers:
			self._Data["covers"].append(CurrentCover.to_dict())

	def _UpdatePersons(self):
		"""Обновляет данные персонажей во внутреннем словарном хранилище данных тайтла."""

		self._Data["persons"] = list()

		for CurrentPerson in self._Persons:
			self._Data["persons"].append(CurrentPerson.to_dict(self._Parser.settings.common.sizing_images))

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenerateTitleData(self) -> dict[str, Any]:
		"""
		Генерирует базовое словарное представление тайтла.

		:return: Базовое словарное представление тайтла.
		:rtype: dict[str, Any]
		"""

		return {
			"format": None,
			"site": self._Parser.manifest.site,
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

			"status": None,
			"is_licensed": None,
			
			"genres": [],
			"tags": [],
			"franchises": [],
			"persons": [],
			
			"branches": [],
			"content": {} 
		}

	@abstractmethod
	def _ParseBranchesToObjects(self):
		"""Преобразует данные ветвей в объекты."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, parser: "BaseParser", slug: str):
		"""
		Базовый тайтл.

		:param parser: Парсер.
		:type parser: BaseParser
		"""

		self._Parser = parser

		self._SystemObjects = parser.source_operator.system_objects
		
		self._DataPath: Path = self._Parser.settings.directories.titles / f"{slug}.json"
		self._Data: dict[str, Any] = self._GenerateTitleData()
		self._Data["slug"] = slug

		self._Branches: list[BaseBranch] = list()
		self._Persons: list[Person] = list()
		self._Covers: list[Cover] = list()

		self._PostInitMethod()

	def find_chapter_by_id(self, chapter_id: int) -> ChapterSearchResult | None:
		"""
		Ищет главу по её ID.

		:param chapter_id: ID главы.
		:type chapter_id: int
		:return: Результат поиска.
		:rtype: ChapterSearchResult | None
		"""

		BranchResult = None
		ChapterResult = None

		for CurrentBranch in self._Branches:
			for CurrentChapter in CurrentBranch.chapters:
				if CurrentChapter.id == chapter_id:
					BranchResult = CurrentBranch
					ChapterResult = CurrentChapter
					break

		if all((BranchResult, ChapterResult)):
			return ChapterSearchResult(cast(BaseBranch, BranchResult), ChapterResult) if ChapterResult else None

		return None

	def load_data(self, identificator: int | str, selector_type: By = By.Slug) -> bool:
		"""
		Открывает локальный JSON файл и интерпретирует его данные.

		:param identificator: Идентификатор тайтла: ID или алиас.
		:type identificator: int | str
		:param selector_type: Режим поиска файла. По умолчанию `By.Slug` – идентификатор соответствует алиасу тайтла.
		:type selector_type: By
		:raises JSONDecodeError: Ошибка десериализации JSON.
		:raises UnsupportedFormat: Неподдерживаемый формат JSON.
		"""

		DataBuffer: dict = dict()
		TitlesDirectory = self._Parser.settings.directories.titles
		Journal = self._Parser.source_operator.shared_data.journal
		FilePath: Path | None = TitlesDirectory / f"{identificator}.json"

		match selector_type:

			case By.Filename:
				FilePath = TitlesDirectory / f"{identificator}.json"
				DataBuffer = SafelyReadTitleJSON(FilePath)

			case By.Slug:
				if self._Parser.settings.common.use_id_as_filename:
					ID = Journal.get_id_by_slug(str(identificator))
					if ID:
						FilePath = TitlesDirectory / f"{ID}.json"
						if FilePath.exists():
							DataBuffer = SafelyReadTitleJSON(FilePath)
				else:
					FilePath = TitlesDirectory / f"{identificator}.json"
					if FilePath.exists():
						DataBuffer = SafelyReadTitleJSON(FilePath)
				
				if not DataBuffer:
					DataBuffer = self._SearchFileInDirectory(TitlesDirectory, str(identificator), By.Slug) or dict()

			case By.ID:
				if not self._Parser.settings.common.use_id_as_filename:
					Slug = Journal.get_slug_by_id(int(identificator))
					if Slug:
						FilePath = TitlesDirectory / f"{Slug}.json"
						if FilePath.exists():
							DataBuffer = SafelyReadTitleJSON(FilePath)
				else:
					FilePath = TitlesDirectory / f"{identificator}.json"
					if FilePath.exists():
						DataBuffer = SafelyReadTitleJSON(FilePath)
					
				if not DataBuffer:
					DataBuffer = self._SearchFileInDirectory(TitlesDirectory, str(identificator), By.ID) or dict()

		if DataBuffer:
			self._Data = self._Data | DataBuffer

		self._ParseCovers()
		self._ParsePersons()
		self._ParseBranchesToObjects()

		return bool(DataBuffer)

	def save(self, sorting: bool = False) -> bool:
		"""
		Сохраняет данные тайтла в локальный файл JSON.

		:param sorting: Указывает, нужно ли провести сортировку глав на основе их нумерации.
		:type sorting: bool
		:return: Возвращает `True`, если файл сохранён, и `False`, если изменений из-за отсутствия изменений запись не выполнялась.
		:rtype: bool
		"""

		self._UpdateCovers()
		self._UpdatePersons()
		self._UpdateBranchesInfo()
		self._UpdateContent(sorting = sorting)

		IsLocalFileEqual = self._IsLocalFileEqual()

		if not IsLocalFileEqual:
			WriteJSON(self._DataPath, self._Data)

		if all((self.id, self.slug)):
			self._Parser.source_operator.shared_data.journal.update(cast(int, self.id), cast(str, self.slug))

		return IsLocalFileEqual

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str):
		"""
		Добавляет альтернативное название.

		:param another_name: Название.
		:type another_name: str
		"""
		
		another_name = another_name.strip()
		if another_name != self._Data["localized_name"] and another_name != self._Data["eng_name"] and another_name:
			self._Data["another_names"].append(another_name)

	def add_cover(self, cover: Cover):
		"""
		Добавляет обложку.

		:param cover: Обложка.
		:type cover: Cover
		:raises ValueError: Отсутствует ссылка на обложку.
		"""

		if not cover.link:
			raise ValueError("Cover must have a link.")
		
		self._Covers.append(cover)

	def add_author(self, author: str):
		"""
		Добавляет автора.

		:param author: Имя автора.
		:type author: str
		"""

		author = author.strip()
		if author and author not in self._Data["authors"]:
			self._Data["authors"].append(author)

	def add_genre(self, genre: str):
		"""
		Добавляет жанр.

		:param genre: Жанр.
		:type genre: str
		"""

		genre = genre.strip()
		if genre not in self._Data["genres"]:
			self._Data["genres"].append(genre)

	def add_tag(self, tag: str):
		"""
		Добавляет тег.

		:param tag: Тег.
		:type tag: str
		"""

		tag = tag.strip()
		if tag not in self._Data["tags"]:
			self._Data["tags"].append(tag)

	def add_franshise(self, franshise: str):
		"""
		Добавляет франшизу.

		:param franshise: Франшиза.
		:type franshise: str
		"""

		franshise = franshise.strip()
		if franshise and franshise not in self._Data["franshises"]:
			self._Data["franshises"].append(franshise)

	def add_person(self, person: Person):
		"""
		Добавляет персонажа.

		:param person: Персонаж.
		:type person: Person
		"""
		
		if person not in self._Persons:
			self._Persons.append(person)

	def add_branch(self, branch: BaseBranch):
		"""
		Добавляет ветвь.

		:param branch: Ветвь контента.
		:type branch: BaseBranch
		:raises ParsingError: Ветвь не имеет ID или ветвь с таким ID уже добавлена в тайтл.
		"""

		if not branch.id:
			Exceptions.Parsers.ParsingError("Branch must have ID.")
		if branch.id in tuple(Element.id for Element in self._Branches):
			raise Exceptions.Parsers.ParsingError("Branch with same ID already in title.")
		
		self._Branches.append(branch)
		self._Branches = list(sorted(self._Branches, key = lambda Value: Value.chapters_count, reverse = True))

	def set_site(self, site: str | None):
		"""
		Задаёт домен сайта-источника.

		:param site: Домен сайта.
		:type site: str | None
		"""

		self._Data["site"] = site

	def set_id(self, id: int | None):
		"""
		Задаёт ID тайтла.

		:param id: ID тайтла.
		:type id: int | None
		"""

		self._Data["id"] = id

	def set_content_language(self, language_code: str | None):
		"""
		Задаёт язык контента по стандарту ISO 639-3.

		:param original_language: Код языка.
		:type original_language: str | None
		:raise ValueError: Выбрасывается при несоответствии кода языка стандарту.
		"""

		if language_code:
			CheckLanguageCode(language_code)
		self._Data["content_language"] = language_code

	def set_localized_name(self, localized_name: str | None):
		"""
		Задаёт локализованное название тайтла.

		:param localized_name: Локализованное название.
		:type localized_name: str | None
		"""

		self._Data["localized_name"] = localized_name.strip() if localized_name else None

	def set_eng_name(self, eng_name: str | None):
		"""
		Задаёт название на английском языке.

		:param eng_name: Название на английском языке.
		:type eng_name: str | None
		"""

		self._Data["eng_name"] = eng_name.strip() if eng_name else None

	def set_another_names(self, another_names: Sequence[str]):
		"""
		Задаёт набор альтернативных названий.

		:param another_names: Набор альтернативных названий.
		:type another_names: Sequence[str]
		"""

		for Name in another_names:
			self.add_another_name(Name)

	def set_covers(self, covers: Sequence[Cover]):
		"""
		Задаёт последовательность обложек.

		:param covers: Последовательность обложек.
		:type covers: Sequence[Cover]
		:raises ValueError: Выбрасывается при отсутствии ссылки в данных обложки.
		"""

		for CurrentCover in covers:
			self.add_cover(CurrentCover)

	def set_authors(self, authors: Sequence[str]):
		"""
		Задаёт список авторов.

		:param authors: Список авторов.
		:type authors: Sequence[str]
		"""

		for Author in authors:
			self.add_author(Author)

	def set_publication_year(self, publication_year: int):
		"""
		Задаёт год публикации тайтла.

		:param publication_year: Год публикации тайтла.
		:type publication_year: int
		"""

		self._Data["publication_year"] = publication_year

	def set_description(self, description: str | None):
		"""
		Задаёт описание тайтла.

		:param description: Описание тайтла.
		:type description: str | None
		"""

		self._Data["description"] = description.strip() if description else None

	def set_age_limit(self, age_limit: int | None):
		"""
		Задаёт возрастной рейтинг.

		:param age_limit: Возрастной рейтинг.
		:type age_limit: int | None
		"""

		self._Data["age_limit"] = age_limit

	def set_genres(self, genres: Sequence[str]):
		"""
		Задаёт список жанров.

		:param genres: Список жанров.
		:type genres: Sequence[str]
		"""

		for Genre in genres:
			self.add_genre(Genre)

	def set_tags(self, tags: Sequence[str]):
		"""
		Задаёт список тегов.

		:param tags: Список тегов.
		:type tags: Sequence[str]
		"""

		for Tag in tags:
			self.add_tag(Tag)

	def set_franchises(self, franchises: Sequence[str]):
		"""
		Задаёт список франшиз.

		:param franchises: Список франшиз.
		:type franchises: Sequence[str]
		"""

		for Franchise in franchises:
			self.add_franshise(Franchise)

	def set_persons(self, persons: Sequence[Person]):
		"""
		Задаёт список персонажей.

		:param persons: Список персонажей.
		:type persons: Sequence[Person]
		"""
		
		for CurrentPerson in persons:
			self.add_person(CurrentPerson)

	def set_status(self, status: Statuses | None):
		"""
		Задаёт статус тайтла.

		:param status: Статус тайтла.
		:type status: Statuses | None
		"""

		self._Data["status"] = status.value if status else None
	
	def set_is_licensed(self, is_licensed: bool | None):
		"""
		Задаёт состояние: лицензирован ли тайтл в источнике.

		:param is_licensed: Состояние: лицензирован ли тайтл в источнике.
		:type is_licensed: bool | None
		"""

		self._Data["is_licensed"] = is_licensed