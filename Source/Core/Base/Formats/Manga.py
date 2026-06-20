from Source.Core.Base.Formats.BaseFormat import BaseChapter, BaseBranch, BaseTitle
from Source.Core.Base.Parsers.Components.ImagesDownloader import ImageResolution

from typing import Any, cast

from enum import Enum

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ <<<<< #
#==========================================================================================#

class Types(Enum):
	"""Определения типов манги."""

	manga = "manga"
	manhwa = "manhwa"
	manhua = "manhua"
	oel = "oel"
	western_comic = "western_comic"
	russian_comic = "russian_comic"
	indonesian_comic = "indonesian_comic"

#==========================================================================================#
# >>>>> ВНУТРЕННИЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Slide:
	"""Слайд."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def link(self) -> str:
		"""Ссылка на изображение."""

		return self.__Link
	
	@property
	def index(self) -> int:
		"""Индекс изображения."""

		return self.__Index

	@property
	def resolution(self) -> "ImageResolution | None":
		"""Разрешение изображения."""

		return self.__Resolution

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, link: str, index: int):
		"""
		Слайд.

		:param link: Ссылка на изображение.
		:type link: str
		:param index: Индекс слайда.
		:type index: int
		"""

		self.__Link: str = link
		self.__Index: int = index

		self.__Resolution: "ImageResolution | None" = None

	def set_resolution(self, width: int, height: int):
		"""
		Указывает разрешение изображения.

		:param width: Ширина изображения.
		:type width: int
		:param height: Высота изображения.
		:type height: int
		"""

		self.__Resolution = ImageResolution(width, height)

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		Buffer = {
			"index": self.__Index,
			"link": self.__Link,
			"width": self.__Resolution.width if self.__Resolution else None,
			"height": self.__Resolution.height if self.__Resolution else None
		}

		return Buffer

class Chapter(BaseChapter):
	"""Глава манги."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def slides(self) -> tuple[Slide, ...]:
		"""Последовательность слайдов."""

		return tuple(self.__Slides)
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _Clear(self):
		"""Очищает контент главы."""

		self.__Slides.clear()

	def _IsEmpty(self) -> bool:
		"""
		Проверяет, пустая ли глава.

		:return: Состояние: пуста ли глава.
		:rtype: bool
		"""

		return not bool(self.slides)

	def _FromDict(self, data: dict):
		"""
		Заполняет данные главы из словаря.

		:param data: Словарь данных главы.
		:type data: dict
		"""

		self._Data = self._Data | data
		self.__Slides.clear()
		
		for SlideData in self._Data["slides"]:
			SlideData = cast(dict, SlideData)

			SlideBuffer = Slide(SlideData["link"], SlideData["index"])
			Width, Height = SlideData.get("width"), SlideData.get("height")

			if all((Width, Height)):
				SlideBuffer.set_resolution(cast(int, Width), cast(int, Height))

			self.__Slides.append(SlideBuffer)

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Data["slides"] = list()
		self.__Slides: list[Slide] = list()

	def _PreFormatter(self):
		"""Метод, запускающийся перед генерацией словарного представления объекта."""

		self._Data["slides"] = [CurrentSlide.to_dict() for CurrentSlide in self.__Slides]

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_slide(self, link: str, width: int | None = None, height: int | None = None):
		"""
		Создаёт и добавляет слайд.

		:param link: Ссылка на изображение.
		:type link: str
		:param width: Ширина изображения.
		:type width: int
		:param height: Высота изображения.
		:type height: int
		"""

		CurrentSlide = Slide(link, len(self.__Slides) + 1)

		if all((width, height)):
			CurrentSlide.set_resolution(cast(int, width), cast(int, width))

		self.__Slides.append(CurrentSlide)
		
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

		TypeValue = self._Data.get("type")
		if TypeValue:
			return Types(TypeValue)
		
		return None

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
			"type": None
		} | TitleData

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
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УСТАНОВКИ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_type(self, type: Types | None):
		"""
		Задаёт тип манги.

		:param type: Тип манги.
		:type type: Types | None
		"""

		self._Data["type"] = type.value if type else None