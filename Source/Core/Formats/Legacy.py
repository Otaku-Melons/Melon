from dublib.Methods import ReplaceDictionaryKey, Zerotify

class LegacyManga:
	"""Устаревший формат манги."""

	def from_legacy(manga: dict) -> dict:
		"""
		Форматирует мангу из устаревшего формата.
			manga – словарное описание манги.
		"""

		# Определения типов и статусов.
		Types = {
			"UNKNOWN": None,
			"MANGA": "manga",
			"MANHWA": "manhwa",
			"MANHUA": "manhua",
			"WESTERN_COMIC": "western_comic",
			"RUS_COMIC": "russian_comic",
			"INDONESIAN_COMIC": "indonesian_comic",
			"MANGA": "manga",
			"OEL": "oel"
		}
		Statuses = {
			"UNKNOWN": None,
			"ANNOUNCED": "announced",
			"ONGOING": "ongoing",
			"ABANDONED": "dropped",
			"COMPLETED": "completed"
		}
		# Переименование ключей.
		manga = ReplaceDictionaryKey(manga, "ru-name", "ru_name")
		manga = ReplaceDictionaryKey(manga, "en-name", "en_name")
		manga = ReplaceDictionaryKey(manga, "another-names", "another_names")
		manga = ReplaceDictionaryKey(manga, "author", "authors")
		manga = ReplaceDictionaryKey(manga, "publication-year", "publication_year")
		manga = ReplaceDictionaryKey(manga, "age-rating", "age_limit")
		manga = ReplaceDictionaryKey(manga, "is-licensed", "is_licensed")
		manga = ReplaceDictionaryKey(manga, "series", "franchises")
		manga = ReplaceDictionaryKey(manga, "chapters", "content")
		# Преобразование значений.
		manga["format"] = "melon-manga"
		manga["authors"] = manga["authors"].split(", ") if manga["authors"] else list()
		manga["type"] = Types[manga["type"]]
		manga["status"] = Statuses[manga["status"]]

		# Для каждой ветви.
		for BranchID in manga["content"]:

			# Для каждой главы.
			for ChapterIndex in range(len(manga["content"][BranchID])):
				# Буфер для внесения изменений.
				Buffer = manga["content"][BranchID][ChapterIndex]
				# Переименование ключей.
				Buffer = ReplaceDictionaryKey(Buffer, "is-paid", "is_paid")
				Buffer = ReplaceDictionaryKey(Buffer, "translator", "translators")
				# Преобразование значений.
				Buffer["translators"] = Buffer["translators"].split(", ") if Buffer["translators"] else list()
				# Сохранение изменений.
				manga["content"][BranchID][ChapterIndex] = Buffer

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
			"oel": "OEL"
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
		manga["author"] = Zerotify(", ".join(manga["author"]))
		manga["type"] = Types[manga["type"]]
		manga["status"] = Statuses[manga["status"]]

		# Приведение жанров и тегов в нижний регистр.
		for Index in range(len(manga["genres"])): manga["genres"][Index] = manga["genres"][Index].lower()
		for Index in range(len(manga["tags"])): manga["tags"][Index] = manga["tags"][Index].lower()

		# Для каждой ветви.
		for BranchID in manga["chapters"]:

			# Для каждой главы.
			for ChapterIndex in range(len(manga["chapters"][BranchID])):
				# Буфер для внесения изменений.
				Buffer = manga["chapters"][BranchID][ChapterIndex]
				# Переименование ключей.
				Buffer = ReplaceDictionaryKey(Buffer, "is_paid", "is-paid")
				Buffer = ReplaceDictionaryKey(Buffer, "translators", "translator")
				# Преобразование значений.
				Buffer["translator"] = ", ".join(Buffer["translator"]) if Buffer["translator"] else None
				# Сохранение изменений.
				manga["chapters"][BranchID][ChapterIndex] = Buffer

		return manga