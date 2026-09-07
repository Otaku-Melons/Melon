from dataclasses import dataclass

@dataclass
class GeneratorOptions:
	"""Настройки генератора модели."""

	is_mirror_available: bool = False
	is_multiple_parsers_allowed: bool = False
	is_force_mode_available: bool = False

@dataclass(frozen = True)
class ProcessorOptions:
	"""Настройки обработчика."""

	use_timer: bool = True
