from dublib.functions.data import zerotify

from ...structs.image import ImageData

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

		self.__Data["description"] = zerotify(description)

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