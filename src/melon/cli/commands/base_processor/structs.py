from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ....core.base.source_operator import (
		BaseSourceOperator,
		ParserManifest,
		ParserSettings,
	)
	from ....core.system_objects.manager.parsers import ParserOperator

@dataclass(frozen = True)
class DataclassStub:
	"""Заглушка для команд, не требующих параметров."""

	pass

@dataclass(frozen = True)
class ProcessorOptions:
	"""Контейнер настроек обработчика."""

	use_timer: bool = True
	allow_multiple_parsers: bool = False

@dataclass(frozen = True)
class RequiredParser:
	"""Коллекция управляющих объектов трубемого парсера."""

	name: str
	parser_operator: "ParserOperator"
	source_operator: "BaseSourceOperator"
	manifest: "ParserManifest"
	settings: "ParserSettings"

@dataclass(frozen = True)
class PreparedData:
	"""Предподготолвенные данные."""

	required_parsers: tuple[RequiredParser, ...]
	is_force_mode_enabled: bool
	mirror: str | None