from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:
	from .. import CheckLanguageCode, WordsDictionary

def GetDictionaryPreset(language_code: str) -> "WordsDictionary | None":
	"""
	Возвращает готовый словарь ключевых локальных определений.

	:param language_code: Код языка по стандарту ISO 639-3.
	:type language_code: str
	:return: Пресет словаря для определённого языка.
	:rtype: WordsDictionary | None
	"""

	CheckLanguageCode(language_code)

	try:
		Module = importlib.import_module(f".{language_code}", package = __package__)
		return getattr(Module, f"WordsDictionary_{language_code}")
	
	except (ModuleNotFoundError, AttributeError):
		return None