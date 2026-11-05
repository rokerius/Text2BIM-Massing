# Карта переноса

Текущие возможности — в [status.md](status.md), устройство процессов — в
[architecture.md](architecture.md), подтверждение проверок — в
[validation.md](validation.md). Эта карта отвечает за происхождение кода.

Text2BIM: `b71b83d0d6640e7dfe7af3fda17b40fb3cfd70dc`.
Маслов: `607ff1fcf80477787409522d93e18e42ac1436cf`.

Оригиналы выбранных файлов сохраняются в `upstream/<project>/`. Их Git blob SHA
и SHA-256 перечислены в `manifest.json` и проверяются тестом. Эти каталоги
не являются исполняемым backend и не входят в wheel; они входят в sdist.

## Text2BIM

| Исходный файл/фрагмент | Рабочее место | Изменения и статус |
| --- | --- | --- |
| `tool_agent/python_interpreter.py`, весь файл | `src/text2bim_massing/_vendor/text2bim/python_interpreter.py` | Единственная правка: `evaluate()` выбрасывает `InterpretorError` после SyntaxError. Точное текстовое сравнение с этой правкой проверяется тестом. |
| `tool_agent/utils.py`: `safe_encode`, `remove_last_human_message_with_regex`, `clean_code_for_chat_extend` | `src/text2bim_massing/_vendor/text2bim/utils.py` | Тела функций без изменений; удалены неиспользуемые функции, импорты `vs` и работы с изображениями. Равенство AST проверяется тестом. |
| `tool_agent/agents.py`: `OpenAiAgent.generate_many`, `generate_one`, `_chat_generate`, инициализация SDK | `src/text2bim_massing/llm.py` | Сохранены интерфейс генерации, Chat Completions и user-message. Убрано наследование от HuggingFace Agent; добавлены конфигурация endpoint/timeout, явные параметры, usage, счётчик вызовов и подмена транспорта для тестирования. Неверное ветвление по имени модели заменено явной конфигурацией. |
| `tool_agent/agents.py`: `MyAgent.chat`, `chat_with_function_call`, `chat_check`, `plan_designer` | `_vendor/text2bim/agents.py` | Сохранены порядок подстановок placeholders, разбор code blocks и роли. Убраны HuggingFace/vs, добавлены инъекция транспорта и исполнителя. Рекурсивное исправление заменено ограниченным циклом с тем же числом попыток по конфигурации; инструкция об уже выполненном коде изменена на полный rollback неуспешного скрипта. |
| `tool_agent/multi_agents_workflow.py`: `run_po_coder_agents`, `run_agent_checking_loop` | `workflow.py` | Сохранены PO→Programmer и Reviewer→исполняемый патч, включая структуру исходного patch request. IFC/Solibri, frontend и глобальные пути заменены immutable архивом и внешним evaluator. Reviewer возвращает JSON-решение с ID оценённого кандидата; ядро не выводит score из отчёта. |
| Четыре файла `tool_agent/muti_agent_prompt/*.txt` | `_vendor/text2bim/prompts/` + `prompts.py` | Оригинальные ресурсы не меняются. `prompts.py` заменяет Vectorworks, исправляет имя plan_designer, уточняет ограничения исполнения и snapshot/evaluate/select. У Architect сохранены роль и вставка задачи, BIM checklist/few-shot заменены инструкциями о контурах и экструзиях. Reviewer получает JSON-отчёт и формат выбора кандидата. Все рабочие промпты сохраняются в запуске. |
| `tool_agent/vw_tools_extend.py`: `CreatePolygon`, `GetPolygonVertex`, `GetVertNum`, `Move`, `DeleteTool`, `DuplicateObj`, `RotateObj` | `src/text2bim_massing/tools.py` | Сохранены имена функций инструментов и смысл общих операций. Их реализации новые: `vs`, слои и наследование `transformers.Tool` заменены вызовами `Scene`. У `create_polygon`/`duplicate_obj` убран `layer_uuid`; добавлены инструменты массингов и чтения состояния. |
| `requirements.txt` | `pyproject.toml` | Из исходных провайдеров подключён один OpenAI SDK исходной версии 1.82.0. SDK Mistral/Anthropic/Google, transformers 4.30.2, ptvsd, python-dotenv, pillow, ifcopenshell пока не подключаются. API-ключ читается из окружения. Геометрия добавляет Shapely; mesh-extra согласован с зависимостями Маслова. |

Стены, окна, двери, кровли, IFC-экспорт, GUI и Solibri не переносились: они не
входят в контракт массингов. Оригинальный `vs.py` не используется.

## Маслов

| Исходный фрагмент | Рабочее место | Изменения и статус |
| --- | --- | --- |
| `src/polygons_to_shapely_converter.py`: `PolygonsToShapelyConverter.__call__` | `_vendor/maslov/polygons_to_shapely_converter.py` | Метод без изменений. Убраны `Function` и неиспользуемые импорты. |
| `src/shapely_to_polygons_converter.py`: `ShapelyToPolygonsConverter.__call__` | `_vendor/maslov/shapely_to_polygons_converter.py` | Метод без изменений. Убраны `Function` и неиспользуемые импорты. |
| `src/mesh_compiler/massing_mesh_compiler.py` | Внешний checkout; `adapters.compile_mesh` | Исходный класс импортируется в интеграционных тестах без изменений. Адаптер оборачивает экструзии в список зданий. |
| `SampleMetric` и `SampleProcessor` | `adapters.SampleMetricAdapter`, `SampleProcessorAdapter` | Компонент передаётся извне. Вложенность выбирается явно: `extrusions`, `building`, `buildings`. Отчёт не агрегируется в score; поля процессора задаются явно. |

Валидация входа и канонизация представления в `geometry.py` — новый код.
Валидные кольца обрабатываются исходной семантикой Маслова: вложенное кольцо
вычитается, остальные объединяются. Канонизация меняет порядок/ориентацию
вершин, но проверяет топологическое равенство формы после обратного преобразования.
Кольца выдаются по убыванию площади, чтобы внешнее кольцо и его отверстие
предшествовали острову внутри отверстия: исходный конвертер зависит от порядка.
Тела обоих исходных конвертеров остаются неизменными.

Сцена, транзакции и неизменяемое сериализованное состояние — новый код.
Профиль и созданная из него экструзия независимы. При изменении профиля
существующая экструзия сохраняет захваченную геометрию.

## Новое окружение исполнения и транспорта

`execution.py`/`_worker.py` запускают неизменённый по существу исходный AST
интерпретатор в отдельном процессе. Проверка AST ограничивает импорты и доступ
к private атрибутам; доступны только документированные инструменты, math и
ограниченный набор builtins. Время, вывод, код и сериализованное состояние
ограничены. Успех принимает сцену и переменные вместе; ошибка не принимает ни то,
ни другое. Отчёты уже выполненных внешних оценок остаются в архиве и учитываются
в бюджете даже при последующей ошибке скрипта.

Оценка проходит через RPC к parent: generated code не получает evaluator или
LLM credentials. `archive.py` фиксирует snapshot, отчёт и состояние. Отдельный
`_evaluate_worker.py` выполняет доверенный внешний callable; cloudpickle нужен
для замыканий и объектов оценщиков, а результат возвращается только как JSON.
Это новый код замены Vectorworks/Solibri.

`runtime.py` даёт общий учёт LLM-вызовов, оценок, времени, истории и расходов.
`llm.py` добавляет разбор native tool calls; передача tool responses и повторный
запрос основаны на `OpenAiAgent.generate_with_function_call` исходного Text2BIM.
Retries API отключаются внутри бюджетированного запуска, чтобы не скрывать
дополнительные попытки.

`codex_client.py` — новый transport по указанию пользователя: официальный Codex
CLI с сохранённой ChatGPT авторизацией. Он получает те же адаптированные роли,
но оборачивает ответ в JSON Schema; запрос Architect передаётся JSON-конвертом
вместо native API tool call. Используются read-only и ephemeral режимы CLI,
проверяется отсутствие его внутренних tool actions. Это явное отличие от
исходного провайдера/модели эксперимента. API-ключи не передаются в этот CLI.

`config.py`, `cli.py`, `__main__.py`, публичный `generate` и JSON-примеры — новый
код standalone runner. `provenance.json` записывает source commits и транспорт;
default-модель CLI обозначается явно как незафиксированная. CLI дополнительно
сохраняет входной runner config. Сам CLI не изменяет внешний checkout.


## Полный реестр и внешний эксперимент

[Проверяемый реестр](text2bim-diff.md) включает disposition всех 44 исходных
файлов и 156 declarations выбранных Python-файлов, diff перенесённых функций,
инструментов, зависимостей и рабочих промптов mm/m. Каждому файлу проекта
соответствует причина, влияние и проверка в `adaptation-spec.json`.
`tools/audit_adaptation.py --check` проверяет эту карту и хеши текущего состояния.

`integrations/maslov/` — новый внешний runner/config/README. Точные копии
трёх файлов добавлены в `experiments/methods/text2bim_adapted/` checkout Маслова.
Runner импортирует закреплённый пакет и существующие `BuildingFloorCount` и
`SiteMatch`; ядро пакета и метод Маслова для этого не меняются. Context содержит
только `id`, `site_contour`, `requirements`. Реестр описывает ограничения
пилота с одним зданием и явные цели конфига; это не полная benchmark-интеграция.


`integrations/maslov/run.py` теперь поддерживает task_mode requirements.
`with_canonical_area` и `BuildingBrief` импортируются из исходного
`subtractive_additive_massing/brief.py` исключительно для нормализации данных
и производных целей; алгоритмы поиска/разбиения не вызываются. Runtime Text2BIM
не меняется. Новый requirements.json подключает исходные FloorCountError,
UsableAreaError, SiteMatch и IdIoU с фактическими требованиями каждого sample.
Схема, отказ unknown values и provenance описаны в requirements.md интеграции.
