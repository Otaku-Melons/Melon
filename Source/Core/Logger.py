from dublib.WebRequestor import WebResponse
from datetime import datetime

import logging
import time
import os

class Logger:
	"""Менеджер логов."""

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер логов."""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Путь к файлу лога.
		self.__LogFilename = None

		#---> Настройка логов.
		#==========================================================================================#
		# Если каталог логов не существует, создать его.
		if not os.path.exists("Logs"): os.makedirs("Logs")
		# Получение текущей даты.
		CurrentDate = datetime.now()
		# Время запуска скрипта.
		StartTime = time.time()
		# Формирование пути к файлу лога.
		self.__LogFilename = "Logs/" + str(CurrentDate)[:-7] + ".log"
		self.__LogFilename = self.__LogFilename.replace(":", "-")
		# Установка конфигнурации.
		logging.basicConfig(filename = self.__LogFilename, encoding = "utf-8", level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")		

	#==========================================================================================#
	# >>>>> БАЗОВЫЕ ТИПЫ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def critical(self, text: str):
		"""
		Записывает в лог критическую ошибку.
			text – данные.
		"""

		logging.critical(text)

	def error(self, text: str):
		"""
		Записывает в лог ошибку.
			text – данные.
		"""

		logging.error(text)

	def info(self, text: str):
		"""
		Записывает в лог информацию.
			text – данные.
		"""

		logging.info(text)

	def warning(self, text: str):
		"""
		Записывает в лог предупреждение.
			text – данные.
		"""

		logging.warning(text)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ТИПОВ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def amending_end(self, slug: str, chapters_cont: int):
		"""
		Записывает в лог информацию о количестве дополненных глав.
			slug – алиас;
			chapters_cont – количество дополненных глав.
		"""

		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\". Amended chapters count: {chapters_cont}.")

	def chapter_amended(self, slug: str, chapter_id: int, is_paid: bool):
		"""
		Записывает в лог данные дополненной главы.
			slug – алиас;
			chapter_id – идентификатор главы;
			is_paid – является ли глава платной.
		"""

		# Составление типа главы.
		Chapter = "Paid chapter" if is_paid else "Chapter"
		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\". {Chapter} {chapter_id} amended.")

	def chapter_repaired(self, slug: str, chapter_id: int, is_paid: bool):
		"""
		Записывает в лог данные дополненной главы.
			slug – алиас;
			chapter_id – идентификатор главы;
			is_paid – является ли глава платной.
		"""

		# Составление типа главы.
		Chapter = "Paid chapter" if is_paid else "Chapter"
		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\". {Chapter} {chapter_id} repaired.")

	def parsing_start(self, slug: str):
		"""
		Записывает в лог сообщение об успешном парсинге данных тайтла.
			slug – алиас.
		"""

		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\". Parsing...")

	def request_error(self, response: WebResponse, text: str | None = None):
		"""
		Обрабатывает ошибку сети.
			response – объект WEB-ответа;
			text – описание ошибки.
		"""

		# Если не передано описание, использовать стандартное.
		if not text: text = "Request error."
		# Запись в лог ошибки.
		logging.error(f"{text} Response code: {response.status_code}.")

	#==========================================================================================#
	# >>>>> МЕТОДЫ УПРАВЛЕНИЯ ЛОГАМИ <<<<< #
	#==========================================================================================#

	def remove(self):
		"""Удаляет файл лога."""

		# Если файл существует, удалить его.
		if os.path.exists(self.__LogFilename): os.remove(self.__LogFilename)