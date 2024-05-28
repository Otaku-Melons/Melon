from Source.Core.Objects import Objects

from dublib.WebRequestor import WebConfig, WebLibs, WebRequestor

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
	
	def __init__(self, system_objects: Objects, requestor: WebRequestor, exception: bool = False):
		"""
		Загрузчик изображений.
			system_objects – коллекция системных объектов;
			requestor – менеджер запросов;
			exception – указывает, следует ли выбрасывать исключение.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects
		# Состояние: следует ли выбрасывать исключения.
		self.__RaiseExceptions = exception
		# Менеджер запросов.
		self.__Requestor = requestor

	def cover(self, url: str, site: str, directory: str, slug: str, title_id: int) -> str:
		"""
		Скачивает обложку.
			url – ссылка на изображение;
			site – домен сайта для установка заголовка запроса Referer;
			directory – путь к каталогу загрузки;
			slug – алиас тайтла;
			title_id – целочисленный идентификатор тайтла.
		"""

		# Описание загрузки.
		Status = None

		#---> Определение параметров файла.
		#==========================================================================================#
		Filetype = self.__GetFiletype(url)
		Filename = self.__GetFilename(url)
		IsCoverExists = os.path.exists(f"{directory}/{Filename}{Filetype}")

		# Если файл не существует или включён режим перезаписи.
		if not IsCoverExists or self.__SystemObjects.FORCE_MODE:

			#---> Запрос данных.
			#==========================================================================================#
			# Выполнение запроса.
			Response = self.__Requestor.get(url)

			# Если запрос успешен
			if Response.status_code == 200:
				
				# Открытие потока записи.
				with open(f"{directory}/{Filename}{Filetype}", "wb") as FileWriter:
					# Запись изображения.
					FileWriter.write(Response.content)

					# Если обложка существовала и был включён режим перезаписи.
					if IsCoverExists and self.__SystemObjects.FORCE_MODE:
						# Запись в лог информации: обложка перезаписана.
						self.__SystemObjects.logger.info(f"Title: \"{slug}\" (ID: {title_id}). Cover overwritten: \"{Filename}{Filetype}\".")

					else:
						# Запись в лог информации: обложка скачана.
						self.__SystemObjects.logger.info(f"Title: \"{slug}\" (ID: {title_id}). Cover downloaded: \"{Filename}{Filetype}\".")
						
					# Изменение сообщения.
					Status = "Done."

			else:
				# Запись в лог ошибки запроса.
				self.__SystemObjects.logger.request_error(Response, f"Unable to download cover: \"{Filename}{Filetype}\".")
				# Выброс исключения.
				if self.__RaiseExceptions: raise Exception(f"Unable to download cover: \"{Filename}{Filetype}\". Response code: {Response.status_code}.")
				# Изменение сообщения.
				Status = "Failure!"

		else:
			# Запись в лог информации: обложка уже существует.
			self.__SystemObjects.logger.info(f"Title: \"{slug}\" (ID: {title_id}). Cover already exists: \"{Filename}{Filetype}\".")
			# Изменение сообщения.
			Status = "Skipped."

		return Status

	def image(self, url: str, site: str, directory: str | None = None, filename: str | None = None, full_filename: bool = False):
		"""
		Скачивает изображение.
			url – ссылка на изображение;
			site – домен сайта для установка заголовка запроса Referer;
			directory – путь к каталогу загрузки;
			filename – имя файла без расширения;
			full_filename – указывает, является ли имя файла полным.
		"""

		#---> Определение параметров файла.
		#==========================================================================================#
		Filetype = self.__GetFiletype(url)
		directory = "" if directory == None else directory + "/"
		if filename and full_filename: Filetype = ""
		elif filename == None: filename = self.__GetFilename(url)

		# Если файл не существует или включён режим перезаписи.
		#if not os.path.exists(f"{directory}{filename}{Filetype}") or self.__SystemObjects.FORCE_MODE:
		#---> Запрос данных.
		#==========================================================================================#
		# Выполнение запроса.
		Response = self.__Requestor.get(url)

		# Если запрос успешен
		if Response.status_code == 200:
			
			# Открытие потока записи.
			with open(f"{directory}{filename}{Filetype}", "wb") as FileWriter:
				# Запись изображения.
				FileWriter.write(Response.content)
				# Переключение состояния.
				IsSuccess = True

		else:
			# Запись в лог ошибки запроса.
			self.__SystemObjects.logger.request_error(Response, f"Unable to download image: \"{url}\".")
			# Выброс исключения.
			if self.__RaiseExceptions: raise Exception(f"Unable to download image: \"{url}\". Response code: {Response.status_code}.")