# Melon
**Melon** – это модульный парсер манги и ранобэ, способный получать всю информацию о тайтлах в JSON, запрашивать обновления и собирать контент в удобный для ознакомления формат.

<p align="center">
	<img src="Source/icon.svg" width=25% height=25% allign="center">
</p>

Проект приветствует добавление парсеров сторонними разработчиками. Для этого создана и постоянно актуализируется подробная документация:
* [Разработка парсера](/Docs/DEVELOPMENT.md)
* [Настройка логов](/Docs/LOGGER.md)
* [Форматы описательных файлов](/Docs/Examples)

## Порядок установки и использования
1. Скачать и распаковать последний релиз.
2. Убедиться в доступности на вашем устройстве Python версии не старше **3.10**.
3. Открыть каталог со скриптом в терминале: можно воспользоваться командой `cd` или встроенными возможностями файлового менеджера.
4. Создать виртуальное окружение Python.
```
python -m venv .venv
```
5. Активировать вирутальное окружение. 
```
# Для Windows.
.venv\Scripts\activate.bat

# Для Linux или MacOS.
source .venv/bin/activate
```
6. Установить зависимости.
```
pip install -r requirements.txt
```
7. Произвести настройку путём редактирования файла _Settings.json_.
8. В вирутальном окружении указать для выполнения интерпретатором файл `main.py`, передать ему необходимые параметры и запустить.

# Консольные команды
Вся документация по CLI поставляется в самообновляемом формате. Для получения доступа к ней используются следующие команды:
```
# Список доступных команд.
main.py help

# Подробная информация о конкретной команде.
main.py help command
```

# Настройки
Для каждого парсера в его же каталоге поставляется файл _settings.json_. Он обязан содержать следующие разделы: _common_, _proxy_, _custom_. Таким образом достигается максимальная гибкость конфигурации.

## common
Данный раздел содержит обязательные базовые параметры парсера.
___
```JSON
"archives_directory": ""
```
Указывает, куда сохранять построенный контент. При пустом значении будет создана директория `Output/[PARSER_NAME]/archives` в каталоге запуска Melon. Рекомендуется оформлять в соответствии с принципами путей в Linux.
___
```JSON
"covers_directory": ""
```
Указывает, куда сохранять обложки тайтлов. При пустом значении будет создана директория `Output/[PARSER_NAME]/covers` в каталоге запуска Melon (для каждого тайтла создаётся дополнительный вложенный каталог с названием в виде используемого имени описательного файла). Рекомендуется оформлять в соответствии с принципами путей в Linux.
___
```JSON
"titles_directory": ""
```
Указывает, куда сохранять описательные файлы. При пустом значении будет создана директория `Output/[PARSER_NAME]/titles` в каталоге запуска Melon. Рекомендуется оформлять в соответствии с принципами путей в Linux.
___
```JSON
"use_id_as_filename": false
```
Указывает способ именования описательных файлов и зависимых каталогов. При активации будет использоваться целочисленный идентификатор, по умолчанию – алиас.
___
```JSON
"sizing_images": false
```
Указывает, следует ли пытаться найти данные о разрешении изображений и заносить их в описательный файл.
___
```JSON
"legacy": false
```
Включает режим совместимости с устаревшими форматами [DMP-V1](/Docs/Examples/dmp-v1.md) и [DNP-V1](/Docs/Examples/dnp-v1.md).
___
```JSON
"tries": 1
```
Указывает количество повторов запроса до получения удовлетворительного статуса.
___
```JSON
"delay": 1
```
Задаёт интервал в секундах, выжидаемый между последовательными запросами к серверу. 

## proxy
Данный раздел описывает данные прокси-сервера, использующегося для установки соединения с ресурсом.
___
```JSON
"enable": false
```
Переключает использование прокси-сервера.
___
```JSON
"host": ""
```
Указывает IP-адрес прокси-сервера.
___
```JSON
"port": ""
```
Указывает порт прокси-сервера.
___
```JSON
"login": ""
```
Указывает логин для авторизации на прокси-сервере. Необязательный параметр для публичных серверов.
___
```JSON
"password": ""
```
Указывает пароль для авторизации на прокси-сервере. Необязательный параметр для публичных серверов.

## custom
Данный раздел содержит параметры отдельных парсеров, не поддающиеся унификации. Такие опции должны быть описаны в _README.md_ файле, находящемся в домашнем каталоге парсера.

_Copyright © DUB1401. 2024._
