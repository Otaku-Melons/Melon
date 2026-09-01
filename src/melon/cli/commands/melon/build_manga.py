from dataclasses import dataclass
from typing import Literal, cast

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from ....builders.manga import MangaBuilder, MangaOutputFormats
from ....core.base.formats.base_format.enums import By
from ..base_processor import PreparedData
from ..base_processor.templates import T_SingleParserRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	filename: str
	target_id: int | None
	target_type: Literal["branch", "chapter"] | None
	output_format: str | None
	chapter_template: str | None
	volume_template: str | None
	is_sort_by_volumes: bool

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Build read-ready manga content."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("FILE", "Filename of local JSON.", important = True)
		ComPos.set_argument()

		self._AddParserPosition()

		ComPos = command.create_position("TARGET", "Target for building. By default longest branch.")
		ComPos.add_key("--branch", value_type = ValidableTypes.UnsignedInteger, description = "Branch ID.")
		ComPos.add_key("--chapter", value_type = ValidableTypes.UnsignedInteger, description = "Chapter ID.")

		ComPos = command.create_position("FORMAT", "Format of output content. By default downloads images in folder.")
		ComPos.add_flag("-cbz", description = "Make *.CBZ files.")
		ComPos.add_flag("-pdf", description = "Make *.PDF file.")
		ComPos.add_flag("-zip", description = "Make *.ZIP archives.")

		command.base.add_flag("-s", description = "Enable chapters sorting by volumes directories.")

		command.base.add_key("--cnt", description = "Template for chapters naming.")
		command.base.add_key("--vnt", description = "Template for volumes naming.")

		return command

	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> Parameters:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedData
		:return: Структура **dataclass**.
		:rtype: Parameters
		"""

		Filename: str = data.get_important_position_value("FILE", expected_type = str)
	
		TargetID: int | None = data.get_position_value("TARGET", expected_type = int)
		TargetType: Literal["branch", "chapter"] | None = None
		if data.check_key("--chapter"): TargetType = "chapter"
		elif data.check_key("--branch"): TargetType = "branch"
	
		OutputFormat: str | None = data.get_position_value("FORMAT", expected_type = str)
		if OutputFormat: OutputFormat = OutputFormat.lstrip("-")
	
		ChapterTemplate: str | None = data.get_key_value("--ct", expected_type = str)
		VolumeTemplate: str | None = data.get_key_value("--vt", expected_type = str)
	
		SortByVolumes: bool = data.check_flag("-s")

		return Parameters(
			filename = Filename,
			required_parser = prepared_data.required_parsers[0],
			target_id = TargetID,
			target_type = TargetType,
			output_format = OutputFormat,
			chapter_template = ChapterTemplate,
			volume_template = VolumeTemplate,
			is_sort_by_volumes = SortByVolumes
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		TypingResult = parameters.required_parser.source_operator.get_content_type_by_file(parameters.filename)
		Parser = parameters.required_parser.source_operator.launch_parser(TypingResult.content_type)
		Title = Parser.init_empty_title(TypingResult.slug)
	
		if Title.load(parameters.filename, By.Filename):
			self.printer.emit(f"Loaded file: <i>{parameters.filename}</i>.")
		else:
			self.printer.error(f"Unable load file: <b>{parameters.filename}</b>.")
			return False
	
		Builder = MangaBuilder(Parser, Title)
		if parameters.output_format: Builder.select_output_format(MangaOutputFormats(parameters.output_format))
		if parameters.chapter_template: Builder.set_chapter_name_template(parameters.chapter_template)
		if parameters.chapter_template: Builder.set_volume_name_template(parameters.chapter_template)
		Builder.switch_volumes_sorting(parameters.is_sort_by_volumes)
	
		match parameters.target_type:
			case "branch": Builder.build_branch(parameters.target_id)
			case "chapter": Builder.build_chapter(cast(int, parameters.target_id))
			case _: Builder.build_branch()

		return True