import enum

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class By(enum.Enum):
	"""Типы идентификаторов описательных файлов."""
	
	Filename = 0
	Slug = 1
	ID = 2

class Statuses(enum.Enum):
	"""Определения статусов."""

	announced = "announced"
	ongoing = "ongoing"
	completed = "completed"
	dropped = "dropped"

#==========================================================================================#
# >>>>> БАЗОВЫЕ СТРУКТУРЫ ТАЙТЛОВ <<<<< #
#==========================================================================================#

class BaseChapter:
	"""Базовая глава."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def id(self) -> int | None:
		"""Уникальный идентификатор главы."""

		return self._Chapter["id"]
	
	@property
	def volume(self) -> str | None:
		"""Номер тома."""

		return self._Chapter["volume"]
	
	@property
	def number(self) -> str | None:
		"""Номер главы."""

		return self._Chapter["number"]
	
	@property
	def name(self) -> str | None:
		"""Название главы."""

		return self._Chapter["name"]
	
	@property
	def is_paid(self) -> bool | None:
		"""Состояние: платная ли глава."""

		return self._Chapter["is_paid"]
	
	@property
	def translators(self) -> list[str]:
		"""Список ников переводчиков."""

		return self._Chapter["translators"]
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Базовая глава."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._Chapter = {
			"id": None,
			"volume": None,
			"number": None,
			"name": None,
			"is_paid": None,
			"translators": []
		}

	def __getitem__(self, key: str) -> bool | int | list | str | None:
		"""
		Возвращает значение ключа из словаря данных главы. Не рекомендуется к использованию!
			key – ключ данных.
		"""

		return self._Chapter[key]

	def add_extra_data(self, key: str, value: any):
		"""
		Добавляет дополнительные данные о главе.
			key – ключ для доступа;\n
			value – значение.
		"""

		self._Chapter[key] = value

	def add_translator(self, translator: str):
		"""
		Добавляет переводчика.
			translator – ник переводчика.
		"""

		self._Chapter["translator"].append(translator)

	def remove_extra_data(self, key: str):
		"""
		Удаляет дополнительные данные о главе.
			key – ключ для доступа.
		"""

		del self._Chapter[key]

	def set_dict(self, dictionary: dict):
		"""
		Задаёт словарь, используемый в качестве хранилища данных главы.
			dictionary – словарь данных главы.
		"""

		NoneType = type(None)
		ImportantKeys = ["id", "volume", "number", "name", "is_paid", "translators", "slides"]
		ImportantKeysTypes = [
			[int, NoneType],
			[str, NoneType],
			[str, NoneType],
			[str, NoneType],
			[bool, NoneType],
			[list],
			[list]
		]

		for KeyIndex in range(len(ImportantKeys)):
			if ImportantKeys[KeyIndex] not in dictionary.keys(): raise KeyError(ImportantKeys[KeyIndex])
			if type(dictionary[ImportantKeys[KeyIndex]]) not in ImportantKeysTypes[KeyIndex]: raise TypeError(ImportantKeys[KeyIndex])
		
		self._Chapter = dictionary.copy()

	def set_id(self, id: int | None):
		"""
		Задаёт уникальный идентификатор главы.
			ID – идентификатор.
		"""

		self._Chapter["id"] = id

	def set_is_paid(self, is_paid: bool | None):
		"""
		Указывает, является ли глава платной.
			is_paid – состояние: платная ли глава.
		"""

		self._Chapter["is_paid"] = is_paid

	def set_name(self, name: int | None):
		"""
		Задаёт название главы.
			name – название главы.
		"""

		self._Chapter["name"] = name

	def set_number(self, number: str | None):
		"""
		Задаёт номер главы.
			number – номер главы.
		"""

		self._Chapter["number"] = str(number)

	def set_volume(self, volume: str | None):
		"""
		Задаёт номер тома.
			volume – номер тома.
		"""

		self._Chapter["volume"] = str(volume)

	def to_dict(self) -> dict:
		"""Возвращает словарь данных главы."""

		return self._Chapter.copy()
	
class BaseBranch:
	"""Базовая ветвь."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def chapters(self) -> list[BaseChapter]:
		"""Список глав."""

		return self._Chapters

	@property
	def chapters_count(self) -> int:
		"""Количество глав."""

		return len(self._Chapters)

	@property
	def empty_chapters_count(self) -> int:
		"""Количество глав без контента."""

		EmptyChaptersCount = 0

		for CurrentChapter in self._Chapters:
			if not CurrentChapter.slides: EmptyChaptersCount += 1

		return EmptyChaptersCount

	@property
	def id(self) -> int:
		"""Уникальный идентификатор ветви."""

		return self._ID
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, id: int):
		"""
		Базовая ветвь.
			ID – уникальный идентификатор ветви.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._ID = id
		self._Chapters: list[BaseChapter] = list()

	def add_chapter(self, chapter: BaseChapter):
		"""
		Добавляет главу в ветвь.
			chapter – глава.
		"""

		self._Chapters.append(chapter)

	def get_chapter_by_id(self, id: int) -> BaseChapter:
		"""
		Возвращает главу по её уникальному идентификатору.
			id – идентификатор главы.
		"""

		Data = None

		for CurrentChapter in self._Chapters:
			if CurrentChapter.id == id: Data = CurrentChapter

		if not Data: raise KeyError(id)

		return CurrentChapter
	
	def replace_chapter_by_id(self, chapter: BaseChapter, id: int):
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
	
	def to_list(self) -> list[dict]:
		"""Возвращает список словарей данных глав, принадлежащих текущей ветви."""

		BranchList = list()
		for CurrentChapter in self._Chapters: BranchList.append(CurrentChapter.to_dict())

		return BranchList
	
class BaseTitle:
	"""Базовый тайтл."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def format(self) -> str:
		"""Формат структуры данных."""

		return self._Title["format"]

	@property
	def site(self) -> str:
		"""Домен целевого сайта."""

		return self._Title["site"]

	@property
	def id(self) -> int:
		"""Целочисленный уникальный идентификатор тайтла."""

		return self._Title["id"]

	@property
	def slug(self) -> int:
		"""Алиас."""

		return self._Title["slug"]
	
	@property
	def content_language(self) -> str | None:
		"""Код языка контента по стандарту ISO 639-3."""

		return self._Title["content_language"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Базовый тайтл."""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._Title = {
			"format": "melon-manga",
			"site": None,
			"id": None,
			"slug": None,
			"content_language": None
		}