# Разработка и работа с Git

Основной принцип: сохранять код и взаимодействие Text2BIM, добавляя минимально
необходимые обёртки. Задачи и границы изменений описаны в
[плане](Text2BIM-Massing-implementation-plan.md), фактическое состояние — в
[docs/status.md](docs/status.md).

## Окружение

Закреплённое проверенное окружение — Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Для Python 3.11–3.13 с диапазонами совместимости:

```bash
python -m pip install -e '.[dev,llm,mesh,maslov]'
```

Рабочую версию Python задаёт `.python-version`. `requirements-dev.txt` —
snapshot проверенного окружения Python 3.12, а не универсальный lock всех платформ.

## Порядок изменения

1. Создать ветку с понятной задачей: `feat/…`, `fix/…`, `docs/…`.
2. Сохранить исходные файлы `upstream/` побайтово. При правке перенесённого кода
   сначала свериться с оригиналом и [картой переноса](docs/source-map.md).
3. Одновременно записать причину, влияние и проверку в
   `docs/text2bim-adaptation.md`; обновить ручной `docs/adaptation-spec.json`.
   Новый файл должен войти в `file_groups`, изменение метода — в соответствующую
   запись. Простое обновление хеша не заменяет эту сверку.
4. Обновить инструкции, статус и план, если изменились возможности или ограничения.
5. Сформировать реестр и выполнить проверки ниже. Не править генерируемые diff
   и lock вручную.
6. Сделать содержательный commit и PR: проблема, новое поведение, влияние на
   baseline и фактическая проверка. Связанные изменения держать вместе.

```bash
python tools/audit_adaptation.py --write
python tools/audit_adaptation.py --check
```

`.gitattributes` сохраняет исходные файлы и vendor-код без преобразования
окончаний строк. Не выполнять массовое переформатирование этих каталогов.
Upstream/vendor помечены для GitHub как заимствованные, diff и lock — как
генерируемые; это не исключает их из Git или проверки.

## Проверки

```bash
python -m pip check
ruff check src tests examples tools integrations
ruff format --check src tests examples tools integrations
python tools/audit_adaptation.py --check
python -m pytest -c pyproject.toml tests -q
python -m build
python examples/scene_without_llm.py > /tmp/text2bim-massing.json
git diff --check
```

С точным внешним checkout Маслова:

```bash
python -m pytest -c pyproject.toml tests -q \
  --maslov-repo /path/to/massing-generation
```

Ожидаемый HEAD — `607ff1fcf80477787409522d93e18e42ac1436cf`, `src/` должен
совпадать с commit. Без checkout двенадцать интеграционных тестов пропускаются.
Все автоматические тесты обходятся без сетевого LLM; живые прогоны выполняются
отдельно и записываются в [отчёт](docs/validation.md), включая неудачи.

## Linux

```bash
docker build -t text2bim-massing .
docker run --rm text2bim-massing
```

Для внешних интеграционных тестов подключить checkout только для чтения:

```bash
docker run --rm \
  --mount type=bind,source=/absolute/path/to/massing-generation,target=/maslov,readonly \
  -e GIT_CONFIG_COUNT=1 \
  -e GIT_CONFIG_KEY_0=safe.directory \
  -e GIT_CONFIG_VALUE_0=/maslov \
  text2bim-massing \
  python -m pytest -c pyproject.toml tests -q --maslov-repo /maslov
```

Docker по умолчанию выполняет тесты. CLI, авторизация и данные живого
эксперимента не встроены в образ.

## Что хранить в репозитории

Хранить код, конфиги без секретов, исходники с provenance, документацию и
проверяемый реестр. `.venv/`, `.local/`, `runs/`, `outputs/`, сборки, кеши и
локальные `.env` исключены из Git. В отчёте достаточно сохранить версию,
конфигурацию, показатели и путь к локальным артефактам; сырые traces не
появляются у другого пользователя после clone.

Тонкий runner версионируется в `integrations/maslov/`. Если его файлы копируются
во внешний checkout, сохранять совпадение копий и отдельно фиксировать commit
или PR целевого репозитория. Изменение README этого пакета не обновляет
внешнюю копию автоматически.
