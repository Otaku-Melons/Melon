from Source.Core.Objects import Objects

from dublib.Engine.Bus import ExecutionError, ExecutionStatus
from dublib.Methods.Filesystem import NormalizePath
from dublib.WebRequestor import WebRequestor

import os

class Downloader:
	"""Загрузчик изображений."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetFilename(self, url: str) -> str:
		"""
		Определяет имя файла.
			url – ссылка на изображение.
		"""

		# Имя файла. 
		Filename = url.split("/")[-1]
		# Расширение фала.
		Filetype = self.__GetFiletype(url)
		# Удаление расширения.
		Filename = Filename[:len(Filetype) * -1]

		return Filename

	def __GetFiletype(self, url: str) -> str:
		"""
		Определяет расширение файла.
			url – ссылка на изображение.
		"""

		# Расширение файла. 
		Filetype = ""
		# Имя файла на сервере.
		ServerFilename = url.split("/")[-1]
		# Если в названии файла есть точка, определить расширение.
		if "." in ServerFilename: Filetype = "." + ServerFilename.split(".")[-1]

		return Filetype

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, system_objects: Objects, requestor: WebRequestor, exception: bool = False, logging: bool = True):
		"""
		Загрузчик изображений.
			system_objects – коллекция системных объектов;\n
			requestor – менеджер запросов;\n
			exception – указывает, следует ли выбрасывать исключение;\n
			logging – указывает, нужно ли обрабатывать ошибку через системный объект логгирования.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects
		# Состояние: следует ли выбрасывать исключения.
		self.__RaiseExceptions = exception
		# Менеджер запросов.
		self.__Requestor = requestor
		# Состояние: нужно ли обрабатывать ошибку через системный объект логгирования.
		self.__Logging = logging

	def image(
			self,
		   	url: str,
			directory: str = "Temp",
			filename: str | None = None,
			is_full_filename: bool = False,
			referer: str | None = None
		) -> ExecutionStatus:
		"""
		Скачивает изображение.
			url – ссылка на изображение;\n
			directory – путь к каталогу загрузки;\n
			filename – имя файла;\n
			is_full_filename – указывает, является ли имя файла полным;\n
			referer – домен сайта для установка заголовка запроса Referer.
		"""

		# Состояние загрузки.
		Status = ExecutionStatus(0)
		# Нормализация пути.
		directory = NormalizePath(directory)

		#---> Определение параметров файла.
		#==========================================================================================#
		# Расширение файла.
		Filetype = ""
		# Если имя файла указано и не помечено как полное, получить расширение файла (с точкой).
		if filename and not is_full_filename: Filetype = self.__GetFiletype(url)
		# Если имя файла не указано, получить полное имя файла из URL.
		elif not filename: filename = self.__GetFilename(url)

		#---> Выполнение загрузки.
		#==========================================================================================#
		# Состояние: существует ли файл.
		IsFileExists = os.path.exists(f"{directory}{filename}{Filetype}")

		# Если файл не существует или включён режим перезаписи.
		if not IsFileExists or self.__SystemObjects.FORCE_MODE:
			# Заголовки запроса.
			Headers = None

			# Если указан домен сайта, добавить его в заголовок.
			if referer: Headers = {
				"Referer": f"https://{referer}/"
			}
				
			# Выполнение запроса.
			Response = self.__Requestor.get(url, headers = Headers)

			# Если запрос успешен
			if Response.status_code == 200:
				
				# Открытие потока записи.
				with open(f"{directory}{filename}{Filetype}", "wb") as FileWriter:
					# Запись изображения.
					FileWriter.write(Response.content)
					# Изменение статуса.
					Status = ExecutionStatus(200)
					Status.message = "Done."

			else:
				# Запись в лог ошибки запроса.
				if self.__Logging: self.__SystemObjects.logger.request_error(Response, f"Unable to download image: \"{url}\".")
				# Изменение статуса.
				Status = ExecutionError(Response.status_code)
				Status.message = f"Error! Response code: {Response.status_code}."
				# Выброс исключения.
				if self.__RaiseExceptions: raise Exception(f"Unable to download image: \"{url}\". Response code: {Response.status_code}.")

		# Если файл уже существует.
		elif IsFileExists:
			# Изменение статуса.
			Status.message = "Already exists."

		return Status