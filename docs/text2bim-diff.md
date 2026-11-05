# Проверяемые отличия от Text2BIM

Сгенерировано `python tools/audit_adaptation.py --write`; проверка — `--check`.

Граница аудита: полный Git tree исходного commit, все declarations пяти выбранных
Python-файлов, все файлы standalone-проекта, перенесённые фрагменты и четыре промпта.
Хеши фиксируют проверенное состояние; причины и влияние задаются вручную в adaptation-spec.json.

Это проверка полноты заявленной карты и точных diff, а не доказательство эквивалентности методов.

## Исходные файлы

| Файл | Статус | Причина |
| --- | --- | --- |
| `.gitignore` | replaced | Standalone Python/Linux packaging и документация заменяют настройку Vectorworks/Windows. |
| `.vscode/launch.json` | replaced | Standalone Python/Linux packaging и документация заменяют настройку Vectorworks/Windows. |
| `LICENSE` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `README.md` | replaced | Standalone Python/Linux packaging и документация заменяют настройку Vectorworks/Windows. |
| `data/state.json` | replaced | Global GUI state заменён per-run snapshot и interpreter state; входных UUID Vectorworks нет. |
| `data/test.wav` | excluded | Демо/аудио/иллюстрации не являются входом standalone text-only massing workflow. |
| `data/test_env_2024_new.vwx` | excluded | Проприетарная исходная сцена Vectorworks; заменена новой сценой массингов. |
| `data/test_env_2025_new.vwx` | excluded | Проприетарная исходная сцена Vectorworks; заменена новой сценой массингов. |
| `demo.gif` | excluded | Демо/аудио/иллюстрации не являются входом standalone text-only massing workflow. |
| `method.png` | excluded | Демо/аудио/иллюстрации не являются входом standalone text-only massing workflow. |
| `requirements.txt` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `test_prompt.txt` | excluded | Исходные BIM/Vectorworks задачи не выдаются за massing benchmark; новые проверки помечены отдельно. |
| `tool_agent/Ifc_test_data/.gitignore` | replaced | IFC/Solibri/BCF engine/checking заменены внешним callable evaluator и JSON report. |
| `tool_agent/Ifc_test_data/sample_model.ifc` | replaced | IFC/Solibri/BCF engine/checking заменены внешним callable evaluator и JSON report. |
| `tool_agent/Solibri_workflow_xml.xml` | replaced | IFC/Solibri/BCF engine/checking заменены внешним callable evaluator и JSON report. |
| `tool_agent/agents.py` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/multi_agents_workflow.py` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/muti_agent_prompt/checker_chat_prompt_temp.txt` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/muti_agent_prompt/coder_chat_prompt_temp.txt` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/muti_agent_prompt/floor_plan_designer_chat_prompt_few_shots.txt` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/muti_agent_prompt/po_chat_prompt_temp.txt` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/python_interpreter.py` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/solibri_checker.py` | replaced | IFC/Solibri/BCF engine/checking заменены внешним callable evaluator и JSON report. |
| `tool_agent/solibri_data/.gitignore` | replaced | IFC/Solibri/BCF engine/checking заменены внешним callable evaluator и JSON report. |
| `tool_agent/solibri_data/LLM-checking-FullExample.smc` | replaced | IFC/Solibri/BCF engine/checking заменены внешним callable evaluator и JSON report. |
| `tool_agent/speech2text.py` | excluded | Интерфейс Vectorworks/голосовой ввод вне текстового API; GUI/audio flow не переносится. |
| `tool_agent/test_code.py` | excluded | Исходные BIM/Vectorworks задачи не выдаются за massing benchmark; новые проверки помечены отдельно. |
| `tool_agent/utils.py` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `tool_agent/vs.py` | excluded | API-заглушки vs.py не являются рабочим геометрическим движком. |
| `tool_agent/vs_interface.py` | excluded | Интерфейс Vectorworks/голосовой ввод вне текстового API; GUI/audio flow не переносится. |
| `tool_agent/vw_tools_extend.py` | archived | Оригинал сохранён с Git blob SHA; перенос/исключения declarations указаны ниже. |
| `web_palette/.gitignore` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/LICENSE` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2024/WebPaletteTUM.vlb` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2024/WebPaletteTUM.vwr/Strings/WebPaletteTUM.vwstrings` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2024/WebPaletteTUM.vwr/html/index.html` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2024/WebPaletteTUM.vwr/html/main.js` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2025/WebPaletteTUM.vlb` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2025/WebPaletteTUM.vwr/Strings/ExtMenuShowWebPaletteTUM.vwstrings` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2025/WebPaletteTUM.vwr/Strings/WebPaletteTUM.vwstrings` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2025/WebPaletteTUM.vwr/html/index.html` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/Palette2025/WebPaletteTUM.vwr/html/main.js` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/README.md` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |
| `web_palette/software_architect.png` | excluded | Web palette/Vectorworks SDK UI вне standalone massing API; соответствующие assets/licensing не распространяются. |

## Отличия метода

### SOURCES: Фиксация полного источника

Полный tree исходного commit сохранён; 11 выбранных файлов скопированы побайтово. Остальные файлы явно исключены по назначению.

Влияние: Содержимое оригиналов не меняется. Это bounded audit перенесённого baseline, не утверждение эквивалентности всей GUI-системе.

Проверка: Git blob SHA/SHA-256, полный file/declaration inventory, tests/test_sources.py и audit --check.

### GEOMETRY: Замена Vectorworks геометрией массингов

Vectorworks/Solibri отсутствуют в standalone Linux контракте. Два конвертера Маслова сохраняют тела методов. Сцена и инструменты написаны заново.

Влияние: Нет стен, окон, дверей, слоёв, IFC или vs.py. Добавлены экструзии, отверстия, компоненты и стабильные ID. Проверка >=3 вершин, finite/valid geometry, положительной высоты и canonical ring order отличаются от GUI; перевода произвольной BIM-сцены нет.

Проверка: Дифф конвертеров, геометрические тесты, исходный MassingMeshCompiler.

### TOOLS: API инструментов и единицы

Сохранены общие имена инструментов, индексация вершин с нуля, UUID и возвраты move/rotate; layer_uuid удалён. Добавлены профиль, экструзия, редактирование, чтение и экспорт.

Влияние: Tool units mm по умолчанию в RunConfig, m во внешнем формате; m разрешён явно. Move принимает defaults/списки, rotate расширен на список, profiles независимы от solids. Канонизация может менять порядок вершин. FindSelect и GUI selection не переносятся.

Проверка: tests/test_tools_interpreter.py, test_geometry_scene.py; точная карта API в tools.py.

### INTERPRETER: Исправление SyntaxError

Исходный интерпретатор сохранён целиком; ast.parse SyntaxError теперь выбрасывает InterpretorError вместо (None,state).

Влияние: Устраняет ложный успех. Остальные исходные ветви, включая fuzzy lookup имён/ключей, не исправлялись.

Проверка: Точный full-file diff и регрессия SyntaxError.

### EXECUTION: Ограниченное исполнение и состояние

Отдельный процесс с тайм-аутом не может надёжно вернуть промежуточное состояние при принудительном завершении. Сцена и variables принимаются вместе только после успеха попытки.

Влияние: Это инженерный выбор, более строгий, чем частичное исполнение Text2BIM: все code blocks одного ответа объединяются; no-code считается ошибкой; весь неуспешный script откатывается. Разрешены только JSON-кодируемые data, math aliases, ограниченные builtins/imports/AST. Функции, classes, async, private access запрещены. Это не OS sandbox.

Проверка: Тайм-аут, размеры code/output/state, rollback сцены и mutable variables, сохранение math/tuple/UUID; tests/test_execution.py.

### AGENTS: Перенос ролей и исправлений

MyAgent больше не наследует HF Agent; tool descriptions, transport, executor и log инъецируются. Prompt substitutions и clean_code_for_chat_extend сохранены.

Влияние: Enhancer→Architect по запросу→Programmer, Reviewer→patch. Recursive repair заменён ограниченным циклом; default 2 исправления = исходным 3 попыткам. Repair-инструкция изменена из-за rollback; prompt/history repair накапливается. Удалены unused return_code/remote/is_reviewing/kwargs и documentation_retrieval branch.

Проверка: Role/call ordering, no-code/SyntaxError repair, source fragment diffs, tests/test_workflow.py.

### PROMPTS: Адаптация четырёх промптов

Оригинальные ресурсы не редактируются. Runtime заменяет Vectorworks, исправляет plan_desinger, описывает supported tools/rollback/snapshots.

Влияние: Architect BIM checklist и wall/door example заменены массингами; исходные framing, rationality, few-shot format и task suffix сохранены. В пример явно добавлен floor_height во вход пользователя. Reviewer выдаёт JSON decision/guidance, а не свободный текст; единицы m изменяются только по конфигурации.

Проверка: Точные diff всех четырёх промптов для mm и m; prompts.json каждого запуска.

### LLM: Один конфигурируемый клиент

Из четырёх провайдеров исходника подключён один OpenAI Chat Completions SDK той же версии 1.82.0; clients и budgets вынесены отдельно.

Влияние: Исходные model defaults и всегда истинное o1/o4 ветвление не сохраняются: model/temperature/reasoning/stop задаются явно; send_stop=False по умолчанию. Автоматические retries внутри generate отключены. Images и остальные providers не переносятся. Native multiple tool calls и original unknown-function fallback сохранены. Неверные/пустые ответы отклоняются.

Проверка: Настоящий SDK с mock HTTP, explicit timeout/usage/errors и multiple Architect/fallback tests.

### CODEX: Transport через подписку по запросу пользователя

Codex CLI не является исходным OpenAI API эксперимента; отдельный backend использует saved ChatGPT login.

Влияние: CLI получает JSON-конверт conversation/functions и JSON Schema response, свои system/developer instructions и reported usage. Native tool calls эмулируются JSON. Stop sequences CLI не реализует. Read-only/ephemeral, без внутренних tools/API-key forwarding. Default model не зафиксирован; для experiment нужен explicit model.

Проверка: Fake CLI protocol/env test, четыре живых задания macOS/Linux; docs/validation.md.

### ARCHIVE: Snapshot, оценка и выбор

Внешний report относится к immutable snapshot. Archive/commit/evaluate/select обязательны по контракту; arbitrary report не имеет встроенного score.

Влияние: Host оценивает current snapshot, если agent не сделал этого; cached report и выбор не переоцениваются. Reviewer может выбрать старый candidate; для patch восстанавливаются его scene и variables. Уже выполненные оценки/архив не откатываются при последующей ошибке script. Нет исходного stop по пустому issue_str или GUI YNDialog. Completed означает решение Reviewer, не физическую валидность.

Проверка: stale report, cache, earlier selection, failed script after evaluation; tests/test_workflow.py.

### CONTEXT: Передача внешней задачи

Task context добавлен к входу Enhancer и Reviewer. Programmer получает только answer Enhancer, как в run_po_coder_agents.

Влияние: Дополнительный обход Enhancer удалён. Patch request expression восстановлено без изменений; добавлено только состояние выбранной scene с ID, необходимое при archive selection.

Проверка: source patch assignment AST equality, test_initial_programmer_receives_the_enhancer_answer_without_a_bypass.

### BUDGETS: Лимиты и trace

GUI-контроль и global state/log paths заменены RunConfig, per-run files, process timeouts и учитываемыми LLM/evaluator attempts.

Влияние: Итерации, calls, evals, repairs, время, память Linux и размеры ограничены. Недостающий код не считается успехом. Любая незавершённость возвращает статус/архив; при нехватке бюджета selected может отсутствовать. В cost только фактический usage и заданные пользователем цены, для подписки без цены null.

Проверка: Budget/error/status/partial-result tests; config.json, history.jsonl, provenance.json.

### EVALUATOR: Внешние компоненты

SampleMetric/SampleProcessor передаются извне через явные layouts; evaluator executes in a separate fresh interpreter.

Влияние: Нет Solibri/BCF, GUI или встроенного критерия. Metric приводится к float, processor report keys выбираются конфигом, NaN/non-JSON отклоняются. Cloudpickle применяется только к доверенному evaluator, не к generated code; объекты с несериализуемым состоянием возвращают evaluation_failed.

Проверка: Настоящие metric/processor, timeout/serialization/JSON tests и Linux tests.

### PACKAGING: Standalone пакет, зависимости и инфраструктура

Установочный пакет, Python 3.11–3.13 под контракт Маслова, CLI, tests, Docker/CI и документация созданы заново.

Влияние: Shapely/cloudpickle добавлены; maslov/mesh extras optional. Transformers, multimodal/BIM/GUI/other-provider dependencies не подключаются. Нет NSGA-II или параметризации нашего метода в Text2BIM.

Проверка: pyproject.toml/requirements-dev.txt, wheel/sdist/core-only smoke и Docker/Linux.

### INTEGRATION: Тонкий внешний пилот Маслова

После проверки ядра добавлены отдельные runner/config/README в integrations/maslov и их точные копии в experiments/methods/text2bim_adapted внешнего checkout. Установленный пакет проверяется по Git SHA; core/runtime не изменяется.

Влияние: Каждый sample запускает независимый generate. В контексте только id/site_contour/requirements; target building не передаётся. Поддерживается одно здание; многозданные rows отклоняются. Метрики FloorCount/SiteMatch объединяются в отдельные поля, без score. Два этажа, высота 3 м, модель gpt-6.1-sol и бюджеты — явная конфигурация диагностического пилота. Это ещё не общий benchmark и не новый алгоритм разбиения участка. Выбор assessed candidate и частичные результаты сохраняются.

Проверка: Регрессия IDs/target leakage, неподдерживаемых требований, выбора samples, drift package pin и двух независимых scripted runs с исходными метриками; живой Linux-пилот на реальном участке фиксируется в validation.md.

### DOCUMENTATION: Документация текущего состояния и оформление GitHub

По запросу пользователя README и план переписаны по фактическим возможностям; статус отделён от исторического журнала, инструкции и доказательства вынесены на отдельные страницы. Добавлены contributor guide, changelog, GitHub templates и атрибуты сохранения исходных байтов.

Влияние: Алгоритм генерации, runtime, зависимости, исходники и конфиг пилота не изменяются. Новые файлы описывают уже реализованное поведение, пределы доказательств и следующие задачи. GitHub vendor/generated атрибуты меняют только отображение и преобразование строк; pinned/vendor файлы исключены из нормализации.

Проверка: Сверка с кодом и артефактами, локальные Markdown-ссылки и синтаксис примеров, существующие тесты и аудит, сборка sdist и проверка его инвентаря; исходные bytes и runtime pin остаются проверяемыми.

### REQUIREMENTS: Реальные требования sample во внешнем runner

Отдельный task_mode requirements формирует задачу по каждому sample. Внешние чистые with_canonical_area/BuildingBrief переиспользуются из закреплённого checkout Маслова, без копирования и запуска алгоритма поиска. Новый requirements.json задаёт четыре исходные метрики; prepare-only сохраняет binding до LLM.

Влияние: Runtime, порядок ролей и исходники Text2BIM не меняются. Одна постройка, сохранение ID, alias usable_area->total_area, явная числовая валидация без скрытых defaults. Нулевые/неизвестные/дробные этажи и неполные цели отклоняются до модели; это ограничение fully-stated subset, а не общий fallback Маслова. Высота и средняя площадь этажа — производные входных данных. Четыре метрики сохраняются раздельно; общей функции score нет. Dataset читается один раз для совпадения SHA и фактического входа. Текущая цель по уточнению пользователя — один массинг; test split и массовая сборка отложены. --sample обозначает единичный вход (--dataset сохранён как алиас).

Проверка: test_maslov_runner.py: валидация чисел, исходный alias helper, отсутствие изменений входа и target leakage, prepare-only без клиента, отказ плохой второй строки до LLM, два разных requirements/бюджета и Reviewer-патч, исходные метрики на отверстиях/компонентах/вертикальном переносе. Живой Linux-запуск реального CoMa sample 1627 фиксируется в validation.md.

### CHECKPOINTS: Согласованные checkpoints и воспроизводимый экспорт

Ревью выявило две воспроизводимые ошибки: полный скрипт мог строить геометрию после commit вместо выбранного snapshot; variables после commit терялись при восстановлении. Worker записывает фактические мутации/аргументы/IDs, код экспорта воспроизводит их, source хранится отдельно. Повторное ревью e94f895 выявило мутацию без записи при перехваченном overflow: record() теперь атомарно принимает операцию и журнал через Scene.transaction(), откатывая объекты/revision, выделенные IDs, записи и счётчик байтов при любой ошибке. Commit после перехваченного исключения получает согласованный checkpoint; необработанное исключение отклоняет попытку и сохраняет прежние кандидаты/отчёты.

Влияние: Геометрия и её report неизменны. При точном совпадении итоговой сцены успешной попытки continuation-state связывается с полным успешным состоянием без новой оценки. При другом snapshot или ошибке остаётся ранний checkpoint. Восстановление возвращает и журнал, исключая брошенную ветку. Programmer получает source provenance и точный список variables. Роли/исходный интерпретатор/метрики не меняются; изменён формат code/source_code и добавлен checkpoint.json. Replay — инфраструктура, не повторное исполнение LLM-кода или evaluator. Standalone-конфиги будут закреплены на core-фиксе 62162651ce3bdd2d7ed0a9373ef6a392c4642a36, исторический pin 3cbfead остаётся в отчётах прежних запусков.

Проверка: test_checkpoints.py: два дофиксовых контрпримера, uncommitted tail, late variables, commit в цикле, выбор старой ветки с патчем, ошибка после оценки, pure-variable update без лишней оценки, IDs/изменяемые аргументы/math aliases, повреждённый журнал и native Python replay. P2: точный пример 50 move_obj с try/except при 2000 байт и стандартном лимите; overflow при 100 копиях с последующим меньшим переносом; необработанный overflow до/после принятой попытки при сохранении оценённого checkpoint. Лимиты и replay-проверка не ослаблены; эта проверка детерминированна, без live LLM. Полный набор macOS/Linux и прежний одиночный feedback-пилот фиксируются отдельно.

## Зависимости

Исходные requirements.txt (UTF-16):

```text
openai==1.82.0
mistralai==1.7.1
anthropic==0.52.0
google-genai==1.16.1
ptvsd
python-dotenv
transformers==4.30.2
pillow
ifcopenshell
```

Текущие зависимости и extras (причины — LLM, EVALUATOR, PACKAGING выше):

```json
{
  "dependencies": [
    "shapely>=2.1.2,<3",
    "cloudpickle>=3.1,<4"
  ],
  "optional-dependencies": {
    "llm": [
      "openai==1.82.0"
    ],
    "maslov": [
      "numpy>=2.2,<2.3",
      "typeguard>=4.6,<5"
    ],
    "mesh": [
      "numpy>=2.2,<2.3",
      "trimesh>=5,<6",
      "mapbox-earcut>=2,<3",
      "manifold3d>=3.5.2,<4",
      "networkx>=3,<4"
    ],
    "dev": [
      "pytest==9.2.0",
      "ruff==0.17.3",
      "build>=1.2,<2",
      "typeguard>=4.6,<5"
    ]
  }
}
```

## Точные diff фрагментов

### INTERPRETER

Единственная допустимая правка — SyntaxError raises InterpretorError.

```diff
--- tool_agent/python_interpreter.py:None
+++ src/text2bim_massing/_vendor/text2bim/python_interpreter.py:None
@@ -51,8 +51,7 @@
     try:
         expression = ast.parse(code)
     except SyntaxError as e:
-        print(f"Syntax error in generated code: {e}")
-        return None, state
+        raise InterpretorError(f"Syntax error in generated code: {e}") from e
     
     if state is None:
         state = {}
```

### UTIL-safe_encode

Тело без изменений; неиспользуемые функции/импорты исключены.

```diff
# Без изменений
```

### UTIL-remove_last_human_message_with_regex

Тело без изменений; неиспользуемые функции/импорты исключены.

```diff
# Без изменений
```

### UTIL-clean_code_for_chat_extend

Тело без изменений; неиспользуемые функции/импорты исключены.

```diff
# Без изменений
```

### AGENT-chat

AGENTS/EXECUTION: transport и execution injected; остальное сравнивается явно.

```diff
--- tool_agent/agents.py:MyAgent.chat
+++ src/text2bim_massing/_vendor/text2bim/agents.py:MyAgent.chat
@@ -1,87 +1,38 @@
-def chat(self, task, chat_history, *, hint_string=None, return_code=False, remote=False, is_reviewing=False, **kwargs):
-    
-        # BASE_PYTHON_TOOLS = {name: attr for name, attr in vars(builtins).items() if callable(attr)}
-        for name, attr in vars(builtins).items():
-            if callable(attr):
-                BASE_PYTHON_TOOLS[name] = attr
-
-        # update chat history from frontend befor call format_prompt
-        description = "\n".join([f"- {name}: {tool.description}" for name, tool in self.toolbox.items()])
-        # replace method will return original string if no match is found
-        prompt = self.chat_prompt_template.replace("<<all_tools>>", description)
-        if hint_string:
-            # get the textual representation of the floor plan from floor plan designer
-            prompt = prompt.replace("<<floor_plan_text>>", hint_string.strip())
-
-        if chat_history:
-            self.chat_history = prompt.replace("<<chat_history>>", chat_history.strip() + "\n")
-        else:
-            self.chat_history = prompt.replace("<<chat_history>>", "")
-        
-        prompt = self.chat_history
-
-        prompt = prompt.replace("<<task>>", task)
-
-        # prompt = self.format_prompt(task, chat_mode=True)
-        original_result = self.generate_one(prompt, stop=["User:", "Programmer:", "Product Owner:"])
-        # vs.AlrtDialog(f"original answer from llm: {original_result}")
-        explanations, codes = clean_code_for_chat_extend(original_result)
-        # init chat state in current chat session
-        self.chat_state.update(kwargs)
-        
-        if self.response_counter == 0:
-            # extract the role string from the last line of the prompt. e.g. "Programmer:" or "Assistant:"
-            role = prompt.split("\n")[-1]
-            self.log(f"{role}")
-        
-        for explanation, code in zip_longest(explanations, codes):
-            
-            # only show result if documentation_retrieval_tool is used
-            if code is not None and "documentation_retrieval_tool" in code:
-                try:
-                    self.cached_tools = resolve_tools(code, self.toolbox, remote=remote, cached_tools=self.cached_tools)
-                    # the result is the return value of the last tool function invoked in the generated code
-                    result, state = evaluate(code, self.cached_tools, state=self.chat_state, chat_mode=True) # state=kwargs.copy()
-                    # update the chat state
-                    self.chat_state.update(state)
-                    self.log(f"{result}")
-                    
-                except Exception as e:
-                    self.log(f"Error while excuting code: {e}")
+def chat(self, task, chat_history="", *, hint_string=None):
+        self.response_counter = 0
+        while True:
+            prompt = self.chat_prompt_template.replace("<<all_tools>>", self.tool_description)
+            if hint_string:
+                prompt = prompt.replace("<<floor_plan_text>>", hint_string.strip())
+            if chat_history:
+                self.chat_history = prompt.replace("<<chat_history>>", chat_history.strip() + "\n")
             else:
-                # explanation from agent
-                if explanation:
-                    self.log(f"{explanation}")
-                if code is not None:
-                    self.log(f"\n```py\n{code}\n```")
-                    if not return_code:
-                        self.log("\n==Result==\n")
-                        try:
-                            self.cached_tools = resolve_tools(code, self.toolbox, remote=remote, cached_tools=self.cached_tools)
-                            # the result is the return value of the last tool function invoked in the generated code
-                            result, state = evaluate(code, self.cached_tools, state=self.chat_state, chat_mode=True) # state=kwargs.copy()
-                            # update the chat state
-                            self.chat_state.update(state)
-                            self.log(f"Code executed successfully!\n")
-                            # rest the counter
-                            self.response_counter = 0
-                        except Exception as e:
-                            self.response_counter += 1
-                            self.log(f"Error while excuting code: {e}\n")
-                            # recursively call the chat function to solve the error, we only try 3 times
-                            if self.response_counter < 3:
-                                vs.AlrtDialog(f"Try to fix the error: {e}, iteration: {self.response_counter}")
-                                # we delete the elements that are created from the error code
-                                # TODO: this is not a good solution, might be dangerous
-                                if not is_reviewing:
-                                    # delete_all_in_model()
-                                    pass
-                                self.chat_state, original_result = self.chat(f"Could you please fix the error by revising your code: Error while excuting code: {e}. In the script where you made the mistake, the code before the line where the error occurred has already been executed. It may have created or modified some objects, so please avoid repeating the same actions. If you really need to, please delete the objects created before in the script where you made mistake", original_result, **self.chat_state)
-                            else:
-                                self.log(f"I can't fix the error by myself: {e}. Please give me some hints.")
-
-                    else:
-                        tool_code = get_tool_creation_code(code, self.toolbox, remote=remote)
-                        # return f"{tool_code}\n{code}"
-        
-        return self.chat_state, original_result
+                self.chat_history = prompt.replace("<<chat_history>>", "")
+            prompt = self.chat_history
+            prompt = prompt.replace("<<task>>", task)
+            original_result = self.generate_one(prompt, stop=["User:", "Programmer:", "Product Owner:"])
+            explanations, codes = clean_code_for_chat_extend(original_result)
+            for explanation in explanations:
+                self.log("explanation", text=explanation)
+            code = "\n\n".join(codes)
+            self.log("generated_code", code=code, attempt=self.response_counter)
+            if code:
+                result = self.executor.execute(code)
+            else:
+                from ...execution import ExecutionResult
+                result = ExecutionResult(False, "The response contains no executable code block")
+            self.log("execution", success=result.success, error=result.error, stdout=result.stdout)
+            if result.success:
+                self.response_counter = 0
+                return result, original_result
+            self.response_counter += 1
+            if self.response_counter > self.max_repairs:
+                return result, original_result
+            # Source's repair request assumed partial execution. The adapted
+            # transaction restores both scene and variables before this retry.
+            task = (
+                f"Could you please fix the error by revising your code: {result.error}. "
+                "The entire failed script was rolled back, including its variables. "
+                "Previously successful scripts remain. Correct this script in one Python block."
+            )
+            chat_history += "\nProgrammer: " + original_result
```

### AGENT-chat_with_function_call

AGENTS/EXECUTION: transport и execution injected; остальное сравнивается явно.

```diff
--- tool_agent/agents.py:MyAgent.chat_with_function_call
+++ src/text2bim_massing/_vendor/text2bim/agents.py:MyAgent.chat_with_function_call
@@ -1,32 +1,15 @@
-def chat_with_function_call(self, task:str, chat_history:str, stop=["User:","Programmer:","Product Owner:"]):
-        # BASE_PYTHON_TOOLS = {name: attr for name, attr in vars(builtins).items() if callable(attr)}
-        # Get all Python built-in functions
-        for name, attr in vars(builtins).items():
-            if callable(attr):
-                BASE_PYTHON_TOOLS[name] = attr
-
-        description = "\n".join([f"- {name}: {tool.description}" for name, tool in self.toolbox.items()])
-        # replace method will return original string if no match is found
-        prompt = self.chat_prompt_template.replace("<<all_tools>>", description)
-         # update chat history from frontend
+def chat_with_function_call(self, task, chat_history, available_functions, function_description):
+        prompt = self.chat_prompt_template.replace("<<all_tools>>", self.tool_description)
         if chat_history:
             self.chat_history = prompt.replace("<<chat_history>>", chat_history.strip() + "\n")
         else:
             self.chat_history = prompt.replace("<<chat_history>>", "")
-        
         prompt = self.chat_history
         prompt = prompt.replace("<<task>>", task)
-        # check which agent class
-        if isinstance(self, OpenAiAgent):
-            result = self.generate_with_function_call(prompt, stop=stop, available_functions=AVALIABLE_FUNCTIONS, function_description=FUNCTION_DESCRIPTION)
-        if isinstance(self, GeminiAgent):
-            result = self.generate_with_function_call(prompt, stop=stop, available_functions=AVALIABLE_FUNCTIONS, function_declaration=FUNCTION_DECLARATIONS_GEMINI)
-        if isinstance(self, MistralAgent):
-            result = self.generate_with_function_call(prompt, stop=stop, available_functions=AVALIABLE_FUNCTIONS, function_description=FUNCTION_DESCRIPTION)
-        if isinstance(self, ClaudeAgent):  # Add Claude support
-            result = self.generate_with_function_call(prompt, stop=stop, available_functions=AVALIABLE_FUNCTIONS, function_description=FUNCTION_DECLARATIONS_CLAUDE)
-        # extract the role string from the last line of the prompt. e.g. "Programmer:" or "Assistant:"
-        role = prompt.split("\n")[-1]
-        # TODO: lets reduce this for gemini agent, when the output string is too long, it will cause the webplatte to crash
-        self.log(f"{role}{result}")
+        self.llm.role = self.role
+        result = self.llm.generate_with_function_call(
+            prompt, stop=["User:", "Programmer:", "Product Owner:"],
+            available_functions=available_functions, function_description=function_description,
+        )
+        self.log("agent_text", role=self.role, text=result)
         return result
```

### AGENT-chat_check

AGENTS/EXECUTION: transport и execution injected; остальное сравнивается явно.

```diff
--- tool_agent/agents.py:MyAgent.chat_check
+++ src/text2bim_massing/_vendor/text2bim/agents.py:MyAgent.chat_check
@@ -1,14 +1,9 @@
-def chat_check(self, code: str = None, issues: str = None, stop=["User:","Programmer:","Product Owner:", "Reviewer:"]):
-        description = "\n".join([f"- {name}: {tool.description}" for name, tool in self.toolbox.items()])
-        # replace method will return original string if no match is found
-        prompt = self.chat_prompt_template.replace("<<all_tools>>", description)
+def chat_check(self, code=None, issues=None, stop=["User:", "Programmer:", "Product Owner:", "Reviewer:"]):
+        prompt = self.chat_prompt_template.replace("<<all_tools>>", self.tool_description)
         if code:
             prompt = prompt.replace("<<code>>", code)
         if issues:
             prompt = prompt.replace("<<issues>>", issues)
-
         result = self.generate_one(prompt, stop)
-        # extract the role string from the last line of the prompt. e.g. "Programmer:" or "Assistant:"
-        role = prompt.split("\n")[-1]
-        self.log(f"{role}{result}")
+        self.log("agent_text", role=self.role, text=result)
         return result
```

### AGENT-__init__

AGENTS/EXECUTION: transport и execution injected; остальное сравнивается явно.

```diff
--- tool_agent/agents.py:MyAgent.__init__
+++ src/text2bim_massing/_vendor/text2bim/agents.py:MyAgent.__init__
@@ -1,18 +1,9 @@
-def __init__(self, chat_prompt_template=None, run_prompt_template=None, additional_tools=None):
-
-        agent_name = self.__class__.__name__
+def __init__(self, llm, chat_prompt_template, tool_description, *, executor=None, max_repairs=2, role="Programmer", log=None):
+        self.llm = llm
         self.chat_prompt_template = chat_prompt_template
-        self.run_prompt_template = run_prompt_template
-        self._toolbox = {}
-        self.log = print
+        self.tool_description = tool_description
+        self.executor = executor
+        self.max_repairs = max_repairs
+        self.role = role
+        self.log = log or (lambda *args: None)
         self.response_counter = 0
-        self._histroy_response= []
-        if additional_tools is not None:
-            if isinstance(additional_tools, (list, tuple)):
-                additional_tools = {t.name: t for t in additional_tools}
-            elif not isinstance(additional_tools, dict):
-                additional_tools = {additional_tools.name: additional_tools}
-
-            self._toolbox.update(additional_tools)
-
-        self.prepare_for_new_chat()
```

### ARCHITECT-CALL

Один configured backend вместо provider/model dispatch; подстановка task сохранена.

```diff
--- tool_agent/agents.py:plan_designer
+++ src/text2bim_massing/_vendor/text2bim/agents.py:plan_designer
@@ -1,79 +1,10 @@
-def plan_designer(query: str, 
-                  model: str = "claude",  # model can be "gpt" or "gemini" or "mistral" or "claude"
-                  floor_plan_designer_path=ARCHITECT_PROMPT_PATH): 
-
-    with open(floor_plan_designer_path, "r", encoding="utf-8") as f:
-        floor_plan_designer_prompt_str = f.read()
-    prompt = floor_plan_designer_prompt_str.replace("<<task>>", query)
-
-    if "gpt" in model:
-        client = OpenAI(api_key=OPENAI_API_KEY)
-        messages = [{"role": "user","content": str(prompt)}]
-        model_name="o4-mini-2025-04-16" # "gpt-4.1","o4-mini","gpt-4o-2024-05-13","o1-preview" model_name = "o4-mini"  # "gpt-4o", "gpt-4o-2024-05-13" "o1-preview" "gpt-4.1"
-        if "o1" or "o4" in model_name:
-            # o1 api currently doesnt support other args
-            second_response = client.chat.completions.create(
-                model=model_name,
-                messages=messages,
-                reasoning_effort="high",  # "low", "medium", "high"
-            )
-        else:
-            second_response = client.chat.completions.create(
-                model=model_name,
-                messages=messages,
-                temperature=0,
-                stop=["User:"],
-            )
-        
-        return second_response.choices[0].message.content
-
-    if "gemini" in model:
-        # Configure Google GenAI API (new library)
-        api_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
-        if api_key is None:
-            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable.")
-        
-        from google import genai
-        from google.genai.types import GenerateContentConfig, HttpOptions
-        
-        client = genai.Client(
-            vertexai=True, project=VERTEX_PROJECT, location=VERTEX_LOCATION, http_options=HttpOptions(api_version='v1')
-        )
-        
-        second_response = client.models.generate_content(
-            model="gemini-2.5-pro-preview-05-06", # "gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-05-20"
-            contents=prompt,
-            config=GenerateContentConfig(
-                temperature=0.1, 
-                stop_sequences=["User:"],
-                max_output_tokens=65535,  # Set a reasonable limit for output tokens
-            ),
-        )
-       
-        return second_response.text
-    
-    if "mistral" in model:
-        api_key = os.environ.get("MISTRAL_API_KEY", MISTRAL_API_KEY)
-        client = Mistral(api_key=api_key)
-        messages = [{"role": "user", "content": prompt}]
-        
-        chat_response = client.chat.complete(
-            model="mistral-medium-2505",
-            messages=messages,
-            temperature=0,
-        )
-        return chat_response.choices[0].message.content
-
-    if "claude" in model:
-        api_key = os.environ.get("CLAUDE_API_KEY", CLAUDE_API_KEY)
-        client = anthropic.Anthropic(api_key=api_key)
-        response = client.messages.create(
-            model="claude-sonnet-4-20250514", # "claude-4-opus-20250514", "claude-sonnet-4-20250514"
-            max_tokens=4096,
-            temperature=0,
-            messages=[
-                {"role": "user", "content": prompt}
-            ],
-            stop_sequences=["User:"]
-        )
-        return response.content[0].text
+def plan_designer(query, *, llm, prompt_template):
+    # From original plan_designer: insert task into Architect template, then send
+    # one user-message using the already configured client and shared budgets.
+    prompt = prompt_template.replace("<<task>>", query)
+    previous = llm.role
+    llm.role = "Architect"
+    try:
+        return llm.generate_one(prompt, stop=["User:"])
+    finally:
+        llm.role = previous
```

### NATIVE-FUNCTION-CALL

Native response normalized; budget оборачивает каждый запрос, original query/fallback сохранены.

```diff
--- tool_agent/agents.py:OpenAiAgent.generate_with_function_call
+++ src/text2bim_massing/runtime.py:BudgetedLLM.generate_with_function_call
@@ -1,55 +1,35 @@
-def generate_with_function_call(self, prompt:str, stop:str, available_functions:dict[str, Callable], function_description:list[dict]):
-        messages=[{"role": "user", "content": prompt}]
-        
-        response = self.client.chat.completions.create(
-            model=self.model,
-            messages=messages,
-            # temperature=0,
-            tools=function_description,
-            tool_choice = "auto",
-            # tool_choice = "required",
-            # reasoning_effort="high",  # "low", "medium", "high"
-            # stop=stop,
+def generate_with_function_call(self, prompt, stop, available_functions, function_description):
+        # From Text2BIM OpenAiAgent.generate_with_function_call: tool request,
+        # execute supplied functions, append tool outputs, then request final text.
+        messages = [{"role": "user", "content": prompt}]
+        response = self.complete(messages, tools=function_description, stop=stop)
+        if not response.tool_calls:
+            return response.text
+        messages.append(
+            {
+                "role": "assistant",
+                "content": response.text or None,
+                "tool_calls": [
+                    {
+                        "id": call.id,
+                        "type": "function",
+                        "function": {
+                            "name": call.name,
+                            "arguments": call.arguments,
+                        },
+                    }
+                    for call in response.tool_calls
+                ],
+            }
         )
-        response_message = response.choices[0].message
-        if hasattr(response_message, "tool_calls"):
-            tool_calls = response_message.tool_calls
-        else:
-            return response_message.content
-        # Step 2: check if the model wanted to call a function
-        if tool_calls:
-            # Step 3: call the function
-            # Note: the JSON response may not always be valid; be sure to handle errors
-            messages.append(response_message)  # extend conversation with assistant's reply
-            # Step 4: send the info for each function call and function response to the model
-            for tool_call in tool_calls:
-                function_name = tool_call.function.name
-                if function_name not in available_functions:
-                    # if the function is not available, most likely the model is trying to call a function that is belong to the programmer's toolset
-                    # in this case, we can just disable the function call and give the model second chance to generate the response
-                    return self.generate_one(prompt, stop)
-                    
-                function_to_call = available_functions[function_name]
-                function_args = json.loads(tool_call.function.arguments)
-                function_response = function_to_call(
-                    function_args.get("query"),
-                )
-                messages.append(
-                    {
-                        "tool_call_id": tool_call.id,
-                        "role": "tool",
-                        "content": str(function_response),
-                    }
-                )  # extend conversation with function response
-            second_response = self.client.chat.completions.create(
-                model=self.model,
-                messages=messages,
-                reasoning_effort="high",  # "low", "medium", "high"
-                # temperature=0,
-                # stop=stop,
-            )
-            # also send the function call response to the frontend, currently hard coded the role as "Architect:"
-            self.log(f"Architect: {function_response}")
-            return second_response.choices[0].message.content
-        else:
-            return response_message.content
+        for call in response.tool_calls:
+            if call.name not in available_functions:
+                return self.generate_one(prompt, stop)
+            function_to_call = available_functions[call.name]
+            function_args = json.loads(call.arguments)
+            result = function_to_call(function_args.get("query"))
+            messages.append({"tool_call_id": call.id, "role": "tool", "content": str(result)})
+        final = self.complete(messages, stop=stop)
+        if final.tool_calls:
+            raise LLMFailed("Unexpected recursive function call")
+        return final.text
```

### LLM-generate_many

LLM: извлечён transport; форма API запроса та же, параметры задаются явно.

```diff
--- tool_agent/agents.py:OpenAiAgent.generate_many
+++ src/text2bim_massing/llm.py:OpenAIClient.generate_many
@@ -1,2 +1,2 @@
-def generate_many(self, prompts, stop):
+def generate_many(self, prompts, stop=None):
         return [self._chat_generate(prompt, stop) for prompt in prompts]
```

### LLM-generate_one

LLM: извлечён transport; форма API запроса та же, параметры задаются явно.

```diff
--- tool_agent/agents.py:OpenAiAgent.generate_one
+++ src/text2bim_massing/llm.py:OpenAIClient.generate_one
@@ -1,2 +1,2 @@
-def generate_one(self, prompt, stop):
+def generate_one(self, prompt, stop=None):
         return self._chat_generate(prompt, stop)
```

### LLM-_chat_generate

LLM: извлечён transport; форма API запроса та же, параметры задаются явно.

```diff
--- tool_agent/agents.py:OpenAiAgent._chat_generate
+++ src/text2bim_massing/llm.py:OpenAIClient._chat_generate
@@ -1,16 +1,5 @@
 def _chat_generate(self, prompt, stop):
-        if "o1" or "o4" in self.model:
-            # o1 api currently doesnt support other args
-            result = self.client.chat.completions.create(
-                model=self.model,
-                messages=[{"role": "user", "content": prompt}],
-                reasoning_effort="high",  # "low", "medium", "high"
-            )
-        else:
-            result = self.client.chat.completions.create(
-                model=self.model,
-                messages=[{"role": "user", "content": prompt}],
-                temperature=0,
-                stop=stop,
-            )
-        return result.choices[0].message.content
+        response = self.complete([{"role": "user", "content": prompt}], stop=stop)
+        if response.tool_calls:
+            raise ValueError("Unexpected tool call in a text-only completion")
+        return response.text
```

### INITIAL-WORKFLOW

Внешний жизненный цикл/архив добавлен вокруг ролей; raw task bypass удалён.

```diff
--- tool_agent/multi_agents_workflow.py:run_po_coder_agents
+++ src/text2bim_massing/workflow.py:generate
@@ -1,92 +1,228 @@
-def run_po_coder_agents(query: str, 
-                        chat_history_front_end: str, 
-                        model=MODEL): # model = "gpt" or "gemini" or "mistral" or "claude"
-    # init tools
-    tool_list = init_vw_tools()
+def generate(task, evaluator, llm, config=None, output_dir="runs/text2bim") -> GenerationResult:
+    """Generate, evaluate and improve massing; retain partial results on budget exhaustion.
 
-    with open(PRODUCT_OWNER_PROMPT_PATH, "r", encoding="utf-8") as f:
-        po_prompt_str = f.read()
+    task is a string, GenerationTask, or {instruction, context}. evaluator obeys
+    evaluator(massing, context) -> JSON report. llm implements complete(messages,
+    tools=None, stop=None, timeout=None), as both supplied transports do.
+    """
+    config = RunConfig(**config) if isinstance(config, dict) else config or RunConfig()
+    if isinstance(task, str):
+        task = GenerationTask(task)
+    elif isinstance(task, dict):
+        task = GenerationTask(**task)
+    if not isinstance(task, GenerationTask):
+        raise TypeError("task must be an instruction, GenerationTask or task dictionary")
+    if not callable(evaluator):
+        raise TypeError("evaluator must be callable")
+    root = Path(output_dir).resolve()
+    root.mkdir(parents=True, exist_ok=True)
+    if any(root.iterdir()):
+        raise FileExistsError(f"Output directory must be empty: {root}")
+    context = deepcopy(task.context)
+    write_json(root / "task.json", {"instruction": task.instruction, "context": context})
+    write_json(root / "config.json", asdict(config))
+    write_json(
+        root / "provenance.json",
+        {
+            "text2bim_commit": "b71b83d0d6640e7dfe7af3fda17b40fb3cfd70dc",
+            "geometry_source_commit": "607ff1fcf80477787409522d93e18e42ac1436cf",
+            "llm_transport": type(llm).__module__ + "." + type(llm).__qualname__,
+            "model": getattr(llm, "model", None),
+            "evaluator_type": type(evaluator).__module__ + "." + type(evaluator).__qualname__,
+        },
+    )
+    prompts = load_prompts(config.tool_units)
+    write_json(root / "prompts.json", prompts)
+    trace = Trace(root)
+    budget = Budget(config)
+    backend = BudgetedLLM(llm, budget, trace)
+    archive = CandidateArchive(root, evaluator, context, budget, trace)
+    executor = ProcessExecutor(config, remaining=budget.remaining)
+    executor.on_success = lambda: archive.complete_execution(executor)
 
-    with open(CODER_PROMPT_PATH, "r", encoding="utf-8") as f:
-        coder_prompt_str = f.read()
+    def handle_event(message, code):
+        budget.check()
+        event = message["event"]
+        if event == "commit":
+            return archive.commit(
+                SceneSnapshot(message["snapshot"]),
+                "\n\n".join([*executor.codes, code]),
+                message["state"],
+                actions=[*executor.actions, *message["actions"]],
+                attempt=executor.attempts,
+            )
+        if event == "evaluate":
+            return archive.evaluate(message["candidate_id"])
+        if event == "select":
+            return archive.select(message["candidate_id"])
+        raise ValueError(f"Unknown worker event: {event}")
 
-    if model == "gpt":
-        agent_po = OpenAiAgent(
-            model="o4-mini-2025-04-16", # "gpt-4.1","o4-mini","gpt-4o-2024-05-13","o1-preview",o4-mini-2025-04-16
-            chat_prompt_template=po_prompt_str,
-            additional_tools=tool_list
+    executor.event_handler = handle_event
+    documentation = MassingTools(Scene(), units=config.tool_units).documentation() + (
+        "\ncommit_candidate(): commit the current immutable scene snapshot; return candidate ID."
+        "\nevaluate(candidate_id): evaluate this archived snapshot or read its cached JSON report."
+        "\nselect_candidate(candidate_id): select an already evaluated archive entry without evaluation."
+        "\nBuiltins: print, len, str, int, float, bool, list, dict, tuple, set, range, enumerate, zip, "
+        "sum, min, max, abs, round, sorted, reversed, all, any. Imports: public math only."
+    )
+    enhancer = MyAgent(backend, prompts["Enhancer"], documentation, role="Enhancer", log=trace.add)
+    programmer = MyAgent(
+        backend,
+        prompts["Programmer"],
+        documentation,
+        executor=executor,
+        max_repairs=config.max_repairs,
+        role="Programmer",
+        log=trace.add,
+    )
+    reviewer = MyAgent(backend, prompts["Reviewer"], documentation, role="Reviewer", log=trace.add)
+    status, reason = "budget_exhausted", "iterations"
+    iteration = 0
+    try:
+        if config.max_iterations == 0:
+            raise BudgetExceeded("iterations")
+        query = (
+            task.instruction
+            + "\nExternal task context:\n"
+            + json.dumps(context, ensure_ascii=False)
         )
-
-        agent_coder = OpenAiAgent(
-            model="o4-mini-2025-04-16", # "gpt-4.1","o4-mini","gpt-4o-2024-05-13","o1-preview"
-            chat_prompt_template=coder_prompt_str,
-            additional_tools=tool_list
+        answer = enhancer.chat_with_function_call(
+            query,
+            "",
+            available_functions={
+                "plan_designer": lambda query: plan_designer(
+                    query, llm=backend, prompt_template=prompts["Architect"]
+                )
+            },
+            function_description=PLAN_FUNCTION,
         )
-    
-    elif model == "gemini":
-        agent_po = GeminiAgent(
-            model="gemini-2.5-pro-preview-05-06", # "gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-05-20"
-            chat_prompt_template=po_prompt_str,
-            additional_tools=tool_list
-        )
-        agent_coder = GeminiAgent(
-            model="gemini-2.5-pro-preview-05-06", # "gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-05-20"
-            chat_prompt_template=coder_prompt_str,
-            additional_tools=tool_list
-        )
-    
-    elif model == "mistral":
-        agent_po = MistralAgent(
-            model = "mistral-medium-2505",
-            chat_prompt_template=po_prompt_str,
-            additional_tools=tool_list
-        )
-        agent_coder = MistralAgent(
-            model = "mistral-medium-2505",
-            chat_prompt_template=coder_prompt_str,
-            additional_tools=tool_list
-        )
-    
-    elif model == "claude":
-        agent_po = ClaudeAgent(
-            model="claude-sonnet-4-20250514", # "claude-4-opus-20250514", "claude-sonnet-4-20250514"
-            chat_prompt_template=po_prompt_str,
-            additional_tools=tool_list
-        )
-        agent_coder = ClaudeAgent(
-            model="claude-sonnet-4-20250514", # "claude-4-opus-20250514", "claude-sonnet-4-20250514"
-            chat_prompt_template=coder_prompt_str,
-            additional_tools=tool_list
-        )
-
-    agent_coder.set_stream(streamer)
-    agent_po.set_stream(streamer)
-
-    # create a state dictionary file if not exist
-    state_path = STATE_PATH
-    if not os.path.exists(state_path):
-        with open(state_path, "w") as f:
-            json.dump({}, f)
-
-    # load the previous state from file
-    try:
-        with open(state_path, "r") as f:
-            previous_state = json.load(f)
-    except json.JSONDecodeError:
-        previous_state = {} 
-            
-    chat_history = remove_last_human_message_with_regex(chat_history_front_end)
-
-    answer = agent_po.chat_with_function_call(query, chat_history) # consider the function call to connect with architect agent
-    state, code_result = agent_coder.chat(answer, chat_history, **previous_state) # chat will evaluate the code
-
-    # update the state dictionary
-    if isinstance(state, dict):
-        previous_state.update(state)
-
-    # save the state to file
-    with open(state_path, "w") as f:
-        json.dump(previous_state, f, default=safe_encode)
-
-    output_sum = get_output_sum()
-    return output_sum, code_result
+        # From run_po_coder_agents: PO answer is passed to Programmer, whose chat executes code.
+        programmer_task = answer
+        while iteration < config.max_iterations:
+            budget.check()
+            iteration += 1
+            trace.add("iteration", number=iteration)
+            execution, code_result = programmer.chat(programmer_task, "")
+            if not execution.success:
+                budget.check()
+                status, reason = "execution_failed", execution.error
+                break
+            current = next(
+                (
+                    candidate
+                    for candidate in reversed(list(archive.candidates.values()))
+                    if candidate.snapshot.json == executor.snapshot.json
+                    and candidate.state_json == json.dumps(executor.state, allow_nan=False)
+                ),
+                None,
+            )
+            if current is None:
+                candidate_id = archive.commit(
+                    executor.snapshot,
+                    "\n\n".join(executor.codes),
+                    executor.state,
+                    actions=executor.actions,
+                    attempt=executor.attempts,
+                    boundary="script_complete",
+                )
+            else:
+                candidate_id = current.candidate_id
+            # A missing explicit evaluation cannot turn an unassessed mutable form into success.
+            archive.evaluate(candidate_id)
+            issues = {
+                "task": task.instruction,
+                "context": context,
+                "scene": executor.snapshot.to_dict(),
+                "candidates": [candidate.to_dict() for candidate in archive.candidates.values()],
+            }
+            decision = None
+            for attempt in range(config.max_repairs + 1):
+                review_result = reviewer.chat_check(code=code_result, issues=json.dumps(issues))
+                try:
+                    decision = _review_decision(review_result)
+                    archive.select(decision["candidate_id"])
+                    break
+                except (ValueError, KeyError) as error:
+                    trace.add("review_error", error=str(error), attempt=attempt)
+                    issues["decision_error"] = str(error)
+                    decision = None
+            if decision is None:
+                status, reason = "review_failed", "No valid evaluated-candidate decision"
+                break
+            if decision["action"] == "finish":
+                status, reason = "completed", None
+                break
+            chosen = archive.candidates[decision["candidate_id"]]
+            executor.snapshot = chosen.snapshot
+            executor.state = json.loads(chosen.state_json)
+            executor.codes = [chosen.source_code]
+            executor.actions = json.loads(chosen.actions_json)
+            # Source's review patch request is retained, with the selected immutable state made explicit.
+            programmer_task = (
+                review_patch_task(chosen.source_code, decision["guidance"])
+                + "\nSelected scene with stable IDs: "
+                + chosen.snapshot.json
+                + "\nRestored checkpoint variables: "
+                + json.dumps(list(decode_state(executor.state)))
+                + "\nOnly the listed variables belong to this checkpoint. source_code is provenance "
+                "and may include statements after the checkpoint; do not assume those ran."
+            )
+    except BudgetExceeded as error:
+        status, reason = "budget_exhausted", str(error)
+    except EvaluationFailed as error:
+        status, reason = "evaluation_failed", str(error)
+    except LLMFailed as error:
+        status, reason = "llm_failed", str(error)
+    except Exception as error:
+        status, reason = "failed", f"{type(error).__name__}: {error}"
+        trace.add("run_error", error=reason)
+    selected = archive.candidates.get(archive.selected_id)
+    responses = backend.responses
+    usage_known = all(
+        response.prompt_tokens is not None and response.completion_tokens is not None
+        for response in responses
+    )
+    input_tokens = sum(response.prompt_tokens or 0 for response in responses)
+    output_tokens = sum(response.completion_tokens or 0 for response in responses)
+    money = None
+    if (
+        usage_known
+        and len(responses) == budget.llm_calls
+        and config.input_price_per_million is not None
+        and config.output_price_per_million is not None
+    ):
+        money = (
+            input_tokens * config.input_price_per_million
+            + output_tokens * config.output_price_per_million
+        ) / 1_000_000
+    costs = {
+        "llm_calls": budget.llm_calls,
+        "evaluations": budget.evaluations,
+        "execution_attempts": executor.attempts,
+        "iterations": iteration,
+        "elapsed_seconds": time.monotonic() - budget.started,
+        "prompt_tokens": input_tokens,
+        "completion_tokens": output_tokens,
+        "usage_complete": usage_known and len(responses) == budget.llm_calls,
+        "monetary_cost": money,
+    }
+    trace.add(
+        "run_finished", status=status, reason=reason, selected_candidate_id=archive.selected_id
+    )
+    result = GenerationResult(
+        status,
+        reason,
+        selected.to_dict() if selected else None,
+        tuple(candidate.to_dict() for candidate in archive.candidates.values()),
+        tuple(trace.events),
+        costs,
+        str(root),
+    )
+    write_json(root / "scene.json", executor.snapshot.to_dict())
+    write_json(root / "result.json", result.to_dict())
+    if selected:
+        write_json(root / "selected_massing.json", selected.snapshot.to_massing())
+        (root / "selected_code.py").write_text(selected.code)
+        (root / "selected_source_code.py").write_text(selected.source_code)
+        write_json(root / "checkpoint.json", selected.checkpoint())
+    return result
```

### PATCH-REQUEST

Выражение исходного запроса patch сохранено без изменений.

```diff
--- tool_agent/multi_agents_workflow.py:run_agent_checking_loop
+++ src/text2bim_massing/workflow.py:review_patch_task
@@ -1 +1,8 @@
-input_review_result = "The Python code that generates the building with some issues: \n" + f"{code_result}" + "Please write a patch to solve the issues based on the review suggestions. Do not write diff but a excutable python script in a code block. You can reuse the variables defined in the original code, but DO NOT rewrite the original code." + "\n" + "Review suggestions: " + review_result
+input_review_result = (
+        "The Python code that generates the building with some issues: \n"
+        + f"{code_result}"
+        + "Please write a patch to solve the issues based on the review suggestions. Do not write diff but a excutable python script in a code block. You can reuse the variables defined in the original code, but DO NOT rewrite the original code."
+        + "\n"
+        + "Review suggestions: "
+        + review_result
+    )
```

### MASLOV-polygons_to_shapely_converter.py

Исходный метод без изменений; лишние импорты/база Function удалены.

```diff
# Без изменений
```

### MASLOV-shapely_to_polygons_converter.py

Исходный метод без изменений; лишние импорты/база Function удалены.

```diff
# Без изменений
```

### ORIGINAL-PROMPT-po_chat_prompt_temp.txt

Оригинальные prompt resources сохранены побайтово. Runtime diff отдельно ниже.

```diff
# Без изменений
```

### ORIGINAL-PROMPT-coder_chat_prompt_temp.txt

Оригинальные prompt resources сохранены побайтово. Runtime diff отдельно ниже.

```diff
# Без изменений
```

### ORIGINAL-PROMPT-checker_chat_prompt_temp.txt

Оригинальные prompt resources сохранены побайтово. Runtime diff отдельно ниже.

```diff
# Без изменений
```

### ORIGINAL-PROMPT-floor_plan_designer_chat_prompt_few_shots.txt

Оригинальные prompt resources сохранены побайтово. Runtime diff отдельно ниже.

```diff
# Без изменений
```

### LLM-__init__

Инициализация и SDK dispatch выделены в client; параметры, timeout, usage и transport явные, исходный SDK 1.82.0 сохранён.

```diff
--- tool_agent/agents.py:OpenAiAgent.__init__
+++ src/text2bim_massing/llm.py:OpenAIClient.__init__
@@ -1,27 +1,21 @@
-def __init__(
-        self,
-        model="gpt-4o",
-        api_key=None,
-        chat_prompt_template=None,
-        run_prompt_template=None,
-        additional_tools=None,
-    ):
-        if not is_openai_available():
-            raise ImportError("Using `OpenAiAgent` requires `openai`: `pip install openai`.")
-
-        if api_key is None:
-            api_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
-        if api_key is None:
-            raise ValueError(
-                "You need an openai key to use `OpenAIAgent`. You can get one here: Get one here "
-                "https://openai.com/api/`. If you have one, set it in your env with `os.environ['OPENAI_API_KEY'] = "
-                "xxx."
+def __init__(self, config: LLMConfig, *, api_key: str | None = None, client=None):
+        self.config, self.model = config, config.model
+        self.calls = 0
+        self.last_response: LLMResponse | None = None
+        self.responses: list[LLMResponse] = []
+        self._owns_client = client is None
+        if client is None:
+            try:
+                from openai import OpenAI
+            except ImportError as error:
+                raise ImportError("Install text2bim-massing[llm] to use the LLM client") from error
+            api_key = api_key or os.environ.get(config.api_key_env)
+            if not api_key:
+                raise ValueError(f"Set {config.api_key_env} or pass api_key explicitly")
+            client = OpenAI(
+                api_key=api_key,
+                base_url=config.base_url,
+                timeout=config.timeout,
+                max_retries=config.max_retries,
             )
-
-        self.client = OpenAI(api_key=api_key)
-        self.model = model
-        super().__init__(
-            chat_prompt_template=chat_prompt_template,
-            run_prompt_template=run_prompt_template,
-            additional_tools=additional_tools,
-        )
+        self.client = client
```

### LLM-complete

Инициализация и SDK dispatch выделены в client; параметры, timeout, usage и transport явные, исходный SDK 1.82.0 сохранён.

```diff
--- tool_agent/agents.py:OpenAiAgent._chat_generate
+++ src/text2bim_massing/llm.py:OpenAIClient.complete
@@ -1,16 +1,42 @@
-def _chat_generate(self, prompt, stop):
-        if "o1" or "o4" in self.model:
-            # o1 api currently doesnt support other args
-            result = self.client.chat.completions.create(
-                model=self.model,
-                messages=[{"role": "user", "content": prompt}],
-                reasoning_effort="high",  # "low", "medium", "high"
-            )
-        else:
-            result = self.client.chat.completions.create(
-                model=self.model,
-                messages=[{"role": "user", "content": prompt}],
-                temperature=0,
-                stop=stop,
-            )
-        return result.choices[0].message.content
+def complete(self, messages, *, tools=None, stop=None, timeout=None) -> LLMResponse:
+        options = {}
+        for key in ("temperature", "reasoning_effort", "max_completion_tokens"):
+            value = getattr(self.config, key)
+            if value is not None:
+                options[key] = value
+        if self.config.send_stop and stop:
+            options["stop"] = stop
+        if tools:
+            options.update(tools=tools, tool_choice="auto")
+        self.calls += 1
+        self.last_response = None
+        client = self.client
+        if timeout is not None:
+            # A workflow budget must count every HTTP attempt, including failures.
+            client = client.with_options(timeout=min(timeout, self.config.timeout), max_retries=0)
+        result = client.chat.completions.create(
+            model=self.model,
+            messages=messages,
+            **options,
+        )
+        if not result.choices:
+            raise ValueError("The model did not return a text completion")
+        message = result.choices[0].message
+        tool_calls = tuple(
+            ToolCall(call.id, call.function.name, call.function.arguments)
+            for call in message.tool_calls or ()
+        )
+        if not isinstance(message.content, str) and not tool_calls:
+            raise ValueError("The model did not return a text completion")
+        usage = result.usage
+        response = LLMResponse(
+            text=message.content or "",
+            model=result.model,
+            prompt_tokens=usage.prompt_tokens if usage else None,
+            completion_tokens=usage.completion_tokens if usage else None,
+            total_tokens=usage.total_tokens if usage else None,
+            tool_calls=tool_calls,
+        )
+        self.last_response = response
+        self.responses.append(response)
+        return response
```

### TOOL-move_obj

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:Move.__call__
+++ src/text2bim_massing/tools.py:MassingTools.move_obj
@@ -1,38 +1,5 @@
-def __call__(self, uuid: List[str], xDistance, yDistance, zDistance):
-        try:
-            if isinstance(uuid, str):
-                h  = vs.GetObjectByUuid(uuid)
-                if h != vs.Handle(0):
-                    # think about the special case of moving roof, we will get the roof slab uuid(equal to the roof uuid) but we have to move the whole roof
-                    if vs.GetClass(h) == "Roof_Slabs" or vs.GetClass(h) == "Roofs":
-                        # get the roof slab
-                        ok, roof_slab_uuid, iType = vs.IFC_GetEntityProp(h, 'Tag')
-                        roof_slab_h = vs.GetObjectByUuid(roof_slab_uuid)
-                        # move together
-                        vs.Move3DObj(h, xDistance, yDistance, zDistance)
-                        vs.Move3DObj(roof_slab_h, xDistance, yDistance, zDistance)
-                    else:
-                        vs.Move3DObj(h, xDistance, yDistance, zDistance)
-                else:
-                    raise Exception("Can't move the element: either it does not exist or unvalid uuid!")
-                # vs.AlrtDialog(f"element {uuid} moved!")
-            elif isinstance(uuid, List):
-                for id in uuid:
-                    h  = vs.GetObjectByUuid(id)
-                    if h != vs.Handle(0):
-                    # think about the special case of moving roof, we will get the roof slab uuid(equal to the roof uuid) but we have to move the whole roof
-                        if vs.GetClass(h) == "Roof_Slabs" or vs.GetClass(h) == "Roofs":
-                            # get the roof slab
-                            ok, roof_slab_uuid, iType = vs.IFC_GetEntityProp(h, 'Tag')
-                            roof_slab_h = vs.GetObjectByUuid(roof_slab_uuid)
-                            # move together
-                            vs.Move3DObj(h, xDistance, yDistance, zDistance)
-                            vs.Move3DObj(roof_slab_h, xDistance, yDistance, zDistance)
-                        else:
-                            vs.Move3DObj(h, xDistance, yDistance, zDistance)
-                    else:
-                        raise Exception("Can't move the element: either it does not exist or unvalid uuid!")
-            else:
-                raise Exception("uuid type not supported!")
-        except Exception as e:
-            raise ValueError(f"Error occured during moving element: {e}")
+def move_obj(self, uuid, xDistance=0, yDistance=0, zDistance=0):
+        """Move an ID or list of IDs; 2D profiles only support x/y movement. Return None."""
+        self.scene.move(
+            uuid, self._length(xDistance), self._length(yDistance), self._length(zDistance)
+        )
```

### TOOL-delete_element

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:DeleteTool.__call__
+++ src/text2bim_massing/tools.py:MassingTools.delete_element
@@ -1,29 +1,3 @@
-def __call__(self, uuid: Union[str, List[str]]):
-        try:
-            if isinstance(uuid, str):
-                h = vs.GetObjectByUuid(uuid)
-                if vs.GetClass(h) == "Roofs" or vs.GetClass(h) == "Roof_Slabs":
-                    # get the roof slab
-                    ok, roof_slab_uuid, iType = vs.IFC_GetEntityProp(h, 'Tag')
-                    roof_slab_h = vs.GetObjectByUuid(roof_slab_uuid)
-                    vs.DelObject(roof_slab_h)
-                    vs.DelObject(h)
-                else: 
-                    vs.DelObject(h)
-                vs.AlrtDialog(f"element {uuid} deleted!")
-            elif isinstance(uuid, List):
-                for id in uuid:
-                    h = vs.GetObjectByUuid(id)
-                    if vs.GetClass(h) == "Roofs" or vs.GetClass(h) == "Roof_Slabs":
-                        # get the roof slab
-                        ok, roof_slab_uuid, iType = vs.IFC_GetEntityProp(h, 'Tag')
-                        roof_slab_h = vs.GetObjectByUuid(roof_slab_uuid)
-                        vs.DelObject(roof_slab_h)
-                        vs.DelObject(h)
-                    else: 
-                        vs.DelObject(h)
-                vs.AlrtDialog(f"elements deleted!")
-            else:
-                vs.AlrtDialog("handle type not supported")
-        except Exception as e:
-            raise ValueError(f"Error occured during deleting element: {e}")
+def delete_element(self, uuid):
+        """Delete an ID or list of IDs atomically."""
+        return self.scene.delete(uuid)
```

### TOOL-create_polygon

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:CreatePolygon.__call__
+++ src/text2bim_massing/tools.py:MassingTools.create_polygon
@@ -1,23 +1,3 @@
-def __call__(self, vertices: List[str], layer_uuid: str):
-        try:
-            # set active layer
-            layer_name = vs.GetLName(vs.GetObjectByUuid(layer_uuid))
-            vs.Layer(layer_name)
-
-            vs.ClosePoly()
-            if all(isinstance(vertex, list) for vertex in vertices):
-                vertices = [tuple(vertex) for vertex in vertices]
-            unique_set=set(vertices)
-            if isinstance(vertices, List):
-                # we need to have at least two different input items in order to produce correct polygon
-                if len(unique_set) > 1:
-                    vs.Poly(*vertices)
-                    hpoly = vs.LNewObj()
-                    uuid = vs.GetObjectUuid(hpoly)
-                    return uuid
-                else:
-                    raise Exception("Please provide at least two different vertices!")
-            else:
-                raise Exception("Please provide a list of vertices!")
-        except Exception as e:
-            raise ValueError(f"Error occured during creating polygon: {e}")
+def create_polygon(self, vertices):
+        """Create a single-ring 2D profile from [(x, y), ...]; return its stable ID."""
+        return self.scene.create_polygon(self._polygons([vertices]))
```

### TOOL-get_polygon_vertex

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:GetPolygonVertex.__call__
+++ src/text2bim_massing/tools.py:MassingTools.get_polygon_vertex
@@ -1,10 +1,5 @@
-def __call__(self, uuid: str, at: int):
-        try:
-            if isinstance(uuid, str):
-                h  = vs.GetObjectByUuid(uuid)
-                # In Verctorworks, the index of the first vertex start with 1
-                valid_at = at+1
-                temp = vs.GetPolylineVertex(h, valid_at)
-                return temp[0]
-        except Exception as e:
-            raise ValueError(f"Error occured during getting polygon vertex: {e}")
+def get_polygon_vertex(self, uuid, at, ring=0):
+        """Read a vertex (zero-based at and ring indexes), in the tool's units."""
+        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (at, ring)):
+            raise ValueError("Vertex and ring indexes must be nonnegative integers")
+        return tuple(self.get_object(uuid)["polygons"][ring][at])
```

### TOOL-get_vertex_count

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:GetVertNum.__call__
+++ src/text2bim_massing/tools.py:MassingTools.get_vertex_count
@@ -1,8 +1,5 @@
-def __call__(self, uuid: str):
-        try:
-            if isinstance(uuid, str):
-                h  = vs.GetObjectByUuid(uuid)
-                num = vs.GetVertNum(h)
-                return num
-        except Exception as e:
-            raise ValueError(f"Error occured during getting vertex count: {e}")
+def get_vertex_count(self, uuid, ring=0):
+        """Read the vertex count of a zero-based ring."""
+        if isinstance(ring, bool) or not isinstance(ring, int) or ring < 0:
+            raise ValueError("Ring index must be a nonnegative integer")
+        return len(self.get_object(uuid)["polygons"][ring])
```

### TOOL-duplicate_obj

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:DuplicateObj.__call__
+++ src/text2bim_massing/tools.py:MassingTools.duplicate_obj
@@ -1,71 +1,3 @@
-def __call__(self, element_uuid: Union[str, List[str]], layer_uuid: str, n: int):
-        try:
-            objs_uuid = []
-            if isinstance(element_uuid, str):
-                obj = vs.GetObjectByUuid(element_uuid)
-                if obj != vs.Handle(0):
-                    for i in range(n):
-                        # BUG: when triger the copy command fpr a wall via webpalette, the windows and doors within the walls will disappear. However, when run the script in the built-in script editor, it works fine. 
-                        # if vs.GetTypeN(obj) == 31:
-                        if vs.GetClass(obj) == "xxx": # (never used), this method will not work for wall with doors and windows
-                            # set active layer
-                            layer_h = vs.GetLayer(obj)
-                            layer_name = vs.GetLName(layer_h)
-                            # set active layer
-                            vs.Layer(layer_name)
-                            vs.DSelectAll()
-                            vs.SetSelect(obj)
-                            vs.DoMenuTextByName('Copy', 0)
-                            # switch to the target layer
-                            vs.Layer(vs.GetLName(vs.GetObjectByUuid(layer_uuid)))
-                            vs.DoMenuTextByName('Paste In Place', 0) 
-                            vs.ForEachObjectInLayer(vs.ResetObject, 0, 2, 0)
-                            hobj = vs.FSObject(vs.GetObjectByUuid(layer_uuid))
-                            obj_uuid = vs.GetObjectUuid(hobj)
-                            objs_uuid.append(obj_uuid)
-                            vs.ForEachObjectInLayer(set_ifc_property_for_duplication, 2, 1, 0)
-                            vs.DSelectAll()
-                        else:
-                            if vs.GetClass(obj) == "Slabs":
-                                hobj = vs.CreateDuplicateObjN(obj, vs.GetObjectByUuid(layer_uuid), False)
-                            else:
-                                # because of the BUG mentioned above, we need to do it this way
-                                hobj = vs.CreateDuplicateObjN(obj, vs.GetObjectByUuid(layer_uuid), True)
-                                vs.ResetObject(hobj)
-                            obj_uuid = vs.GetObjectUuid(hobj)
-                            objs_uuid.append(obj_uuid)
-                            # add uuid to ifc
-                            set_ifc_property_for_duplication(hobj)
-
-            if isinstance(element_uuid, List):
-                for id in element_uuid:
-                    obj = vs.GetObjectByUuid(id)
-                    if obj != vs.Handle(0):
-                        for i in range(n):
-                            if vs.GetTypeN(obj) == 31:
-                                # set active layer
-                                layer_name = vs.GetLName(obj)
-                                vs.Layer(layer_name)
-                                vs.DSelectAll()
-                                vs.SelectAll()
-                                vs.DoMenuTextByName('Copy', 0)
-                                # switch to the target layer
-                                vs.Layer(vs.GetLName(vs.GetObjectByUuid(layer_uuid)))
-                                vs.DoMenuTextByName('Paste In Place', 0)
-                                vs.ForEachObjectInLayer(set_ifc_property_for_duplication, 2, 1, 0)
-                            else:
-                                if vs.GetClass(obj) == "Slabs":
-                                    hobj = vs.CreateDuplicateObjN(obj, vs.GetObjectByUuid(layer_uuid), False)
-                                else:
-                                    hobj = vs.CreateDuplicateObjN(obj, vs.GetObjectByUuid(layer_uuid), True)     
-                                obj_uuid = vs.GetObjectUuid(hobj)
-                                objs_uuid.append(obj_uuid)
-                                # add uuid to ifc
-                                set_ifc_property_for_duplication(hobj)                    
-                # elevation, thickness = vs.GetLayerElevation(vs.GetObjectByUuid(layer_uuid))
-                # vs.SetLayerElevation(vs.GetObjectByUuid(layer_uuid), 0, 0)
-                # vs.SetLayerElevation(vs.GetObjectByUuid(layer_uuid), elevation, 0)
-
-            return objs_uuid
-        except Exception as e:
-            raise ValueError(f"Error occured during duplicating element: {e}")
+def duplicate_obj(self, element_uuid, n=1):
+        """Copy an ID or list of IDs n times; return new IDs. Originals retain their IDs."""
+        return self.scene.duplicate(element_uuid, n)
```

### TOOL-rotate_obj

Vectorworks и layer заменены Scene: исходное имя и основной контракт сохранены; единицы, ограничения геометрии, defaults и batch-расширения перечислены в TOOLS/GEOMETRY.

```diff
--- tool_agent/vw_tools_extend.py:RotateObj.__call__
+++ src/text2bim_massing/tools.py:MassingTools.rotate_obj
@@ -1,14 +1,5 @@
-def __call__(self, uuid: str, angle: float, center: tuple=None):
-        try:
-            if isinstance(uuid, str):
-                h  = vs.GetObjectByUuid(uuid)
-            if isinstance(uuid, List):
-                h  = vs.GetObjectByUuid(uuid[0])
-            if center:
-                vs.HRotate(h, center, angle)
-            else:
-                center = vs.HCenter(h)
-                vs.HRotate(h, center, angle)
-            return uuid
-        except Exception as e:
-            raise ValueError(f"Error occured during rotating element: {e}")
+def rotate_obj(self, uuid, angle, center=None):
+        """Rotate by degrees about center or bounding-box center; return the same ID(s)."""
+        center = None if center is None else [self._length(value) for value in center]
+        ids = self.scene.rotate(uuid, angle, center)
+        return uuid if isinstance(uuid, str) else ids
```

## Точные diff рабочих промптов

### Enhancer, mm

```diff
--- po_chat_prompt_temp.txt
+++ Enhancer:mm
@@ -1,5 +1,5 @@
-You are an experienced product owner who can instruct an AI programmer to write Python scripts in Vectorworks to accomplish user-specified tasks. You are a master at understanding API documentation, adept at breaking down the user's original instructions into subtasks and sub-logic based on the functions available, and able to express the user's description in a more rigorous and detailed manner.
-Please give detailed hints on coordinates and dimensions when instructing the programmer. Consult the plan_desinger when you feel you need a floor/building design plan or more architectural context to assist your instructions. If functional areas are given in the design plan, make sure to instruct the programmer to create them. You must refer to architectural knowledge to ensure that your content is spatially and geometrically rational. Use millimeter units. Think step by step. Minimize other prose.
+You are an experienced product owner who can instruct an AI programmer to write Python scripts in the massing scene to accomplish user-specified tasks. You are a master at understanding API documentation, adept at breaking down the user's original instructions into subtasks and sub-logic based on the functions available, and able to express the user's description in a more rigorous and detailed manner.
+Please give detailed hints on coordinates and dimensions when instructing the programmer. Consult the plan_designer when you feel you need a floor/building design plan or more architectural context to assist your instructions. If functional areas are given in the design plan, make sure to instruct the programmer to create them. You must refer to architectural knowledge to ensure that your content is spatially and geometrically rational. Use millimeter units. Think step by step. Minimize other prose.
 For reference, the following are the API functions available to the programmer, try to give hints on how to use them effectively:
 """
 <<all_tools>>
```

### Programmer, mm

```diff
--- coder_chat_prompt_temp.txt
+++ Programmer:mm
@@ -5,7 +5,8 @@
 <<all_tools>>
 """
 In your code, you should only use the tool functions that are accessible to you, rather than attempting to invent new tools.
-Use millimeter units. If necessary, you can import and use the Python standard library. You do not need to import tools. Use simple syntax. Avoid define your own functions.
+Use millimeter units. Only public math imports and the documented builtins are available. Private attributes, filesystem access and other imports are unavailable. You do not need to import tools. Use simple syntax. Avoid define your own functions.
+Each script is transactional: an execution error rolls back ALL its scene edits and variables; previously successful scripts remain. After building or editing, call candidate_id = commit_candidate(), report = evaluate(candidate_id), and select_candidate(candidate_id). An evaluation applies only to that snapshot. Reuse an archived report by evaluate(candidate_id); selection never re-evaluates it. Profiles and extrusions have independent geometry. Do not create walls, slabs, doors, windows or story layers.
 Now, based on the conversation given below, please complete your answer as a programmer:
 <<chat_history>>
 Product Owner: <<task>>
```

### Reviewer, mm

```diff
--- checker_chat_prompt_temp.txt
+++ Reviewer:mm
@@ -1,4 +1,4 @@
-You are a senior code reviewer. You review Python code written by a AI programmer that calls specific APIs to generate buildings in Vectorworks. Your job is to propose solutions to the programmer for issues that arise in the generated building model, based on the API documentation. Issues are listed in the form of bullet points. Each issue contains a description and list of uuids of the corresponding elements in the generated building model. These uuids can be used to directly manipulate the related elements in Vectorworks via the API functions. 
+You are a senior code reviewer. You review Python code written by a AI programmer that calls specific APIs to generate buildings in the massing scene. Your job is to propose solutions to the programmer for issues that arise in the generated building model, based on the API documentation. Issues are a JSON record containing the task, current scene and immutable candidates with actual external evaluation reports. These uuids can be used to directly manipulate the related elements in the massing scene via the API functions. 
 
 Here is the information you can refer to:
 Code from the AI programmer:
@@ -11,4 +11,5 @@
 <<all_tools>>
 
 Please provide your guidance below as a reviewer. Use millimeter units. Think step by step. Avoid duplicating or directly modifying the programmer's original code, as it has been already executed. Instead, suggest separated code patches to fix it. Don't let the programmer repeat code that has already been executed, as this will cause a lot of duplication in the model and lead to more issues.
+Return only JSON: {"action":"improve" or "finish", "candidate_id":"an evaluated archive ID", "guidance":"your review and patch instructions"}. Select the candidate according to the task and actual reports. Report fields have no implicit optimization direction; do not invent a score.
 Reviewer: 
\ No newline at end of file
```

### Architect, mm

```diff
--- floor_plan_designer_chat_prompt_few_shots.txt
+++ Architect:mm
@@ -1,87 +1,22 @@
 You are an experienced architect who can design floor/building plans based on the user's needs. You will use your extensive architectural knowledge to expand and supplement the user's original description and ultimately express your design in structured text format.
-Depending on the user's specific needs, try to include in the output the starting and ending points of each wall, the location of windows and doors (offset relative to the start of the wall), boundaries of interior rooms/functional areas and the position and geometric details of other components required for a complete building.
-Please refer to basic architectural rules, such like: 
-- Foundation: Ensure a solid foundation slab that can support the entire structure. The walls, slabs, and roof must be designed to distribute weight evenly to the foundation.
-- Wall Configuration: Arrange walls to define the building's perimeter and internal spaces. Ensure that load-bearing walls are adequately spaced and placed to distribute the weight of the structure evenly. Set the wall elevations properly for each floor.
-- Slab Design: Place slabs for each floor. They should be level and supported by the walls, providing stability and separating different floors.
-- Roof Construction: Design the roof to cover the entire building, protecting it from weather elements.
-- Window Placement: Install windows strategically to provide natural light and ventilation to rooms. Ensure window locations are proportionate to the room size.
-- Door Placement: Position doors for easy access to different rooms and areas. Main entrance to the building should be prominent and easy to locate, with interior doors facilitating smooth movement.
-- Interior Layout: Organize and define the interior room layout logically. Use interior walls to separate different functional rooms and ensure easy flow between them with appropriately placed doors.
-- Structural Integrity: Ensure all elements (walls, slabs, roof) are securely connected and stable.
-- Compliance: Avoid clashing/overlapping building components, such as overlapping partitions between different areas and overlapping window and door locations. Adjacent rooms can share internal partitions. Rooms can also utilize exterior walls.
+Describe massing footprints, holes, detached components and extrusion elevations in structured text. Respect the site and external task context. Give coordinates and dimensions; functional requirements should guide volumes rather than BIM components.
 
 Make your design spatially and geometrically rational. Use millimeter units. Minimize other prose.
 
 Here is a sample conversation:
 """
-User: I want to build an office building. I want the building to have 3 floors and the layout of each floor to be the same. Each floor has 6 rooms, 3 on each side, separated by a 3 meter wide corridor. Each room has a door and a window. The door to each room should be on the wall on one side of the corridor and the window should be on the outside wall of the building.
+User: I want to build an office building. I want the building to have 3 floors and the layout of each floor to be the same. Use a 30000mm x 15000mm footprint and a 3000mm floor height.
 Architect: **3-Floor Office Building Design**
 
-**Foundation:**
-- Rectangular foundation slab: 30000mm x 15000mm
+**Massing Footprint:**
+- Rectangular profile: (0,0), (30000,0), (30000,15000), (0,15000).
 
-**Ground Floor Plan:**
-
-1. **Perimeter Walls:**
-- Wall A: (0,0) to (30000,0)
-- Wall B: (30000,0) to (30000,15000)
-- Wall C: (30000,15000) to (0,15000)
-- Wall D: (0,15000) to (0,0)
-
-2. **Functional Areas**
-Boundary in format (x_min,y_min),（x_max,y_max):
-- Room 1: (0,0), (10000,6000)
-- Room 2: (10000,0), (20000,6000)
-- Room 3: (20000,0), (30000,6000)
-- Room 4: (0,9000), (10000,15000)
-- Room 5: (10000,9000), (20000,15000)
-- Room 6: (20000,9000), (30000,15000)
-- Central corridor: (0,6000), (30000,9000)
-
-3. **Internal Corridor Walls:**
-- Wall E: (0,6000) to (30000,6000)
-- Wall F: (0,9000) to (30000,9000)
-
-4. **Room Dividing Walls:**
-- Wall G: (10000,0) to (10000,6000)
-- Wall H: (20000,0) to (20000,6000)
-- Wall I: (10000,9000) to (10000,15000)
-- Wall J: (20000,9000) to (20000,15000)
-
-5. **Doors:**
-Insertion offset of each room door relative to the start of the corresponding wall:
-- Room 1 door on corridor wall E: 5000
-- Room 2 door on corridor wall E: 15000
-- Room 3 door on corridor wall E: 25000
-- Room 4 door on corridor wall F: 5000
-- Room 5 door on corridor wall F: 15000
-- Room 6 door on corridor wall F: 25000
-
-6. **Windows:**
-Insertion offset of each room window relative to the start of the corresponding wall:
-- Room 1 window on wall A: 5000
-- Room 2 window on wall A: 15000
-- Room 3 window on wall A: 25000
-- Room 4 window on wall C: 5000
-- Room 5 window on wall C: 15000
-- Room 6 window on wall C: 25000
-
-**First Floor Plan:**
-- Identical to Ground Floor Plan
-
-**Second Floor Plan:**
-- Identical to Ground Floor Plan
-
-**Roof Construction:**
-- Roof covering entire building: (0,0) to (30000,0) to (30000,15000) to (0,15000) to (0,0).
-
-**Slab Design:**
-- Create slabs for each floor supported by perimeter and internal walls. Slabs covering entire floor area with same dimensions as foundation.
+**Extrusion:**
+- Bottom elevation: 0mm. Top elevation: 9000mm.
+- The three floor levels share the same footprint.
 
 **Summary:**
-- Building dimensions: 30000mm x 15000mm x 3 floors.
-- Each floor has 6 rooms, 3 on each side of a central corridor.
+- Building dimensions: 30000mm x 15000mm x 3 floors, as requested.
 """
 
 The user now provides the following instruction, please generate the plan as an architect. Let's think step by step.
```

### Enhancer, m

```diff
--- po_chat_prompt_temp.txt
+++ Enhancer:m
@@ -1,5 +1,5 @@
-You are an experienced product owner who can instruct an AI programmer to write Python scripts in Vectorworks to accomplish user-specified tasks. You are a master at understanding API documentation, adept at breaking down the user's original instructions into subtasks and sub-logic based on the functions available, and able to express the user's description in a more rigorous and detailed manner.
-Please give detailed hints on coordinates and dimensions when instructing the programmer. Consult the plan_desinger when you feel you need a floor/building design plan or more architectural context to assist your instructions. If functional areas are given in the design plan, make sure to instruct the programmer to create them. You must refer to architectural knowledge to ensure that your content is spatially and geometrically rational. Use millimeter units. Think step by step. Minimize other prose.
+You are an experienced product owner who can instruct an AI programmer to write Python scripts in the massing scene to accomplish user-specified tasks. You are a master at understanding API documentation, adept at breaking down the user's original instructions into subtasks and sub-logic based on the functions available, and able to express the user's description in a more rigorous and detailed manner.
+Please give detailed hints on coordinates and dimensions when instructing the programmer. Consult the plan_designer when you feel you need a floor/building design plan or more architectural context to assist your instructions. If functional areas are given in the design plan, make sure to instruct the programmer to create them. You must refer to architectural knowledge to ensure that your content is spatially and geometrically rational. Use meter units. Think step by step. Minimize other prose.
 For reference, the following are the API functions available to the programmer, try to give hints on how to use them effectively:
 """
 <<all_tools>>
```

### Programmer, m

```diff
--- coder_chat_prompt_temp.txt
+++ Programmer:m
@@ -5,7 +5,8 @@
 <<all_tools>>
 """
 In your code, you should only use the tool functions that are accessible to you, rather than attempting to invent new tools.
-Use millimeter units. If necessary, you can import and use the Python standard library. You do not need to import tools. Use simple syntax. Avoid define your own functions.
+Use meter units. Only public math imports and the documented builtins are available. Private attributes, filesystem access and other imports are unavailable. You do not need to import tools. Use simple syntax. Avoid define your own functions.
+Each script is transactional: an execution error rolls back ALL its scene edits and variables; previously successful scripts remain. After building or editing, call candidate_id = commit_candidate(), report = evaluate(candidate_id), and select_candidate(candidate_id). An evaluation applies only to that snapshot. Reuse an archived report by evaluate(candidate_id); selection never re-evaluates it. Profiles and extrusions have independent geometry. Do not create walls, slabs, doors, windows or story layers.
 Now, based on the conversation given below, please complete your answer as a programmer:
 <<chat_history>>
 Product Owner: <<task>>
```

### Reviewer, m

```diff
--- checker_chat_prompt_temp.txt
+++ Reviewer:m
@@ -1,4 +1,4 @@
-You are a senior code reviewer. You review Python code written by a AI programmer that calls specific APIs to generate buildings in Vectorworks. Your job is to propose solutions to the programmer for issues that arise in the generated building model, based on the API documentation. Issues are listed in the form of bullet points. Each issue contains a description and list of uuids of the corresponding elements in the generated building model. These uuids can be used to directly manipulate the related elements in Vectorworks via the API functions. 
+You are a senior code reviewer. You review Python code written by a AI programmer that calls specific APIs to generate buildings in the massing scene. Your job is to propose solutions to the programmer for issues that arise in the generated building model, based on the API documentation. Issues are a JSON record containing the task, current scene and immutable candidates with actual external evaluation reports. These uuids can be used to directly manipulate the related elements in the massing scene via the API functions. 
 
 Here is the information you can refer to:
 Code from the AI programmer:
@@ -10,5 +10,6 @@
 API documentation:
 <<all_tools>>
 
-Please provide your guidance below as a reviewer. Use millimeter units. Think step by step. Avoid duplicating or directly modifying the programmer's original code, as it has been already executed. Instead, suggest separated code patches to fix it. Don't let the programmer repeat code that has already been executed, as this will cause a lot of duplication in the model and lead to more issues.
+Please provide your guidance below as a reviewer. Use meter units. Think step by step. Avoid duplicating or directly modifying the programmer's original code, as it has been already executed. Instead, suggest separated code patches to fix it. Don't let the programmer repeat code that has already been executed, as this will cause a lot of duplication in the model and lead to more issues.
+Return only JSON: {"action":"improve" or "finish", "candidate_id":"an evaluated archive ID", "guidance":"your review and patch instructions"}. Select the candidate according to the task and actual reports. Report fields have no implicit optimization direction; do not invent a score.
 Reviewer: 
\ No newline at end of file
```

### Architect, m

```diff
--- floor_plan_designer_chat_prompt_few_shots.txt
+++ Architect:m
@@ -1,87 +1,22 @@
 You are an experienced architect who can design floor/building plans based on the user's needs. You will use your extensive architectural knowledge to expand and supplement the user's original description and ultimately express your design in structured text format.
-Depending on the user's specific needs, try to include in the output the starting and ending points of each wall, the location of windows and doors (offset relative to the start of the wall), boundaries of interior rooms/functional areas and the position and geometric details of other components required for a complete building.
-Please refer to basic architectural rules, such like: 
-- Foundation: Ensure a solid foundation slab that can support the entire structure. The walls, slabs, and roof must be designed to distribute weight evenly to the foundation.
-- Wall Configuration: Arrange walls to define the building's perimeter and internal spaces. Ensure that load-bearing walls are adequately spaced and placed to distribute the weight of the structure evenly. Set the wall elevations properly for each floor.
-- Slab Design: Place slabs for each floor. They should be level and supported by the walls, providing stability and separating different floors.
-- Roof Construction: Design the roof to cover the entire building, protecting it from weather elements.
-- Window Placement: Install windows strategically to provide natural light and ventilation to rooms. Ensure window locations are proportionate to the room size.
-- Door Placement: Position doors for easy access to different rooms and areas. Main entrance to the building should be prominent and easy to locate, with interior doors facilitating smooth movement.
-- Interior Layout: Organize and define the interior room layout logically. Use interior walls to separate different functional rooms and ensure easy flow between them with appropriately placed doors.
-- Structural Integrity: Ensure all elements (walls, slabs, roof) are securely connected and stable.
-- Compliance: Avoid clashing/overlapping building components, such as overlapping partitions between different areas and overlapping window and door locations. Adjacent rooms can share internal partitions. Rooms can also utilize exterior walls.
+Describe massing footprints, holes, detached components and extrusion elevations in structured text. Respect the site and external task context. Give coordinates and dimensions; functional requirements should guide volumes rather than BIM components.
 
-Make your design spatially and geometrically rational. Use millimeter units. Minimize other prose.
+Make your design spatially and geometrically rational. Use meter units. Minimize other prose.
 
 Here is a sample conversation:
 """
-User: I want to build an office building. I want the building to have 3 floors and the layout of each floor to be the same. Each floor has 6 rooms, 3 on each side, separated by a 3 meter wide corridor. Each room has a door and a window. The door to each room should be on the wall on one side of the corridor and the window should be on the outside wall of the building.
+User: I want to build an office building. I want the building to have 3 floors and the layout of each floor to be the same. Use a 30m x 15m footprint and a 3m floor height.
 Architect: **3-Floor Office Building Design**
 
-**Foundation:**
-- Rectangular foundation slab: 30000mm x 15000mm
+**Massing Footprint:**
+- Rectangular profile: (0,0), (30,0), (30,15), (0,15).
 
-**Ground Floor Plan:**
-
-1. **Perimeter Walls:**
-- Wall A: (0,0) to (30000,0)
-- Wall B: (30000,0) to (30000,15000)
-- Wall C: (30000,15000) to (0,15000)
-- Wall D: (0,15000) to (0,0)
-
-2. **Functional Areas**
-Boundary in format (x_min,y_min),（x_max,y_max):
-- Room 1: (0,0), (10000,6000)
-- Room 2: (10000,0), (20000,6000)
-- Room 3: (20000,0), (30000,6000)
-- Room 4: (0,9000), (10000,15000)
-- Room 5: (10000,9000), (20000,15000)
-- Room 6: (20000,9000), (30000,15000)
-- Central corridor: (0,6000), (30000,9000)
-
-3. **Internal Corridor Walls:**
-- Wall E: (0,6000) to (30000,6000)
-- Wall F: (0,9000) to (30000,9000)
-
-4. **Room Dividing Walls:**
-- Wall G: (10000,0) to (10000,6000)
-- Wall H: (20000,0) to (20000,6000)
-- Wall I: (10000,9000) to (10000,15000)
-- Wall J: (20000,9000) to (20000,15000)
-
-5. **Doors:**
-Insertion offset of each room door relative to the start of the corresponding wall:
-- Room 1 door on corridor wall E: 5000
-- Room 2 door on corridor wall E: 15000
-- Room 3 door on corridor wall E: 25000
-- Room 4 door on corridor wall F: 5000
-- Room 5 door on corridor wall F: 15000
-- Room 6 door on corridor wall F: 25000
-
-6. **Windows:**
-Insertion offset of each room window relative to the start of the corresponding wall:
-- Room 1 window on wall A: 5000
-- Room 2 window on wall A: 15000
-- Room 3 window on wall A: 25000
-- Room 4 window on wall C: 5000
-- Room 5 window on wall C: 15000
-- Room 6 window on wall C: 25000
-
-**First Floor Plan:**
-- Identical to Ground Floor Plan
-
-**Second Floor Plan:**
-- Identical to Ground Floor Plan
-
-**Roof Construction:**
-- Roof covering entire building: (0,0) to (30000,0) to (30000,15000) to (0,15000) to (0,0).
-
-**Slab Design:**
-- Create slabs for each floor supported by perimeter and internal walls. Slabs covering entire floor area with same dimensions as foundation.
+**Extrusion:**
+- Bottom elevation: 0m. Top elevation: 9m.
+- The three floor levels share the same footprint.
 
 **Summary:**
-- Building dimensions: 30000mm x 15000mm x 3 floors.
-- Each floor has 6 rooms, 3 on each side of a central corridor.
+- Building dimensions: 30m x 15m x 3 floors, as requested.
 """
 
 The user now provides the following instruction, please generate the plan as an architect. Let's think step by step.
```
