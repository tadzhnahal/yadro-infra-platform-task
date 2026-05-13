# HTTP Status Checker с автоматизацией на Python, Docker и Ansible

## О проекте

Этот репозиторий содержит решение тестового задания по автоматизации HTTP-проверок от команды разработки внутренней инфраструктуры и платформ продуктов YADRO.

Проект состоит из трёх частей:

1. Python-скрипт выполняет HTTP-запросы к сервису `https://httpstat.us` и обрабатывает ответы по группам статус-кодов.
2. Docker-образ на базе `ubuntu:22.04` содержит скрипт и зависимости для его запуска.
3. Ansible playbook готовит Docker на целевом хосте, собирает образ, запускает контейнер и проверяет результат через `docker logs`.

Главный файл первого раздела лежит в `script/http_status_checker.py`. Dockerfile лежит в `docker/Dockerfile`. Ansible-сценарий запускается через `ansible/playbook.yml`.

## Стек

Python, Docker, Ansible.

## Структура репозитория

Папка `script` хранит Python-скрипт и файл зависимостей, `docker` содержит Dockerfile для сборки образа на базе `ubuntu:22.04`, `ansible` включает inventory-файл, конфигурацию Ansible, основной playbook и отдельные task-файлы. Файл `.dockerignore` убирает из Docker-контекста виртуальное окружение, Git-файлы, кэш Python и файлы IDE.

```text
.
├── .dockerignore
├── .gitignore
├── README.md
├── ansible
│   ├── ansible.cfg
│   ├── inventory.ini
│   ├── playbook.yml
│   └── tasks
│       ├── build_image.yml
│       ├── check_container.yml
│       ├── prepare_docker.yml
│       └── run_container.yml
├── docker
│   └── Dockerfile
└── script
    ├── http_status_checker.py
    └── requirements.txt
```

## Основные решения

### Как работает python-скрипт

Скрипт выполняет пять запросов к разным статус-кодам:

```text
102
200
302
404
500
```

Так он проверяет все группы из задания:

* `102` проверяет группу `1xx`;
* `200` проверяет группу `2xx`;
* `302` проверяет группу `3xx`;
* `404` проверяет группу `4xx`;
* `500` проверяет группу `5xx`.

Для ответов `1xx`, `2xx` и `3xx` скрипт пишет в лог статус-код и тело ответа, а для ответов `4xx` и `5xx` создаёт exception. В `main()` скрипт ловит ошибки, пишет их в лог и переходит к следующему запросу. Так один плохой ответ не останавливает все пять проверок.

По умолчанию скрипт обращается к адресу из задания:

```text
https://httpstat.us
```

Во время проверки этот сервис может рвать соединение и не возвращать HTTP-ответ. Поэтому он поддерживает переменную окружения `HTTP_STATUS_BASE_URL`, которая позволяет передать совместимый эндпоинт без правки кода.

### Как работает Docker

Dockerfile использует официальный образ `ubuntu:22.04`. Образ ставит `python3`, `python3-pip`, `ca-certificates` и Python-зависимости из `script/requirements.txt`.

Контейнер запускает скрипт при старте через `CMD`. Поэтому для запуска контейнера не нужно вручную указывать команду `python3`.

### Как работает Ansible

Ansible работает с локальным хостом через inventory-файл:

```text
localhost ansible_connection=local
```

Playbook делает следующее:

1. Определяет целевую систему.
2. Выбирает Docker-пакеты под семейство ОС.
3. Устанавливает Docker и нужные зависимости.
4. Добавляет текущего пользователя в группу `docker`.
5. Запускает и включает `docker.service`.
6. Проверяет `docker --version`.
7. Собирает Docker-образ.
8. Запускает контейнер со скриптом.
9. Проверяет код выхода контейнера.
10. Читает `docker logs`.
11. Проверяет, что в логах есть все пять запросов.

Я разделил Ansible-задачи на несколько файлов в `ansible/tasks`, потому что общий playbook вырос. Главный `playbook.yml` показывает порядок шагов, а task-файлы хранят детали.

## Как запустить проект

### 1. Подготовьте окружение

Установите Python 3, Docker и Ansible. Для запуска Ansible playbook нужен пользователь с правами `sudo`.

Проверьте Python. Выполните команду:

```bash
python3 --version
```

Проверьте Docker. Выполните команду:

```bash
docker --version
```

Проверьте Ansible. Выполните команду:

```bash
ansible --version
```

### 2. Склонируйте репозиторий

Склонируйте проект и перейдите в его корень. Выполните команду:

```bash
git clone https://github.com/tadzhnahal/yadro-infra-platform-task
cd yadro-infra-platform-task
```

### 3. Создайте Python-окружение

Создайте виртуальное окружение и активируйте его. Выполните команду:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установите зависимости для локального запуска скрипта. Выполните команду:

```bash
python -m pip install -r script/requirements.txt
```

### 4. Запустите Python-скрипт локально

Запустите скрипт с совместимым эндпоинтом. Выполните команду:

```bash
HTTP_STATUS_BASE_URL=https://tools-httpstatus.pickup-services.com python script/http_status_checker.py
```

В выводе появятся пять запросов. Для `200` и `302` скрипт выведет `successful response`. Для `404` и `500` скрипт выведет ошибку `status check failed`.

Можно также запустить скрипт с адресом из задания. Выполните команду:

```bash
python script/http_status_checker.py
```

В этом режиме скрипт использует `https://httpstat.us`. Если сервис рвёт соединение, скрипт выведет сетевые ошибки через logging и всё равно пройдёт все пять запросов.

### 5. Соберите Docker-образ вручную

Соберите образ из корня репозитория. Выполните команду:

```bash
docker build -f docker/Dockerfile -t yadro-http-checker .
```

После сборки проверьте образ. Выполните команду:

```bash
docker images yadro-http-checker
```

В списке появится образ `yadro-http-checker:latest`.

### 6. Запустите контейнер вручную

Удалите старый контейнер с таким именем, если он остался после прошлой проверки. Выполните команду:

```bash
docker rm -f yadro-http-checker-container 2>/dev/null || true
```

Запустите контейнер со скриптом. Выполните команду:

```bash
docker run --name yadro-http-checker-container \
  -e HTTP_STATUS_BASE_URL=https://tools-httpstatus.pickup-services.com \
  yadro-http-checker
```

Контейнер запустит скрипт и завершит работу.

### 7. Проверьте логи контейнера

Посмотрите логи контейнера. Выполните команду:

```bash
docker logs yadro-http-checker-container
```

В логах появятся строки с кодами:

```text
requested_status_code=102
requested_status_code=200
requested_status_code=302
requested_status_code=404
requested_status_code=500
```

Проверьте код выхода контейнера. Выполните команду:

```bash
docker inspect yadro-http-checker-container --format='{{.State.ExitCode}}'
```

Ожидаемый результат:

```text
0
```

### 8. Запустите Ansible playbook

Перейдите в папку `ansible`. Выполните команду:

```bash
cd ansible
```

Проверьте, что Ansible видит локальный хост. Выполните команду:

```bash
ansible local -m ping
```

Ожидаемый результат содержит:

```text
localhost | SUCCESS
```

Запустите playbook. Выполните команду:

```bash
ansible-playbook playbook.yml --ask-become-pass
```

Введите пароль пользователя, когда Ansible попросит `BECOME password`.

Playbook завершится без ошибок, если Docker и Ansible работают корректно. В конце вывода должен быть блок `PLAY RECAP` со значением:

```text
failed=0
```

## Как проверить результат

### 1. Проверьте Docker после Ansible

Проверьте версию Docker. Выполните команду:

```bash
docker --version
```

Команда выведет версию Docker.

Проверьте состояние службы Docker. Выполните команду:

```bash
systemctl is-active docker
```

Ожидаемый результат:

```text
active
```

Проверьте автозапуск службы Docker. Выполните команду:

```bash
systemctl is-enabled docker
```

Ожидаемый результат:

```text
enabled
```

### 2. Проверьте образ после Ansible

Посмотрите образ, который собрал playbook. Выполните команду:

```bash
docker images yadro-http-checker
```

В списке появится образ `yadro-http-checker:latest`.

### 3. Проверьте контейнер после Ansible

Посмотрите контейнер. Выполните команду:

```bash
docker ps -a --filter "name=yadro-http-checker-container"
```

Контейнер будет в статусе `Exited`, потому что он запускает скрипт один раз и завершает работу.

Проверьте код выхода контейнера. Выполните команду:

```bash
docker inspect yadro-http-checker-container --format='{{.State.ExitCode}}'
```

Ожидаемый результат:

```text
0
```

### 4. Проверьте логи после Ansible

Посмотрите логи контейнера. Выполните команду:

```bash
docker logs yadro-http-checker-container
```

В логах появятся все пять запросов. Для `200` и `302` будут успешные ответы. Для `404` и `500` будут ошибки из-за плохого HTTP-ответа.

Ansible также проверяет эти строки сам. В выводе playbook появятся сообщения:

```text
Log item found: requested_status_code=102
Log item found: requested_status_code=200
Log item found: requested_status_code=302
Log item found: requested_status_code=404
Log item found: requested_status_code=500
Container logs were checked successfully
```

## Как остановить проект

Контейнер со скриптом завершает работу сам. Если нужно удалить его вручную, выполните команду:

```bash
docker rm -f yadro-http-checker-container
```

Если нужно удалить Docker-образ проекта, выполните команду:

```bash
docker rmi yadro-http-checker
```
