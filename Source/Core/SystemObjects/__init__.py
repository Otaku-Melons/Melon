from Source.Core.SystemObjects.Logger import Logger, LoggerRules
from Source.Core.SystemObjects.Manager import Manager
from Source.Core.SystemObjects.Temper import Temper
from Source.CLI import Templates

class SystemObjects:
	"""Коллекция системных объектов."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	FORCE_MODE = False
	LIVE_MODE = False

	EXIT_CODE = 0
	VERSION = "0.3.0-alpha"

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def extension_name(self) -> str | None:
		"""Название используемого расширения."""

		return self.__ExtensionName

	@property
	def logger(self) -> Logger:
		"""Менеджер портов CLI и логов."""

		return self.__Logger

	@property
	def manager(self) -> Manager:
		"""Менеджер парсеров"""

		return self.__Manager
	
	@property
	def parser_name(self) -> str | None:
		"""Название используемого парсера."""

		return self.__ParserName

	@property
	def temper(self) -> Temper:
		"""Дескриптор каталога временных файлов."""

		return self.__Temper

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Коллекция системных объектов."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Manager = Manager(self)
		self.__Logger = Logger(self)
		self.__Temper = Temper()

		self.__ExtensionName = None
		self.__ParserName = None

	def select_extension(self, extension_name: str):
		"""
		Задаёт используемое расширение и настраивает согласно ему системные объекты.
			extension_name – имя расширения.
		"""

		self.__ExtensionName = extension_name
		self.__Manager.select_extension(extension_name)
		self.__Temper.select_extension(extension_name)

	def select_parser(self, parser_name: str):
		"""
		Задаёт используемое расширение и настраивает согласно ему системные объекты.
			parser_name – имя парсера.
		"""

		self.__ParserName = parser_name
		self.__Logger.select_parser(parser_name)
		self.__Manager.select_parser(parser_name)
		self.__Temper.select_parser(parser_name)