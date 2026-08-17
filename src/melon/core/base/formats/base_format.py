import hashlib
import json
import os
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, Sequence, cast

import orjson

from dublib.functions.data import (
	InsertDictionaryAfterKey,
	RemoveRecurringSubstrings,
	Zerotify,
)
from dublib.functions.filesystem import ReadJSON, WriteJSON
from dublib.validators import Validator_Domain

from ....core import exceptions
from ....core.base.parsers.components.images_downloader import ImageData
from ....core.base.parsers.components.words_dictionary import CheckLanguageCode
from .components.enums import By, Statuses
from .components.structs import ChapterSearchResult

if TYPE_CHECKING:
	from ....core.base.parsers.base_parser import BaseParser

#==========================================================================================#
# >>>>> ВНУТРЕННИЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

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
	def images(self) -> list[ImageData]:
		"""Список данных портретов."""

		return self.__Images.copy()

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

		self.__Data: dict = {
			"name": name,
			"another_names": [],
			"images": [],
			"description": None
		}

		self.__Images: list[ImageData] = []

	def add_another_name(self, another_name: str):
		"""
		Добавляет альтернативное имя.
			another_name – имя.
		"""
		
		another_name = another_name.strip()
		if another_name and another_name != self.name and another_name not in self.another_names:
			self.__Data["another_names"].append(another_name)

	def add_image(self, image: ImageData):
		"""
		Добавляет иллюстрацию персонажа.

		:param image: Данные изображения.
		:type image: ImageData
		"""

		self.__Images.append(image)

	def find_image_by_link(self, link: str) -> ImageData | None:
		"""
		Производит поиск изображения по ссылке.

		:param link: Ссылка на изображение.
		:type link: str
		:return: Изображение или `None` при отсутствии оного.
		:rtype: ImageData | None
		"""

		for CurrentImage in self.__Images:
			if CurrentImage.link == link:
				return CurrentImage
			
		return None

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

		:param sizing_images: Указывает, нужно ли сохранять ключи разрешения изображений персонажа.
		:type sizing_images: bool
		:return: Словарное представление данных персонажа.
		:rtype: dict
		"""

		Buffer = self.__Data.copy()
		
		for Index in range(len(self.__Images)):
			Image = self.__Images[Index]
			Buffer["images"].append(Image.to_dict(sizing = sizing_images))

		return Buffer

class ExtraData:
	"""Дополнительные данные главы."""

	def __init__(self, base_keys: Sequence[str]):
		"""
		Дополнительные данные главы.

		:param base_keys: Последовательность базовых ключей, которые не могут быть использованы в дополнительных данных.
		:type base_keys: Sequence[str]
		"""

		self.__BaseKeys = base_keys

		self.__Data: dict = {}

	def clear(self):
		"""Удаляет все дополнительные данные."""

		self.__Data.clear()

	def exists(self, key: str) -> bool:
		"""
		Проверяет существования дополнительных данных.

		:param key: Проверяемый ключ.
		:type key: str
		:return: Возвращает `True`, если ключ найден.
		:rtype: bool
		:raises ValueError: Ключ зарезервирован обязательными значениями.
		"""

		if key in self.__BaseKeys:
			raise ValueError("Key ir reserved by important values, not extra.")

		return key in self.__Data

	def from_dict(self, data: dict):
		"""
		Копирует все пары ключ-значение, ключи которых не являются обязательными, в дополнительные данные.

		:param data: Словарь данных главы.
		:type data: dict
		"""

		for Key in data.keys():
			if Key not in self.__BaseKeys:
				self.set(Key, data[Key])

	def get(self, key: str) -> Any:
		"""
		Возвращает дополнительные данные главы.
		
		:param key: Ключ, под которым хранятся дополнительные данные.
		:type key: str
		:return: Дополнительные данные.
		:rtype: Any
		:raises KeyError: Ключ не найден.
		"""

		return self.__Data[key]

	def remove(self, key: str):
		"""
		Удаляет дополнительные данные главы. Игнорирует отсутствие ключа.
		
		:param key: Ключ, под которым хранятся дополнительные данные.
		:type key: str
		"""

		if key in self.__Data:
			del self.__Data[key]

	def set(self, key: str, value: Any):
		"""
		Задаёт дополнительные данные.

		:param key: Ключ.
		:type key: str
		:param value: Значение.
		:type value: Any
		:raises KeyError: Ключ используется для обязательных полей данных.
		"""

		if key in self.__BaseKeys:
			raise KeyError(key)
	
		self.__Data[key] = value

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""
	
		return self.__Data.copy()

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
	
	@property
	def extra_data(self) -> ExtraData:
		"""Дополнительные данные главы."""

		return self._ExtraData

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

		self._Parser = parser

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
		self._ExtraData = ExtraData(tuple(self._Data.keys()))

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
		self.extra_data.from_dict(data)

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
		
		if name and self._Parser.settings.common.pretty:
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

		return InsertDictionaryAfterKey(self._Data.copy(), self.extra_data.to_dict(), "workers")

class BaseBranch(ABC):
	"""Базовая ветвь."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def chapters(self) -> tuple[BaseChapter, ...]:
		"""Последовательность глав."""

		return tuple(self._Chapters.values())

	@property
	def chapters_count(self) -> int:
		"""Количество глав."""

		return len(self._Chapters.values())

	@property
	def empty_chapters_count(self) -> int:
		"""Количество глав без контента."""

		return sum(1 for CurrentChapter in self._Chapters.values() if CurrentChapter.is_empty)

	@property
	def id(self) -> int:
		"""Уникальный идентификатор ветви."""

		return self._ID

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _FromSequence(self, chapters: Sequence[BaseChapter]) -> dict[int, BaseChapter]:
		"""
		Преобразует последовательность глав в словарь.

		:param chapters: Последовательность глав.
		:type chapters: Sequence[BaseChapter]
		:return: Словарь глав.
		:rtype: dict[int, BaseChapter]
		"""

		return {CurrentChapter.id: CurrentChapter for CurrentChapter in chapters}

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
		self._Chapters: dict[int, BaseChapter] = {}

	def add_chapter(self, chapter: BaseChapter):
		"""
		Добавляет главу в ветвь. Если глава с таким ID уже существует, добавление не происходит.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:raises ParsingError: Выбрасывается при отсутствии у добавляемой главы ID.
		"""

		if chapter.id is None:
			raise exceptions.parsers.ParsingError("Chapter must have unique ID.")
		
		if chapter.id in tuple(Value.id for Value in self._Chapters.values()):
			return
		
		self._Chapters[chapter.id] = chapter

	def get_chapter_by_id(self, id: int) -> BaseChapter:
		"""
		Возвращает главу по её уникальному идентификатору.

		:param id: ID главы.
		:type id: int
		:return: Глава.
		:rtype: BaseChapter
		:raises KeyError: Глава не найдена.
		"""

		return self._Chapters[id]
	
	def has_chapter(self, id: int) -> bool:
		"""
		Проверяет, содержится ли глава с таким ID в ветви.

		:param id: ID главы.
		:type id: int
		:return: Возвращает `True`, если глава с таким ID присутствует.
		:rtype: bool
		"""

		return id in self._Chapters
	
	def remove_chapter(self, id: int):
		"""
		Удаляет главу из ветви.

		:param id: ID главы.
		:type id: int
		:raises KeyError: Глава не найдена.
		"""
		
		del self._Chapters[id]

	def replace_chapter_by_id(self, chapter: BaseChapter, id: int):
		"""
		Заменяет главу в ветви по её ID.

		:param chapter: Новая глава.
		:type chapter: BaseChapter
		:param id: ID заменяемой главы.
		:type id: int
		:raises KeyError: Глава не найдена.
		"""

		self.get_chapter_by_id(id)
		self._Chapters[id] = chapter
	
	def reverse(self):
		"""Инвертирует порядок глав в ветви."""

		self._Chapters = self._FromSequence(tuple(reversed(self._Chapters.values())))

	def sort(self):
		"""
		По умолчанию помещает главы в порядке возрастания их нумерации.

		Переопределите данный метод для использования иных алгоритмов сортировки.
		"""

		self._Chapters = self._FromSequence(sorted(
			self._Chapters.values(),
			key = lambda Value: (
				list(map(int, Value.volume.split(".") if Value.volume else "")),
				list(map(int, Value.number.split(".") if Value.number else ""))
			)
		))

	def to_list(self) -> list[dict]:
		"""Возвращает список словарей данных глав, принадлежащих текущей ветви."""

		BranchList = []
		for CurrentChapter in self._Chapters.values():
			BranchList.append(CurrentChapter.to_dict())

		return BranchList
	
#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseTitle(ABC):
	"""Базовый тайтл."""

	_IsLocalFileLoaded: bool

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def chapters_count(self) -> int:
		"""Количество глав во всех ветвях."""

		return sum(Branch.chapters_count for Branch in self._Branches.values())

	@property
	def empty_chapters_count(self) -> int:
		"""Количество глав без контента во всех ветвях."""

		return sum(Branch.empty_chapters_count for Branch in self._Branches.values())

	@property
	def is_local_file_loaded(self) -> bool:
		"""Состояние: считывались ли данные из локального файла."""

		return self._IsLocalFileLoaded

	@property
	def path(self) -> Path:
		"""Путь к файлу."""

		return self._Parser.settings.directories.titles / f"{self.used_filename}.json"

	@property
	def used_filename(self) -> str:
		"""Используемое имя файла."""

		if self._Parser.settings.common.use_id_as_filename and self.id:
			return str(self.id)

		return self.slug

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТАЙТЛА <<<<< #
	#==========================================================================================#

	@property
	def domain(self) -> str | None:
		"""Домен источника."""

		return self._Data["domain"]

	@property
	def id(self) -> int | None:
		"""Целочисленный уникальный идентификатор тайтла."""

		return self._Data["id"]

	@property
	def slug(self) -> str:
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
	def covers(self) -> tuple[ImageData, ...]:
		"""Последовательность данных обложек."""

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

		return tuple(self._Branches.values())
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def _LoadData(self, identificator: int | str, selector_type: By = By.Slug) -> dict | None:
		"""
		Открывает локальный JSON файл и считывает его данные.

		:param identificator: Идентификатор тайтла: имя файла (без расширения), ID или алиас тайтла.
		:type identificator: int | str
		:param selector_type: Режим поиска файла. По умолчанию `By.Slug` – идентификатор соответствует алиасу тайтла.
		:type selector_type: By
		:return: Словарь данных тайтла или `None` при отсутствии файла.
		:rtype: dict | None
		:raises JSONDecodeError: Ошибка десериализации JSON.
		:raises UnsupportedFormat: Неподдерживаемый формат JSON.
		"""

		DataBuffer: dict = {}
		TitlesDirectory = self._Parser.settings.directories.titles
		Journal = self._Parser.source_operator.shared_data.journal
		FilePath: Path | None = None

		match selector_type:

			case By.Filename:

				if type(identificator) is int:
					raise ValueError("Filename must be str.")
				
				identificator = cast(str, identificator)

				Filename: str = identificator if identificator.endswith(".json") else f"{identificator}.json"
				FilePath = TitlesDirectory / Filename

				if FilePath.exists():
					DataBuffer = ReadJSON(FilePath)

			case By.Slug:
				if self._Parser.settings.common.use_id_as_filename:
					ID = Journal.get_id_by_slug(str(identificator))
					if ID:
						FilePath = TitlesDirectory / f"{ID}.json"
						if FilePath.exists():
							DataBuffer = ReadJSON(FilePath)
				else:
					FilePath = TitlesDirectory / f"{identificator}.json"
					if FilePath.exists():
						DataBuffer = ReadJSON(FilePath)
				
				if not DataBuffer:
					DataBuffer = self._SearchFileInDirectory(TitlesDirectory, str(identificator), By.Slug) or {}

			case By.ID:
				if not self._Parser.settings.common.use_id_as_filename:
					Slug = Journal.get_slug_by_id(int(identificator))
					if Slug:
						FilePath = TitlesDirectory / f"{Slug}.json"
						if FilePath.exists():
							DataBuffer = ReadJSON(FilePath)
				else:
					FilePath = TitlesDirectory / f"{identificator}.json"
					if FilePath.exists():
						DataBuffer = ReadJSON(FilePath)
					
				if not DataBuffer:
					DataBuffer = self._SearchFileInDirectory(TitlesDirectory, str(identificator), By.ID) or {}

		self._IsLocalFileLoaded = bool(DataBuffer)

		return Zerotify(DataBuffer)

	def _MergeBranch(self, branch: BaseBranch) -> int:
		"""
		Выполняет слияние объектов вевтей с одинаковым ID.

		:param branch: Ветвь.
		:type branch: BaseBranch
		:return: Количество добавленных глав.
		:rtype: int
		"""

		CurrentBranch = self._Branches[branch.id]
		AddedCount = 0

		for NewChapter in branch.chapters:
			if not CurrentBranch.has_chapter(NewChapter.id):
				CurrentBranch.add_chapter(NewChapter)
				AddedCount += 1

		return AddedCount

	def _IsLocalFileEqual(self) -> bool:
		"""
		Проверяет, идентичны ли данные тайтла локальным данным.

		:return: Возвращает `True`, если данные идентичны, или `False` в противном случа и при отсутствии локального файла.
		:rtype: bool
		"""

		if not self.path.exists():
			return False

		LocalHasher = hashlib.sha256(orjson.dumps(ReadJSON(self.path)))
		MemoryHasher = hashlib.sha256(orjson.dumps(self._Data))
		
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
				Data = ReadJSON(Element.path)
				if Data.get(type.value) == identificator:
					return Data

			except (json.JSONDecodeError, exceptions.parsers.UnsupportedFormat):
				pass

		return None

	def _TryUpdateJournal(self):
		"""Обновляет кэш пары алиас-ID, если оба валидны."""

		if all((self.id, self.slug)):
			self._Parser.source_operator.shared_data.journal.update(cast(int, self.id), cast(str, self.slug))

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ПРЕОБРАЗОВАНИЯ СЛОВАРНОЙ СТРУКТУРЫ <<<<< #
	#==========================================================================================#

	def _ParseCovers(self):
		"""Парсит обложки в объектные представления."""

		self._Covers.clear()

		for CoverData in self._Data["covers"]:
			CoverData = cast(dict, CoverData)
			Buffer = ImageData(CoverData["link"])
			Buffer.create_resolution(CoverData.get("width"), CoverData.get("height"))
			self._Covers.append(Buffer)

	def _ParsePersons(self):
		"""Парсит персонажей в объектные представления."""

		self._Persons.clear()

		for PersonData in self._Data["persons"]:
			CoverData = cast(dict, PersonData)
			Buffer = Person(CoverData["name"])
			
			AnotherNames = CoverData.get("another_names") or ()
			Images = CoverData.get("images") or ()
			Description = CoverData.get("description")

			for AnotherName in AnotherNames:
				Buffer.add_another_name(AnotherName)

			for CurrentImageData in Images:
				CurrentImageData = cast(dict, CurrentImageData)
				Image = ImageData(CurrentImageData["link"])
				Image.create_resolution(CurrentImageData.get("width"), CurrentImageData.get("height"))
				Buffer.add_image(Image)

			if Description:
				Buffer.set_description(Description)

			self._Persons.append(Buffer)

	def _UpdateBranchesInfo(self):
		"""Обновляет информацию о ветвях во внутреннем словарном хранилище тайтла."""

		Branches = []

		for CurrentBranch in self._Branches.values():
			Branches.append({"id": CurrentBranch.id, "chapters_count": CurrentBranch.chapters_count})

		self._Data["branches"] = sorted(Branches, key = lambda Value: Value["chapters_count"], reverse = True)

	def _UpdateContent(self, brach_id: int | None = None, sorting: bool = True):
		"""
		Обновляет контент во внутреннем словарном хранилище данных тайтла.

		:param brach_id: Если указать ID ветви, будет обновлена только одна ветвь.
		:type brach_id: int | None
		:param sorting: Указывает, нужно ли провести сортировку глав на основе их нумерации.
		:type sorting: bool
		"""

		for CurrentBranch in self._Branches.values():
			if brach_id and brach_id == CurrentBranch.id or not brach_id:
				if sorting: CurrentBranch.sort()
				self._Data["content"][str(CurrentBranch.id)] = CurrentBranch.to_list()
				if brach_id: break

	def _UpdateCovers(self):
		"""Обновляет данные обложек во внутреннем словарном хранилище данных тайтла."""

		self._Data["covers"] = []

		for CurrentCover in self._Covers:
			self._Data["covers"].append(CurrentCover.to_dict())

	def _UpdatePersons(self):
		"""Обновляет данные персонажей во внутреннем словарном хранилище данных тайтла."""

		self._Data["persons"] = []

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
			"format": "melon-" + type(self).__name__.lower(),
			"domain": self._Parser.manifest.domain,
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
	def _Merge(self, chapter: Any, data: dict[str, Any]):
		"""
		Задаёт новое содержимое для главы, используя словарь её данных.

		:param chapter: Глава.
		:type chapter: Any
		:param data: Словарь данных главы.
		:type data: dict[str, Any]
		"""

		pass

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
		
		self._Data: dict[str, Any] = self._GenerateTitleData()
		self._Data["format"] = "melon-" + type(self).__name__.lower()
		self._Data["slug"] = slug

		self._Branches: dict[int, BaseBranch] = {}
		self._Persons: list[Person] = []
		self._Covers: list[ImageData] = []

		self._IsLocalFileLoaded: bool = False

		self._PostInitMethod()

	def __getitem__(self, key: str) -> Any:
		"""
		Возвращает значение из внутреннего словаря тайтла.

		:param key: Ключ значения.
		:type key: str
		:return: Значение.
		:rtype: Any
		:raises KeyError: Ключ не найден.
		"""

		return self._Data[key]

	def __setitem__(self, key: str, value: Any):
		"""
		Задаёт значение во внутренний словарь тайтла.

		:param key: Ключ значения.
		:type key: str
		:param value: Значение.
		:type value: Any
		"""

		self._Data[key] = value

	def load(self, identificator: int | str, selector_type: By = By.Slug) -> bool:
		"""
		Открывает локальный JSON файл и интерпретирует его данные.

		:param identificator: Идентификатор тайтла: имя файла (без расширения), ID или алиас тайтла.
		:type identificator: int | str
		:param selector_type: Режим поиска файла. По умолчанию `By.Slug` – идентификатор соответствует алиасу тайтла.
		:type selector_type: By
		:return: Возвращает `True`, если удалось найти и открыть файл.
		:rtype: bool
		"""

		DataBuffer = self._LoadData(identificator, selector_type)
		
		if DataBuffer:
			self._Data = self._Data | DataBuffer
			self._ParseCovers()
			self._ParsePersons()
			self._ParseBranchesToObjects()

		return bool(DataBuffer)

	def merge(self) -> int:
		"""
		Считывает данные о контенте тайтла.

		:return: Количество глав, для которых считан контент.
		:rtype: int
		"""

		DataBuffer: dict | None = self._LoadData(self.slug)

		if not DataBuffer:
			return 0
		
		#---> Слияние размеров обложек.
		#==========================================================================================#
		CoversData: list[dict] = DataBuffer["covers"]

		for CoverData in CoversData:
			Link = CoverData["link"]
			TargetCover = self.find_cover_by_link(Link)
			if TargetCover:
				TargetCover.create_resolution(CoverData.get("width"), CoverData.get("height"))

		#---> Слияние размеров портретов персонажей.
		#==========================================================================================#
		PersonsData: list[dict] | None = DataBuffer.get("persons")

		if PersonsData:
			for PersonData in PersonsData:
				PersonObject = self.find_person_by_name(PersonData["name"])
				if not PersonObject: continue

				for CurrentImage in cast(list[dict], PersonData["images"]):
					Link = CurrentImage["link"]
					TargetImage = PersonObject.find_image_by_link(Link)
					if TargetImage:
						TargetImage.create_resolution(CurrentImage.get("width"), CurrentImage.get("height"))
			
		#---> Слияние контента глав.
		#==========================================================================================#
		ContentData: dict[str, dict] = DataBuffer["content"]
		MergedChaptersCount: int = 0

		for BranchKey in ContentData.keys():
			for ChapterData in ContentData[BranchKey]:
				ChapterID = int(ChapterData["id"])
				
				SearchResult = self.find_chapter_by_id(ChapterID)

				if SearchResult and SearchResult.chapter.is_empty:
					self._Merge(SearchResult.chapter, ChapterData)
					MergedChaptersCount += 1

		return MergedChaptersCount

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
			WriteJSON(self.path, self._Data)

		return not IsLocalFileEqual

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОИСКА ОБЪЕКТОВ <<<<< #
	#==========================================================================================#

	def find_branch_by_id(self, branch_id: int) -> BaseBranch | None:
		"""
		Ищет ветвь по её ID.

		:param branch_id: ID dtndb.
		:type branch_id: int
		:return: Результат поиска.
		:rtype: BaseBranch | None
		"""

		return self._Branches.get(branch_id)

	def find_cover_by_link(self, link: str) -> ImageData | None:
		"""
		Производит поиск обложки по ссылке.

		:param link: Ссылка на обложку.
		:type link: str
		:return: Обложка или `None` при отсутствии оной.
		:rtype: ImageData | None
		"""

		for CurrentCover in self._Covers:
			if CurrentCover.link == link:
				return CurrentCover
			
		return None

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

		for CurrentBranch in self._Branches.values():
			for CurrentChapter in CurrentBranch.chapters:
				if CurrentChapter.id == chapter_id:
					BranchResult = CurrentBranch
					ChapterResult = CurrentChapter
					break

		if all((BranchResult, ChapterResult)):
			return ChapterSearchResult(cast(BaseBranch, BranchResult), ChapterResult) if ChapterResult else None

		return None

	def find_person_by_name(self, name: str) -> Person | None:
		"""
		Производит поиск персонажа по имени.

		:param name: Имя персонажа.
		:type name: str
		:return: Обложка или `None` при отсутствии оной.
		:rtype: ImageData | None
		"""

		for CurrentPerson in self._Persons:
			if CurrentPerson.name == name:
				return CurrentPerson
			
		return None

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
		if another_name != self._Data["localized_name"] and another_name != self._Data["eng_name"] and another_name and another_name not in self._Data["another_names"]:
			self._Data["another_names"].append(another_name)

	def add_cover(self, cover: ImageData):
		"""
		Добавляет обложку.

		:param cover: Обложка.
		:type cover: ImageData
		:raises ValueError: Отсутствует ссылка на обложку.
		"""

		if not cover.link:
			raise ValueError("Cover must have a link.")
		
		for CurrentCover in self._Covers:
			if CurrentCover.link == cover.link:
				return
		
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

	def add_franchise(self, franchise: str):
		"""
		Добавляет франшизу.

		:param franchise: Франшиза.
		:type franchise: str
		"""

		franchise = franchise.strip()
		if franchise and franchise not in self._Data["franchises"]:
			self._Data["franchises"].append(franchise)

	def add_person(self, person: Person):
		"""
		Добавляет персонажа.

		:param person: Персонаж.
		:type person: Person
		"""
		
		for CurrentPerson in self._Persons:
			if CurrentPerson.name == person.name:
				return
			
		self._Persons.append(person)

	def add_branch(self, branch: BaseBranch) -> int:
		"""
		Добавляет ветвь.

		:param branch: Ветвь контента. Если ветвь с таким ID уже существует, будут добавлены только отсутствующие главы.
		:type branch: BaseBranch
		:return: Количество добавленных глав.
		:rtype: int
		:raises ParsingError: Ветвь не имеет ID или ветвь с таким ID уже добавлена в тайтл.
		"""

		AddedCount = branch.chapters_count

		if not branch.id:
			exceptions.parsers.ParsingError("Branch must have ID.")

		if branch.id in self._Branches.keys():
			AddedCount = self._MergeBranch(branch)
		else:
			self._Branches[branch.id] = branch
			self._Branches = {CurrentBranch.id: CurrentBranch for CurrentBranch in sorted(self._Branches.values(), key = lambda Value: Value.chapters_count, reverse = True)}

		return AddedCount

	def set_domain(self, domain: str | None):
		"""
		Задаёт домен источника.

		:param site: Домен источника.
		:type site: str | None
		:raises ValueError: Некорректный домен.
		"""

		if domain and not Validator_Domain.validate(domain):
			raise ValueError("Incorrect domain.")

		self._Data["domain"] = domain

	def set_id(self, id: int | None):
		"""
		Задаёт ID тайтла.

		:param id: ID тайтла.
		:type id: int | None
		"""

		self._Data["id"] = id
		self._TryUpdateJournal()

	def set_content_language(self, language_code: str | None, load_preset: bool = True):
		"""
		Задаёт язык контента по стандарту ISO 639-3.

		:param original_language: Код языка.
		:type original_language: str | None
		:param load_preset: Указывает, стоит ли попытаться загрузить готовый словарь ключевых локальных определений.
		:type load_preset: bool
		:raise ValueError: Выбрасывается при несоответствии кода языка стандарту.
		"""

		if language_code:
			CheckLanguageCode(language_code)

			if load_preset:
				self._Parser.load_words_dictionary_preset(language_code)

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

	def set_covers(self, covers: Sequence[ImageData]):
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

	def set_publication_year(self, publication_year: int | None):
		"""
		Задаёт год публикации тайтла.

		:param publication_year: Год публикации тайтла.
		:type publication_year: int | None
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
			self.add_franchise(Franchise)

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