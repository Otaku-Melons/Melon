from Source.Core.Exceptions import GitNotInstalled

from dublib.CLI.TextStyler import Styles, TextStyler
from dublib.Methods.Filesystem import ReadTextFile

import platform
import requests
import shutil
import os
import re

class Installer:
	"""Установщик парсеров."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ CLI <<<<< #
	#==========================================================================================#

	def __StyleParserName(self, parser_name: str) -> str:
		"""
		Возвращает стилизованное название парсера.
			parser_name – значение.
		"""

		return TextStyler(parser_name, decorations = [Styles.Decorations.Bold])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckDirectories(self, parser_name: str):
		"""
		Проверяет наличие каталогов парсера и создаёт их при необходимости.
			parser_name – название парсера.
		"""

		Paths = [
			f"Configs/{parser_name}",
			"Parsers"
		]

		for Path in Paths:
			if not os.path.exists(Path): os.makedirs(Path)

	def __CheckGit(self):
		"""Проверяет наличие Git на устройстве."""

		if os.system(f"git --version {self.__DevNull}") != 0: raise GitNotInstalled()

	def __GetReposLink(self, parser_name: str) -> str:
		"""
		Генерирует ссылку на репозиторий.
			parser_name – название парсера.
		"""

		Link = None
		if self.__SSH: Link = f"git@{self.__Domain}:{self.__Owner}/{parser_name}.git"
		else: Link = f"https://{self.__Domain}/{self.__Owner}/{parser_name}"

		return Link

	def __InstallConfigs(self, parser_name: str):
		"""
		Устанавливает конфигурации парсера.
			parser_name – название парсера.
		"""

		Configs = [
			"logger",
			"settings"
		]

		for Config in Configs:
			TagetPath = f"Configs/{parser_name}/{Config}.json"
			FromPath = f"Parsers/{parser_name}/{Config}.json"

			if not os.path.exists(TagetPath) and os.path.exists(FromPath):
				shutil.copy2(FromPath, TagetPath)
				print(f"Config \"{Config}.json\" installed.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__SSH = False
		self.__Domain = "github.com"
		self.__Owner = "Otaku-Melons"
		self.__DevNull = " >/dev/null 2>&1" if platform.system() == "Linux" else ""

		self.__CheckGit()

	def enable_ssh(self, status: bool):
		"""
		Переключает использование SSH вместо HTTP.
			status – статус.
		"""

		self.__SSH = status

	def get_owner_repositories(self, owner: str | None = None) -> list[str]:
		"""
		Возвращает список репозиториев пользователя или организации.
			owner – пользователь или организация.
		"""

		Repositories = list()
		Owner = owner or self.__Owner
		Response = requests.get(f"https://api.github.com/users/{Owner}")
		if "next" in Response.links: Repositories += self.get_owner_repositories(Response.links["next"]["url"])
		for Repos in Response.json(): Repositories.append(Repos.get("name"))

		return Repositories

	def get_progenitors(self, parser_name: str) -> list[str]:
		"""
		Возвращает список прародителей парсера.
			parser_name – название парсера.
		"""

		Progenitors = list()

		try:
			Path = f"Parsers/{parser_name}/main.py"
			if not os.path.exists(Path): raise FileExistsError(Path)
			Main = ReadTextFile(Path)
			SearchResults = re.findall(r"Parsers\.\w+\.main", Main)
			for String in SearchResults: Progenitors.append(String[8:-5])
			Progenitors = list(set(Progenitors))
		
		except: pass

		return Progenitors

	def install(self, parser_name: str, force: bool = False, is_progenitor: bool = False):
		"""
		Устанавливает парсер.
			parser_name – название парсера;\n
			force – указывает, нужно ли удалить существующие файлы;\n
			is_progenitor – считается ли парсер предком другого парсера.
		"""

		StyledParserName = self.__StyleParserName(parser_name)
		print(f"Installing {StyledParserName}..." if is_progenitor else f"=== Installing {StyledParserName} ===")
		# StyledPrinter("WARNING: Last commit will be installed instead stable version!", text_color = Styles.Colors.Yellow)
		if force: print("Force mode: " + TextStyler("enabled", text_color = Styles.Colors.Red))

		Path = f"Parsers/{parser_name}"
		IsExists = os.path.exists(Path)
		
		if IsExists and force:
			shutil.rmtree(Path)
			print("Existing files deleted.")

		elif IsExists and not force:
			print("Already installed.")

		else:
			self.__CheckDirectories(parser_name)

			if os.system("cd Parsers && git clone " + self.__GetReposLink(parser_name) + self.__DevNull) != 0:
				# StyledPrinter("ERROR!", text_color = Styles.Colors.Red)
				return
			
			else:
				self.__InstallConfigs(parser_name)
				print("Done.")

				Progenitors = self.get_progenitors(parser_name)
				if Progenitors: print("=== Installing progenitors ===")
				for Repos in self.get_progenitors(parser_name): self.install(Repos, is_progenitor = True)

	def set_owner(self, owner: str):
		"""
		Задаёт владельца репозитория для генерации ссылок.
			owner – владелец.
		"""

		self.__Owner = owner

	def uninstall(self, parser_name: str, force: bool = False):
		"""
		Уадялет парсер.
			parser_name – название парсера;\n
			force – указывает, нужно ли удалить существующие файлы.
		"""

		StyledParserName = self.__StyleParserName(parser_name)
		print(f"Uninstalling {StyledParserName}...")
		if force: print("Force mode: " + TextStyler("enabled", text_color = Styles.Colors.Red))

		Path = f"Configs/{parser_name}"

		if force and os.path.exists(Path):
			shutil.rmtree(Path)
			print("Configs removed.")

		if os.path.exists("Configs") and not os.listdir("Configs"): os.rmdir("Configs")

		Path = f"Parsers/{parser_name}"

		if os.path.exists(Path):
			shutil.rmtree(Path)
			print("Done.")

		else: print(f"Parser {StyledParserName} not found.")