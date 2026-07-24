from enum import Enum
from typing import Any, Sequence, cast

from Source.Core.Base.Formats.BaseFormat import BaseBranch, BaseChapter, BaseTitle
from Source.Core.Base.Parsers.Components.ImagesDownloader import ImageData

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

class Chapter(BaseChapter):
	"""Глава манги."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def slides(self) -> "tuple[ImageData, ...]":
		"""Последовательность изображений."""

		return tuple(self.__Slides.values())
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetNewSlideIndex(self, start_index: int = 1) -> int:
		"""
		Генерирует индекс нового слайда.

		:param start_index: Индекс, с которого начинается нумерация слайдов.
		:type start_index: int
		:return: Индекс слайда.
		:rtype: int
		"""

		Indexes: tuple[int, ...] = tuple(self.__Slides.keys())

		if not Indexes:
			return 1
		else:
			return max(Indexes) + 1

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
			SlideIndex: int = SlideData["index"]
			SlideImage = ImageData(SlideData["link"])

			Width, Height = SlideData.get("width"), SlideData.get("height")

			if all((Width, Height)):
				SlideImage.create_resolution(Width, Height)

			self.__Slides[SlideIndex] = SlideImage

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Data["slides"] = list()
		self.__Slides: "dict[int, ImageData]" = dict()

	def _PreFormatter(self):
		"""Метод, запускающийся перед генерацией словарного представления объекта."""

		SlidesData: list[dict] = list()
		
		for Index, Image in self.__Slides.items():
			Buffer: dict = {"index": Index} | Image.to_dict(sizing = self._Parser.settings.common.sizing_images)
			SlidesData.append(Buffer)

		self._Data["slides"] = tuple(SlidesData)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_slide(self, image: "ImageData"):
		"""
		Добавляет слайд.

		:param image: Данные изображения.
		:type image: ImageData
		"""

		Index = self.__GetNewSlideIndex()
		self.__Slides[Index] = image
		
	def set_slides(self, images: "Sequence[ImageData]"):
		"""
		Задаёт слайды.

		:param images: Данные изображений.
		:type images: Sequence[ImageData]
		"""

		self.__Slides.clear()
		
		for CurrentImage in images:
			self.add_slide(CurrentImage)

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

	def _Merge(self, chapter: Chapter, data: dict[str, Any]):
		"""
		Задаёт новое содержимое для главы, используя словарь её данных.

		:param chapter: Глава.
		:type chapter: Chapter
		:param data: Словарь данных главы.
		:type data: dict[str, Any]
		"""

		SlidesData: list[dict] = data["slides"]
		
		for SlideData in SlidesData:
			Slide = ImageData(SlideData["link"])
			Width, Height = SlideData.get("width"), SlideData.get("height")

			if all((Width, Height)):
				Slide.create_resolution(Width, Height)

			chapter.add_slide(Slide)
			
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