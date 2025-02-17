# Melon
**Melon** – это модульная система управления парсерами манги и ранобэ, способная получать информацию о тайтлах, сохранять её в формате JSON, запрашивать обновления и собирать контент в удобный для ознакомления формат.
<p align="center">
	<img src="Source/icon.svg" width=25% height=25% allign="center">
</p>

_Мы уважаем труд сотрудников сайтов, и потому не поставляем никаких решений, связанных с нелегальным получением доступа к платному контенту, а также для снижения нагрузки на эти ресурсы задаём небольшую задержку между запросами._

Проект приветствует добавление парсеров сторонними разработчиками. Для этого создана и постоянно актуализируется подробная документация:
* [Разработка парсера](/Docs/DEVELOPMENT.md)
* [Настройка логов](/Docs/LOGGER.md)
* [Форматы файлов](/Docs/Examples)
* [Обработчик классификаторов](/Docs/TAGGER.md)

## Порядок установки и использования
1. Для установки необходимо наличие системы [Git](https://git-scm.com/) и [Python](https://www.python.org/) версии **3.10** или новее на вашем устройстве.
```Bash
git -v
python3 -V
```
2. Клонируйте репозиторий Melon рекурсивно (для автоматического включения подмодулей) и перейдите в его каталог.
```Bash
git clone https://github.com/Otaku-Melons/Melon --recursive
cd Melon
```
3. Создайте вирутальное окружение Python, после чего активируйте его и установите зависимости.
```Bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
4. Запустите модуль помощи по установке Melon.
```Bash
python main.py install -all
deactivate
```
5. После этого вы сможете использовать систему управления парсерами Melon внутри виртуального окружения, не захламляющего вашу систему ненужными пакетами. Для ознакомления с доступными командами выполните:
```Bash
source .venv/bin/activate
melon help
```

> [!WARNING]  
> На Windows используйте `.venv\Scripts\activate` вместо `source .venv/bin/activate`. Кроме того некоторые функции, например использование алиаса `melon` вместо `python main.py`, не поддерживаются.

# Настройки
Для каждого парсера поставляется файл _settings.json_. Melon ищет его сразу в директории _Configs_, а потом в каталоге самого модуля. Настоятельно рекомендуем редактировать этот файл только внутри _Configs_, это позволит избежать утраты данных при переустановке парсеров, а также поддерживает неизменяемое состояние модулей.

Структура файла настроек унифицирована, последний обязан содержать следующие разделы: _common_, _proxy_, _filters_, _custom_.

## common
Данный раздел содержит обязательные базовые параметры парсера.
___
```JSON
"archives_directory": ""
```
Указывает, куда сохранять построенный контент. При пустом значении будет создана директория `Output/[PARSER_NAME]/archives` в каталоге запуска Melon. Рекомендуется оформлять в соответствии с принципами путей в GNU/Linux.
___
```JSON
"images_directory": ""
```
Указывает, куда сохранять связанные с контентом изображения: обложки тайтлов, иллюстрации, портреты персонажей. При пустом значении будет создана директория `Output/[PARSER_NAME]/images` в каталоге запуска Melon (для каждого тайтла создаётся дополнительный вложенный каталог с названием в виде используемого имени описательного файла). Рекомендуется оформлять в соответствии с принципами путей в GNU/Linux.
___
```JSON
"titles_directory": ""
```
Указывает, куда сохранять описательные файлы. При пустом значении будет создана директория `Output/[PARSER_NAME]/titles` в каталоге запуска Melon. Рекомендуется оформлять в соответствии с принципами путей в GNU/Linux.
___
```JSON
"bad_image_stub": ""
```
Указывает путь к изображению, которое будет заменять содержимое загружаемого слайда, по определённым критериям не являющегося валидным (битый файл, очень малый размер, неверный формат).
___
```JSON
"pretty": false
```
Включает обработку контента для улучшения качества. Например, удаляет точки в конце названий глав манги или пустые абзацы из ранобэ.
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
"retries": 1
```
Указывает количество повторов запроса при неудачном выполнении.
___
```JSON
"delay": 1
```
Задаёт интервал в секундах, выжидаемый между последовательными запросами к серверу. 

## filters
Здесь указываются опциональные фильтры контента. Поддерживается два типа данных: текст и изображение (это отображается в названиях ключей). Сама секция является опциональной и может быть удалена из настроек.
___
```JSON
"text_regexs": []
```
Список регулярных выражений для поиска удаляемых строк.
___
```JSON
"text_strings": []
```
Список удаляемых строк.
___
```JSON
"image_md5": []
```
Список MD5-хэшей игнорируемых изображений.
___
```JSON
"image_min_height": null
```
Минимальная высота валидного изображения.
___
```JSON
"image_min_width": null
```
Минимальная ширина валидного изображения.
___
```JSON
"image_max_height": null
```
Максимальная высота валидного изображения.
___
```JSON
"image_max_width": null
```
Максимальная ширина валидного изображения.

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

_Copyright © DUB1401. 2024-2025._
