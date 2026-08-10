from dulwich import porcelain

from ...core.system_objects.driver import Driver
from ...core.system_objects.options import Options
from ...core.system_objects.printer import Printer
from ...core.system_objects.temper import Temper

class SystemObjects:
	"""Коллекция системных объектов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def MELON_VERSION(self) -> str:
		"""Используемая версия Melon."""

		return porcelain.tag_list(".")[-1].decode().lstrip("v")

	#==========================================================================================#
	# >>>>> СИСТЕМНЫЕ ОБЪЕКТЫ <<<<< #
	#==========================================================================================#

	@property
	def driver(self) -> Driver:
		"""Менеджер парсеров."""

		return self.__Driver

	@property
	def options(self) -> Options:
		"""Менеджер переменных среды парсера."""

		return self.__Options

	@property
	def printer(self) -> Printer:
		"""Оператор вывода."""

		return self.__Printer
	
	@property
	def temper(self) -> Temper:
		"""Дескриптор каталога временных файлов."""

		return self.__Temper

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Коллекция системных объектов."""

		self.__Driver = Driver(self)
		self.__Options = Options()
		self.__Printer = Printer(self)
		self.__Temper = Temper(self)