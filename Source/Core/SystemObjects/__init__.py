from Source.Core.SystemObjects.Logger import Logger, LoggerRules
from Source.Core.SystemObjects.Manager import Manager
from Source.Core.SystemObjects.Temper import Temper
from Source.CLI import Templates

class SystemObjects:
	"""Коллекция системных объектов."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	FORCE_MODE = False
	LIVE_MODE = False
	SHUTDOWN = False

	EXIT_CODE = 0
	VERSION = "0.1.0-alpha"

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

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

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Manager = Manager(self)
		self.__Logger = Logger(self)
		self.__Temper = Temper()
		self.__ParserName = None

	def select_parser(self, parser_name: str):
		"""Выбирает используемый парсер и настраивает согласно ему системные объекты."""

		self.__ParserName = parser_name
		self.__Logger.select_parser(parser_name)
		self.__Manager.select_parser(parser_name)
		self.__Temper.select_parser(parser_name)