from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ....core.base.source_operator import (
		BaseSourceOperator,
		ParserManifest,
		ParserSettings,
	)

@dataclass(frozen = True)
class DataclassStub:
	"""Заглушка для команд, не требующих параметров."""

	pass

@dataclass(frozen = True)
class ProcessorOptions:
	"""Контейнер настроек обработчика."""

	use_timer: bool = True

@dataclass(frozen = True)
class RequiredParser:
	"""Коллекция управляющих объектов трубемого парсера."""

	name: str
	source_operator: "BaseSourceOperator"
	manifest: "ParserManifest"
	settings: "ParserSettings"

@dataclass(frozen = True)
class PreparedData:
	"""Предподготолвенные данные."""

	required_parsers: tuple[RequiredParser, ...]
	is_force_mode_enabled: bool
	mirror: str | None