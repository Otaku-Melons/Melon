from typing import TYPE_CHECKING

from dublib.cli.progress_indicator import ProgressIndicator
from dublib.cli.templates.bus import GenerateMessage, MessagesTypes
from dublib.cli.text_styler import GetStyledTextFromHTML

from .portals import Portals
from .stages import Stages
from .templates import Templates

if TYPE_CHECKING:
	from ....core.system_objects import SystemObjects

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Printer:
	"""Оператор вывода."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def progress_indicator(self) -> ProgressIndicator:
		"""Терминальный индикатор прогресса на основе OSC 9;4."""

		return self.__ProgressIndicator

	@property
	def stages(self) -> Stages:
		"""Сообщения этапов выполнения."""

		return self.__Stages

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self.__SystemObjects

	@property
	def templates(self) -> Templates:
		"""Расширенные шаблоны вывода."""

		return self.__Templates

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Оператор вывода.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""
		
		self.__SystemObjects = system_objects

		self.__ProgressIndicator = ProgressIndicator()
		self.__Stages = Stages(self)
		self.__Templates = Templates(self)

	def emit(self, text: str, message_type: MessagesTypes | None = None, end_line: bool = True, flush: bool = False, parse_html: bool = True):
		"""
		Отправляет сообщение в поток вывода.

		:param text: Текст сообщения.
		:type text: str
		:param message_type: Тип сообщения.
		:type message_type: MessagesTypes | None
		:param end_line: Указывает, нужно ли добавить в конец строки символ новой строки.
		:type end_line: bool
		:param flush: Переключает вывод кэшированных данных.
		:type flush: bool
		:param parse_html: Указывает, парсить HTML теги при помощи функции `GetStyledTextFromHTML()`.
		:type parse_html: bool
		"""

		if parse_html: text = GetStyledTextFromHTML(text)
		MessageText = GenerateMessage(text, message_type)
		print(MessageText, end = "\n" if end_line else "", flush = flush)

	def get_parser_portals(self, parser_name: str) -> Portals:
		"""
		Возвращает порталы вывода парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Порталы вывода парсера.
		:rtype: Portals
		"""

		return Portals(self, parser_name)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ВЫВОДА БАЗОВЫХ ТИПОВ СООБЩЕНИЙ <<<<< #
	#==========================================================================================#

	def critical(self, text: str):
		"""
		Обрабатывает вывод критической ошибки.

		:param text: Текст сообщения.
		:type text: str
		"""

		self.emit(text, MessagesTypes.Critical)

	def error(self, text: str):
		"""
		Обрабатывает вывод ошибки.

		:param text: Текст сообщения.
		:type text: str
		"""

		self.emit(text, MessagesTypes.Error)

	def warning(self, text: str):
		"""
		Обрабатывает вывод предупреждения.

		:param text: Текст сообщения.
		:type text: str
		"""

		self.emit(text, MessagesTypes.Warning)