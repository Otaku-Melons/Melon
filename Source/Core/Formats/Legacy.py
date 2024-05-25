from dublib.Methods import ReplaceDictionaryKey

class LegacyManga:
	"""Устаревший формат манги."""

	def from_legacy(manga: dict) -> dict:
		"""
		Форматирует мангу из устаревшего формата.
			manga – словарное описание манги.
		"""

		# Переименование ключей.
		manga = ReplaceDictionaryKey(manga, "chapters", "content")

		return manga

	def to_legacy(manga: dict) -> dict:
		"""
		Форматирует мангу в устаревший формат.
			manga – словарное описание манги.
		"""

		# Определения типов и статусов.
		Types = {
			None: "UNKNOWN",
			"manga": "MANGA",
			"manhwa": "MANHWA",
			"manhua": "MANHUA",
			"western_comic": "WESTERN_COMIC",
			"russian_comic": "RUS_COMIC",
			"indonesian_comic": "INDONESIAN_COMIC",
			"manga": "MANGA"
		}
		Statuses = {
			None: "UNKNOWN",
			"announced": "ANNOUNCED",
			"ongoing": "ONGOING",
			"dropped": "ABANDONED",
			"completed": "COMPLETED"
		}
		# Переименование ключей.
		manga = ReplaceDictionaryKey(manga, "ru_name", "ru-name")
		manga = ReplaceDictionaryKey(manga, "en_name", "en-name")
		manga = ReplaceDictionaryKey(manga, "another_names", "another-names")
		manga = ReplaceDictionaryKey(manga, "authors", "author")
		manga = ReplaceDictionaryKey(manga, "publication_year", "publication-year")
		manga = ReplaceDictionaryKey(manga, "age_limit", "age-rating")
		manga = ReplaceDictionaryKey(manga, "is_licensed", "is-licensed")
		manga = ReplaceDictionaryKey(manga, "franchises", "series")
		manga = ReplaceDictionaryKey(manga, "content", "chapters")
		# Преобразование значений.
		manga["format"] = "dmp-v1"
		manga["author"] = ", ".join(manga["author"])
		manga["type"] = Types[manga["type"]]
		manga["status"] = Statuses[manga["status"]]

		# Для каждой ветви.
		for BranchID in manga["chapters"]:

			# Для каждой главы.
			for ChapterIndex in range(len(manga["chapters"][BranchID])):
				# Буфер для внесения изменений.
				Buffer = manga["chapters"][BranchID][ChapterIndex]
				# Переименование ключей.
				Buffer = ReplaceDictionaryKey(Buffer, "is_paid", "is-paid")
				# Преобразование значений.
				Buffer["translators"] = ", ".join(Buffer["translators"])
				# Сохранение изменений.
				manga["chapters"][BranchID][ChapterIndex] = Buffer

		return manga