from dublib.Methods.Filesystem import MakeRootDirectories, RemoveDirectoryContent
from dublib.WebRequestor import WebConfig, WebLibs, WebRequestor
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import Clear
from time import sleep

import logging
import shutil
import os

# from Source.Core.Builder import Builder
# b = Builder({}, "70104")
# b.build_branch()
# exit(0)

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ <<<<< #
#==========================================================================================#

class BuildTargetNotFound(Exception):
	"""Исключение: не найдена цель для сборки."""

	def __init__(self, type: str, value: str):
		"""
		Исключение: не найдена цель для сборки.
			type – тип цели для сборки;\n
			value – идентификатор цели для сборки.
		"""

		# Добавление данных в сообщение об ошибке.
		self.__Message = f"Target \"{type}\" with value \"{value}\" not found."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message) 
			
	def __str__(self):
		return self.__Message

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Builder:
	"""Загрузчик контента."""
	
	def __DownloadSlide(self, url: str, directory: str = "Temp/Slides", filename: str | None = None) -> bool:
		"""
		Скачивает слайд.
			url – URL слайда;\n
			directory – директория для загрузки;\n
			filename – имя файла.
		"""

		# Очистка краевой черты.
		directory = directory.rstrip("/")
		# Заголовки запроса.
		Headers = {
			"Referer": "https://remanga.org/"	
		}
		# Запрос слайда.
		Response = self.__Requestor.get(url, headers = Headers)
		# Состояние: успешна ли загрузка.
		IsSuccess = False
		# Если не указано имя файла, взять из URL.
		if filename == None: filename = url.split("/")[-1].split(".")[0]
		# Расширение файла.
		Type = url.split(".")[-1]
		
		# Если запрос успешен.
		if Response.status_code == 200:
			# Переключение статуса.
			IsSuccess = True

			# Если включена фильтрация маленьких слайдов и слайд более 5 KB или фильтрация отключена.
			if self.__EnableFilter == True and len(Response.content) / 1024 > 5 or self.__EnableFilter == False:
					
				# Открытие потока записи.
				with open(f"{directory}/{filename}.{Type}", "wb") as FileWriter:
					# Запись файла изображения.
					FileWriter.write(Response.content)
					
			else:
				# Запись в лог: слайд отфильтрован по размеру.
				logging.info("Slide: \"" + url + "\". Less than 5 KB. Skipped.")
			
			# Запись в лог: слайд загружен.
			logging.info("Slide: \"" + url + "\". Downloaded.")
		
		else:
			# Запись в лог ошибки: не удалось загрузить слайд.
			logging.error("Unable to download slide: \"" + url + "\". Response code: " + str(Response.status_code) + ".")
	
		return IsSuccess

	def __GetChapterByID(self, chapter_id: int) -> dict:
		"""
		Возвращает структуру главы с переданным идентификатором.
			chapter_id – ID главы.
		"""

		# Для каждой ветви.
		for BranchID in self.__Title["chapters"].keys():
			
			# Для каждой главы.
			for Chapter in self.__Title["chapters"][BranchID]:
				
				# Если глава найдена, вернуть главу.
				if Chapter["id"] == chapter_id: return Chapter
				
		# Если глава не найдена, выбросить исключение.
		raise BuildTargetNotFound("chapter", chapter_id)
	
	def __GetVolumeChapters(self, branch_id: str, volume: str) -> list[dict]:
		"""
		Возвращает список глав, находящихся в томе.
			branch_id – ID ветви перевода;\n
			volume – номер тома.
		"""

		# Список глав.
		Chapters = list()
		
		# Для каждой главы в ветви.
		for Chapter in self.__Title["chapters"][branch_id]:
			
			# Если глава принадлежит указанному тому.
			if str(Chapter["volume"]) == str(volume): Chapters.append(Chapter)
			
		# Если том не найден, выбросить исключение.
		if len(Chapters) == 0: raise BuildTargetNotFound("volume", volume)
			
		return Chapters
	
	def __GetVolumesList(self, branch_id: str) -> list[int, float]:
		"""
		Возвращает список томов.
			branch_id – ID ветви перевода.
		"""
		# Список томов.
		Volumes = list()
		
		# Для каждой главы.
		for Chapter in self.__Title["chapters"][branch_id]:
			
			# Если том не записан, записать.
			if Chapter["volume"] not in Volumes: Volumes.append(Chapter["volume"])
			
		return Volumes

	def __init__(self, settings: dict, title: str, message: str = ""):
		"""
		Загрузчик контента.
			settings – глобальные настройки;\n
			title – название локального файла с описанием тайтла;\n
			message – сообщение из внешнего обработчика.
		"""

		# Если файл указан без расширения, добавить расширение.
		if title.endswith(".json") == False: title = title + ".json"
		# Инициализация загрузчика.
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.requests.enable_proxy_protocol_switching(True)

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Глобальные настройки.
		self.__Settings = settings.copy()
		# Запросчик.
		self.__Requestor = WebRequestor(Config)
		# Данные тайтла.
		self.__Title = ReadJSON(f"Output/remanga/titles/{title}")
		# Заголовок.
		self.__Header = message + "Title: " + self.__Title["slug"] + "\n"
		# Алиас тайтла.
		self.__Slug = self.__Title["slug"]
		# Выходной формат.
		self.__Format = "zip"
		# Состояние: фильтровать ли маленькие слайды.
		self.__EnableFilter = True
		# Состояние: использовать ли интервал.
		self.__UseDelay = True
	
		# Создание папок в корневой директории.
		MakeRootDirectories(["Output", "Temp"])
		# Если формат не поддерживается, выбросить исключение.
		if "format" not in self.__Title.keys() or self.__Title["format"].lower() not in ["dmp-v1", "rn-v2"]: raise Exception("бедаааа")
		
	def build_chapter(self, chapter_id: int, output: str | None = None, message: str = "") -> bool:
		"""
		Скачивает и строит главу.
			chapter_id – ID главы;\n
			output – выходной каталог;\n
			message – сообщение из внешнего обработчика.
		"""

		# Состояние: успешна ли загрузка.
		IsSuccess = True
		# Получение данных главы.
		Chapter = self.__GetChapterByID(chapter_id)
		# Очистка папки временных файлов.
		RemoveDirectoryContent("Temp")
		# Создание папок в корневой директории.
		MakeRootDirectories(["Temp/Slides"])
		# Название главы.
		ChapterName = str(Chapter["number"])
		# Если у главы есть название, добавить его.
		if Chapter["name"] != None: ChapterName += ". " + Chapter["name"].rstrip(".?")
		
		# Если не указан выходной каталог.
		if output == None:
			# Использовать в качестве каталога алиас.
			output = f"Output/{self.__Slug}"	
			# Если не создана, создать выходную директорию.
			if os.path.exists(f"Output/{self.__Slug}") == False: os.makedirs(f"Output/{self.__Slug}")

		else:
			# Удаление конечной косой черты.
			output = output.rstrip("/")
		
		# Для каждого слайда.
		for SlideIndex in range(0, len(Chapter["slides"])):
			# Очистка консоли.
			Clear()
			# Вывод в консоль: прогресс загрузки слайдов.
			print(self.__Header + message + "Slide: " + str(SlideIndex + 1) + " / " + str(len(Chapter["slides"])))
			# Загрузка слайда.
			Result = self.__DownloadSlide(Chapter["slides"][SlideIndex]["link"], filename = str(SlideIndex + 1))
			
			# Если не удалось загрузить слайд.
			if Result == False: 
				# Переключение статуса.
				IsSuccess = False
				# Запись в лог ошибки: не удалось загрузить главу.
				logging.error(f"Unable to create chapter {chapter_id}.")
				# Остановка цикла.
				break
			
			# Если используется интервал и слайд не последний, выждать интервал.
			if self.__UseDelay == True and SlideIndex + 1 != len(Chapter["slides"]): sleep(0.1)
			
		# Если загрузка успешна.
		if IsSuccess == True:
			# Создание архива.
			shutil.make_archive(f"Temp/{ChapterName}", "zip", "Temp/Slides")
			# Если указан нестандартный формат, переименоватьт архив.
			if self.__Format != "zip": os.rename(f"Temp/{ChapterName}.zip", f"Temp/{ChapterName}.{self.__Format}")
			# Если указан выходной каталог, переместить файл.
			if output != None: os.replace(f"Temp/{ChapterName}.{self.__Format}", f"{output}/{ChapterName}.{self.__Format}")
			# Запись в лог сообщения: глава загружена.
			logging.info(f"Chapter {chapter_id}. Build complete.")
		
		return IsSuccess
	
	def build_volume(self, branch_id: str | None, volume: str, message: str = "") -> int:
		"""
		Скачивает и строит том.
			branch_id – ID ветви перевода;\n
			volume – номер тома;\n
			message – сообщение из внешнего обработчика.
		"""

		# Если не указан ID ветви, использовать ветвь с наибольшим количеством глав.
		if branch_id == None: branch_id = str(max(self.__Title["branches"], key = lambda Branch: Branch["chapters_count"])["id"])
		# Количество ошибок.
		ErrorsCount = 0
		# Получение списка глав.
		Chapters = self.__GetVolumeChapters(branch_id, volume)
		
		# Для каждой главы.
		for ChapterIndex in range(0, len(Chapters)):
			# Обновление сообщения.
			MessageText = message + "Chapter: " + str(ChapterIndex + 1) + " / " + str(len(Chapters)) + "\n"
			# Если не создана, создать выходную директорию.
			if os.path.exists(f"Output/{self.__Slug}/Том " + volume) == False: os.makedirs(f"Output/{self.__Slug}/Том " + volume)
			# Загрузка главы.
			Result = self.build_chapter(Chapters[ChapterIndex]["id"], output = f"Output/{self.__Slug}/Том " + volume, message = MessageText)
			# Если не удалось загрузить главу, выполнить инкремент ошибок.
			if Result == False: ErrorsCount += 1
			
		# Сообщение об ошибках.
		ErrorsMessage = "" if ErrorsCount == 0 else f" Errors: {ErrorsCount}."
		# Запись в лог сообщения: том построен.
		logging.info(f"Volume {volume}. Build complete.{ErrorsMessage}")

		return ErrorsCount
	
	def build_branch(self, branch_id: str | None = None) -> int:
		"""
		Скачивает и строит ветвь перевода.
			branch_id – ID ветви перевода.
		"""

		# Если не указан ID ветви, использовать ветвь с наибольшим количеством глав.
		if branch_id == None: branch_id = str(max(self.__Title["branches"], key = lambda Branch: Branch["chapters_count"])["id"])
		# Количество ошибок.
		ErrorsCount = 0
		# Если ветвь не найдена, выбросить исключение.
		if branch_id not in self.__Title["chapters"].keys(): raise BuildTargetNotFound("branch", branch_id)
		
		# Для каждого тома.
		for Volume in self.__GetVolumesList(branch_id):
			# Обновление сообщения.
			MessageText = "Volume: " + str(Volume) + "\n"
			# Загрузка тома.
			Result = self.build_volume(branch_id, str(Volume), MessageText)
			# Инкремент количества ошибок.
			ErrorsCount += Result
			
		# Сообщение об ошибках.
		ErrorsMessage = "" if ErrorsCount == 0 else f" Errors: {ErrorsCount}."
		# Запись в лог сообщения: том построен.
		logging.info(f"Branch {branch_id}. Build complete.{ErrorsMessage}")

		return ErrorsCount
	
	def set_delay_status(self, status: bool):
		"""
		Задаёт статус использования интервала.
			status – статус.
		"""

		self.__UseDelay = status