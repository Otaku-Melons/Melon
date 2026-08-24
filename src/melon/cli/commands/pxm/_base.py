from ..base_processor import PARAMS, BaseCommandProcessor

class CommandProcessorTemplate(BaseCommandProcessor[PARAMS]):
	"""Контейнер шаблонов генерации команд."""
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ГЕНЕРАЦИИ КОМАНДЫ <<<<< #
	#==========================================================================================#

	def _AddSettingsExportStrategyPosition(self):
		"""Добавляет позицию стратегии слияния конфигурации."""

		ComPos = self._Command.create_position("STRATEGY", "Strategy of config installation conflict resolution.")
		ComPos.add_flag("-s", description = "Skip installation (default).")
		ComPos.add_flag("-o", description = "Overwrite exists config.")
		ComPos.add_flag("-m", description = "Merge exists config parameters with preset.")

	def _AddParserPosition(self):
		"""Добавляет позицию имени парсера, используюмую **pxm**."""

		ComPos = self._Command.create_position("PARSER", "Parser name.", important = True)
		ComPos.set_argument()
	