from typing import TYPE_CHECKING

from Source.Core import Exceptions

if TYPE_CHECKING:
	from Source.Core.SystemObjects import SystemObjects

def GetParsersNamesFromKey(system_objects: "SystemObjects", key_value: str | None, all_by_default: bool = True) -> tuple[str, ...]:
	"""
	Парсит и валидирует имена затребованных парсеров из значения ключа `--use` команды.

	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param key_value: Значение ключа.
	:type key_value: str | None
	:param all_by_default: Указывает, нужно ли при отсутствии указанных парсеров выбрать все установленные.
	:type all_by_default: bool
	:raises Exceptions.System.ParserNotFound: Парсер не найден.
	:return: Последовательность имён затребованных парсеров.
	:rtype: tuple[str, ...]
	"""

	Parsers: tuple[str, ...] = ()

	if key_value:
		Parsers = tuple(Element.strip() for Element in key_value.split(","))

	AllParsers: tuple[str, ...] = system_objects.driver.parsers_names

	if not Parsers:
		if all_by_default:
			Parsers = AllParsers
	else:
		for CurrentParser in Parsers:
			if CurrentParser not in AllParsers:
				raise Exceptions.System.ParserNotFound(CurrentParser)
			
	return Parsers