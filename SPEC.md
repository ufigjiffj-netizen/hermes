\# Hermes — Technical Specification



\## 1. Назначение



\*\*Hermes\*\* — специализированный асинхронный бот для полной автоматизации продаж на FunPay.



Hermes предназначен для:



\* автоматизации продаж;

\* автоматической выдачи товаров/лотов;

\* автоматического поднятия лотов;

\* обработки заказов;

\* работы с аккаунтом FunPay через `golden key`;

\* работы через proxy;

\* асинхронного выполнения сетевых операций;

\* управления через встроенный CLI;

\* расширения функциональности через plugins;

\* работы с SQLite без внешних сервисов;

\* опциональной работы с PostgreSQL;

\* запуска как systemd service;

\* deployment через Ansible.



Hermes не проектируется как универсальный marketplace framework. Единственная поддерживаемая торговая площадка — FunPay.



\---



\# 2. Главные архитектурные принципы



\## 2.1. FunPay является частью Core



Не требуется:



```yaml

funpay:

&#x20; enabled: true

```



или:



```yaml

marketplace:

&#x20; type: funpay

```



FunPay является не опциональным модулем, а основной платформой Hermes.



\---



\## 2.2. Core + Plugins



Архитектура:



```text

Hermes

│

├── Core

│   ├── FunPay client

│   ├── authentication

│   ├── orders

│   ├── lots

│   ├── auto-bump

│   ├── delivery

│   ├── scheduler

│   ├── networking

│   ├── rate limiting

│   ├── logging

│   ├── configuration

│   ├── secrets

│   ├── storage

│   └── CLI

│

└── Plugins

&#x20;   ├── AI replies

&#x20;   ├── account rental

&#x20;   ├── Telegram

&#x20;   ├── Discord

&#x20;   └── Web panel

```



CLI является частью Core.



Plugins используются только для функциональности, которая не является обязательной для базовой работы Hermes.



\---



\# 3. Core functionality



Hermes без единого plugin должен поддерживать:



\* подключение к FunPay;

\* авторизацию через `golden key`;

\* получение данных FunPay;

\* отправку запросов;

\* обработку заказов;

\* автоматическую выдачу;

\* автоматическое поднятие лотов;

\* scheduler;

\* rate limiting;

\* connection pooling;

\* proxy;

\* logging;

\* SQLite;

\* optional PostgreSQL;

\* configuration;

\* Secret Store;

\* CLI;

\* graceful shutdown;

\* configuration reload.



\---



\# 4. Асинхронная архитектура



Все сетевые операции должны быть реализованы через async I/O.



Основная модель:



```text

Event Loop

│

├── FunPay HTTP

├── order polling

├── order processing

├── lot management

├── delivery

├── scheduler

├── plugins

└── network operations

```



Не создавать отдельный thread для каждой операции.



Thread/process pool используется только для CPU-bound или несовместимых с async операций.



\---



\# 5. Производительность



Целевая среда:



```text

CPU: 1 core

RAM: 768 MB

```



Hermes должен быть пригоден для работы на минимальной VPS.



Ожидаемая нагрузка FunPay:



```text

обычно: 0–1 RPS

пики: до \~10 RPS

```



Поэтому Hermes не должен быть оптимизирован под огромный throughput.



Приоритеты:



1\. стабильность;

2\. низкое потребление памяти;

3\. низкое потребление CPU;

4\. корректное поведение при коротких пиках;

5\. минимальное количество background workers.



Не использовать обязательные:



\* Redis;

\* RabbitMQ;

\* Kafka;

\* Celery;

\* отдельные queue services;

\* отдельный cache server.



\---



\# 6. HTTP connection pool



FunPay client должен использовать connection pooling.



Пример конфигурации:



```yaml

network:

&#x20; connections:

&#x20;   max: 10

&#x20;   keepalive: 5

```



Размеры должны иметь разумные built-in defaults.



\---



\# 7. Rate limiting



В Core должен присутствовать rate limiter.



Пример:



```yaml

network:

&#x20; rate\_limit:

&#x20;   requests\_per\_second: 5

&#x20;   burst: 10

```



Rate limiter должен поддерживать:



\* requests-per-second;

\* burst;

\* backpressure;

\* ожидание свободного slot;

\* отмену операции;

\* корректную работу с async tasks.



\---



\# 8. Proxy



Hermes должен поддерживать proxy для исходящего FunPay traffic.



Пример:



```yaml

network:

&#x20; proxy:

&#x20;   enabled: true

&#x20;   mode: all

```



Отключение:



```yaml

network:

&#x20; proxy:

&#x20;   enabled: false

```



`enabled: true/false` является стандартным стилем Hermes для boolean-настроек.



Proxy credentials находятся в Secret Store:



```yaml

network:

&#x20; proxy:

&#x20;   enabled: true

&#x20;   mode: all

&#x20;   host: proxy.example.com

&#x20;   port: 8080

&#x20;   username:

&#x20;     secret: proxy.username

&#x20;   password:

&#x20;     secret: proxy.password

```



\---



\# 9. Configuration style



Конфигурация Hermes должна быть:



\* YAML;

\* иерархической;

\* декларативной;

\* читаемой человеком;

\* предсказуемой;

\* похожей по качеству UX на конфигурацию Nginx, Grafana и Prometheus.



Главный принцип:



> Пользователь описывает желаемое поведение Hermes, а не внутренние классы и функции.



\---



\# 10. Boolean directives



Стандарт Hermes:



```yaml

enabled: true

```



или:



```yaml

enabled: false

```



Например:



```yaml

lots:

&#x20; auto\_bump:

&#x20;   enabled: true

```



или:



```yaml

network:

&#x20; proxy:

&#x20;   enabled: false

```



Не использовать различные варианты:



```yaml

enable: true

active: true

use: true

disable: false

```



для одной и той же семантики.



Стандартное имя boolean-директивы:



```text

enabled

```



\---



\# 11. Когда использовать `mode` и `type`



Boolean используется только для фактического включения/выключения.



Если существует несколько режимов, используется `mode`.



Например:



```yaml

proxy:

&#x20; enabled: true

&#x20; mode: all

```



Если выбирается backend:



```yaml

storage:

&#x20; type: sqlite

```



Таким образом:



```text

enabled → включено/выключено



mode → режим работы



type → тип backend/implementation

```



\---



\# 12. Configuration file



Основной файл:



```text

/etc/hermes/hermes.yaml

```



Но он \*\*не обязателен\*\*.



Hermes должен запускаться даже при полном отсутствии конфигурационного файла.



Модель:



```text

Built-in defaults

&#x20;      ↓

/etc/hermes/hermes.yaml

&#x20;      ↓

Effective configuration

```



Пользовательский YAML содержит только overrides.



Не требуется копировать defaults в configuration file.



\---



\# 13. Built-in defaults



Defaults являются частью Hermes.



Не создавать обязательный:



```text

/etc/hermes/default.yaml

```



или:



```text

/usr/share/hermes/default.yaml

```



Hermes самостоятельно знает свои defaults.



При отсутствии:



```text

/etc/hermes/hermes.yaml

```



Hermes использует built-in defaults.



\---



\# 14. Configuration validation



Команда:



```bash

hermes -t

```



проверяет:



\* YAML syntax;

\* schema;

\* types;

\* unknown directives;

\* invalid values;

\* secret references;

\* incompatible options;

\* ranges;

\* deprecated directives.



Отсутствие config не является ошибкой:



```text

Configuration file not found.

Using built-in defaults.



Configuration is valid.

```



Ошибка:



```text

Configuration error:



&#x20; network.rate\_limit.requests\_per\_second



&#x20; expected: positive number

&#x20; got: "fast"

```



Сообщения должны быть ориентированы на пользователя, а не на разработчика.



\---



\# 15. Effective configuration



Команда:



```bash

hermes -T

```



показывает effective configuration:



```text

built-in defaults

\+

hermes.yaml

```



Секреты никогда не раскрываются.



Например:



```yaml

account:

&#x20; golden\_key:

&#x20;   secret: funpay.golden\_key

```



а не фактическое значение.



\---



\# 16. Пример configuration



Минимальный пользовательский конфиг:



```yaml

account:

&#x20; golden\_key:

&#x20;   secret: funpay.golden\_key

```



Более полный:



```yaml

logging:

&#x20; level: info



&#x20; modules:

&#x20;   funpay.orders:

&#x20;     level: debug



network:

&#x20; timeout: 30s

&#x20; connect\_timeout: 10s



&#x20; proxy:

&#x20;   enabled: true

&#x20;   mode: all



&#x20; connections:

&#x20;   max: 10

&#x20;   keepalive: 5



&#x20; rate\_limit:

&#x20;   requests\_per\_second: 5

&#x20;   burst: 10



account:

&#x20; golden\_key:

&#x20;   secret: funpay.golden\_key



polling:

&#x20; interval: 2s

&#x20; max\_interval: 15s



orders:

&#x20; concurrency: 2



lots:

&#x20; auto\_bump:

&#x20;   enabled: true

&#x20;   interval: 30m



storage:

&#x20; type: sqlite

&#x20; path: /var/lib/hermes/hermes.db

```



\---



\# 17. Secrets



Secret Store является частью Core.



Не хранить secrets непосредственно в `hermes.yaml`.



Пример:



```yaml

account:

&#x20; golden\_key:

&#x20;   secret: funpay.golden\_key

```



Поддерживаемые секреты:



\* FunPay golden key;

\* proxy password;

\* PostgreSQL password;

\* API tokens;

\* Telegram token;

\* Discord token;

\* AI API keys;

\* другие credentials plugins.



\---



\# 18. Password hashing



Пароли, которые Hermes должен только проверять, должны храниться как password verifiers:



```text

password

&#x20;  ↓

Argon2id

&#x20;  ↓

salt + hash

```



Использовать:



\* Argon2id;

\* уникальную cryptographically random salt;

\* безопасные параметры cost;

\* constant-time comparison.



Исходный пароль не должен храниться.



\---



\# 19. Operational secrets



Golden key и другие credentials, которые Hermes должен получить в исходном виде, нельзя хранить как hash.



Для них используется encrypted storage.



Архитектура:



```text

Secret Store

│

├── passwords

│   └── Argon2id + salt

│

└── operational secrets

&#x20;   └── authenticated encryption

```



\---



\# 20. Secret CLI



Предусмотреть:



```bash

hermes secrets init

hermes secrets set <name>

hermes secrets list

hermes secrets remove <name>

hermes secrets rotate

hermes secrets backup

hermes secrets restore

```



Например:



```bash

hermes secrets set funpay.golden\_key

```



Значение вводится без echo.



```bash

hermes secrets list

```



Результат:



```text

NAME                         STATUS

funpay.golden\_key            configured

proxy.username               configured

proxy.password               configured

postgres.password             configured

```



Значения никогда не выводятся.



\---



\# 21. Secret vault



Encrypted operational secrets должны храниться отдельно от YAML.



Например:



```text

/etc/hermes/

├── hermes.yaml

└── secrets/

&#x20;   └── vault

```



Vault должен обновляться атомарно:



```text

read

&#x20;↓

decrypt

&#x20;↓

modify

&#x20;↓

encrypt

&#x20;↓

write temporary file

&#x20;↓

fsync

&#x20;↓

atomic rename

```



Это предотвращает повреждение vault при crash/power loss.



\---



\# 22. Secret unlock



Secret Store должен иметь абстракцию unlock provider:



```text

Secret Unlock Provider

│

├── password

├── protected key file

└── future TPM/system integration

```



Не привязывать Core к одному способу получения encryption key.



\---



\# 23. FunPay authentication



FunPay account authentication выполняется через golden key.



Configuration:



```yaml

account:

&#x20; golden\_key:

&#x20;   secret: funpay.golden\_key

```



CLI:



```bash

hermes secrets set funpay.golden\_key

```



Проверка:



```bash

hermes account auth test

```



Golden key:



\* не отображается в CLI;

\* не записывается в обычные logs;

\* не попадает в `hermes -T`;

\* не находится в YAML.



\---



\# 24. Storage abstraction



Storage API должен быть абстрагирован:



```text

Storage

├── SQLite

└── PostgreSQL

```



SQLite является default.



\---



\# 25. SQLite



Default:



```yaml

storage:

&#x20; type: sqlite

```



Database:



```text

/var/lib/hermes/hermes.db

```



SQLite позволяет запустить Hermes без внешней инфраструктуры.



\---



\# 26. PostgreSQL



PostgreSQL является optional.



Пример:



```yaml

storage:

&#x20; type: postgres



&#x20; postgres:

&#x20;   host: 127.0.0.1

&#x20;   port: 5432

&#x20;   database: hermes

&#x20;   username: hermes

&#x20;   password:

&#x20;     secret: postgres.password

```



Сам PostgreSQL server не является частью Hermes deployment.



\---



\# 27. Logging



Logging должен быть иерархическим.



Например:



```text

funpay

funpay.http

funpay.orders

funpay.orders.delivery

plugins

plugins.ai

plugins.telegram

```



Global level:



```yaml

logging:

&#x20; level: info

```



Specific module:



```yaml

logging:

&#x20; level: info



&#x20; modules:

&#x20;   funpay.orders:

&#x20;     level: debug

```



Более глубокий module имеет приоритет над родительским.



\---



\# 28. CLI



CLI входит в Core из коробки.



CLI должен быть ориентирован на действия пользователя.



Пример:



```bash

hermes status

hermes start

hermes stop

hermes restart

hermes reload

hermes logs

```



Configuration:



```bash

hermes -t

hermes -T

```



Account:



```bash

hermes account status

hermes account auth test

```



Orders:



```bash

hermes orders list

hermes orders status

```



Lots:



```bash

hermes lots list

hermes lots bump

```



Secrets:



```bash

hermes secrets init

hermes secrets set ...

hermes secrets list

```



Plugins:



```bash

hermes plugins list

hermes plugins status

```



\---



\# 29. Nginx-style CLI



Hermes должен поддерживать привычные Nginx-like semantics:



```bash

hermes -t

```



Проверка конфигурации.



```bash

hermes -T

```



Показ effective configuration.



```bash

hermes -s reload

```



Reload runtime configuration.



Приоритет — удобство и предсказуемость CLI.



\---



\# 30. Plugin system



Plugin API проектируется заранее.



Plugin должен иметь доступ к официальным Core APIs:



```text

Plugin API

│

├── lifecycle

├── configuration

├── logging

├── secrets

├── storage

├── scheduler

├── networking

├── events

├── CLI registration

└── capabilities

```



Plugins не должны зависеть от внутренних implementation details Core.



\---



\# 31. Planned plugins



Возможные plugins:



```text

AI replies

Account rental

Telegram

Discord

Web panel

```



\### AI replies



Автоматические ответы покупателям.



\### Account rental



Автоматизация аренды аккаунтов.



\### Telegram



Telegram interface для управления Hermes.



\### Discord



Discord interface.



\### Web panel



Полноценная web administration panel.



\---



\# 32. GUI architecture



GUI не входит в Core.



GUI является внешним интерфейсом Hermes.



```text

Hermes Core

&#x20;    │

&#x20; API/events

&#x20;    │

&#x20;┌───┼──────────────┐

&#x20;▼   ▼              ▼

TG  Discord        Web

```



Можно создать любой интерфейс без изменения Core.



\---



\# 33. Event Bus



Для plugins предусмотреть event bus.



Примеры:



```text

order.created

order.paid

order.completed

order.cancelled



lot.created

lot.updated

lot.bumped



account.connected

account.disconnected



message.received

message.sent

```



Plugins могут подписываться на события.



\---



\# 34. Plugin isolation



Plugin API должен предусматривать capabilities.



В перспективе plugin может явно запрашивать:



```text

storage

network

secrets

events

cli

```



Это позволит контролировать доступ plugins к ресурсам Hermes.



\---



\# 35. Polling



При обычной нагрузке 0–1 RPS Hermes не должен выполнять агрессивный polling.



Пример:



```yaml

polling:

&#x20; interval: 2s

&#x20; max\_interval: 15s

```



В будущем допускается adaptive polling:



```text

activity ↑ → faster polling

activity ↓ → slower polling

```



\---



\# 36. Graceful shutdown



Поддерживать:



```text

SIGTERM

SIGINT

SIGHUP

```



Shutdown:



```text

signal

&#x20;↓

stop accepting new tasks

&#x20;↓

finish safe operations

&#x20;↓

close FunPay connections

&#x20;↓

close storage

&#x20;↓

flush logs

&#x20;↓

exit

```



\---



\# 37. Configuration reload



Команда:



```bash

hermes -s reload

```



должна:



1\. перечитать YAML;

2\. проверить configuration;

3\. построить новый effective configuration;

4\. применить изменения;

5\. сохранить старую configuration при ошибке.



При invalid configuration:



```text

reload failed

running configuration unchanged

```



\---



\# 38. Filesystem layout



Linux:



```text

/etc/hermes/

├── hermes.yaml

└── secrets/

&#x20;   └── vault



/var/lib/hermes/

├── hermes.db

└── state/



/var/log/hermes/

└── ...



/run/hermes/

└── ...

```



`hermes.yaml` является optional.



\---



\# 39. systemd



Hermes поставляется как systemd service.



Service работает от отдельного пользователя:



```text

User=hermes

Group=hermes

```



Не запускать Hermes от root.



Root необходим только для deployment и системных операций.



\---



\# 40. systemd hardening



Использовать доступные systemd security features:



```text

NoNewPrivileges

ProtectSystem

ProtectHome

PrivateTmp

```



и дополнительные ограничения по мере проверки совместимости.



\---



\# 41. Permissions



Пример:



```text

/etc/hermes

&#x20;   root:hermes



/var/lib/hermes

&#x20;   hermes:hermes



/var/log/hermes

&#x20;   hermes:hermes



/run/hermes

&#x20;   hermes:hermes

```



Secret vault должен иметь максимально строгие permissions.



\---



\# 42. Ansible deployment



Ansible является официальным способом deployment Hermes на Linux.



```bash

ansible-playbook -i inventory/production.yml hermes.yml

```



Ansible выполняет:



1\. создание пользователя `hermes`;

2\. создание directories;

3\. установку Hermes;

4\. установку systemd unit;

5\. deployment configuration;

6\. deployment secrets;

7\. установку permissions;

8\. enable/start service;

9\. upgrades.



\---



\# 43. Ansible Vault



Deployment secrets, хранящиеся в Ansible repository, не должны находиться plaintext.



Использовать Ansible Vault.



Разделение:



```text

Ansible Vault

&#x20;    ↓

deployment-time secrets



Hermes Secret Store

&#x20;    ↓

runtime secrets

```



\---



\# 44. Docker



Docker \*\*не входит в первую версию Hermes\*\*.



Не создавать на первоначальном этапе:



```text

Dockerfile

compose.yaml

entrypoint

Docker-specific config

```



Архитектура не должна препятствовать добавлению Docker позже.



\---



\# 45. Windows



Windows support рассматривается как будущий deployment layer.



Предполагаемый вариант:



```text

Windows

&#x20;  ↓

Docker Desktop

&#x20;  ↓

Hermes

```



Пользователь должен управлять Hermes через привычный CLI:



```powershell

hermes status

hermes logs

hermes reload

```



а не напрямую через Docker CLI.



Windows wrapper в будущем будет преобразовывать команды Hermes в Docker operations.



Core Hermes при этом не должен знать о Docker.



\---



\# 46. Security model



Основные требования:



\* Hermes не работает от root;

\* secrets не находятся в обычном YAML;

\* operational secrets encrypted;

\* password verifiers используют Argon2id;

\* secrets не выводятся CLI;

\* secrets не пишутся в logs;

\* strict filesystem permissions;

\* atomic vault writes;

\* безопасные temporary files;

\* configuration validation перед reload;

\* invalid reload не изменяет runtime state;

\* plugins получают только необходимые capabilities.



\---



\# 47. Threat model



Hermes должен защищать secrets от:



\* случайного доступа другого локального пользователя;

\* утечки `hermes.yaml`;

\* кражи vault-файла;

\* backup leakage;

\* случайного попадания credentials в logs;

\* неправильных filesystem permissions.



Полный контроль от root на работающей системе не является целью.



Root считается доверенным системным администратором.



\---



\# 48. Default installation



Чистая установка может выглядеть так:



```text

/etc/hermes/

```



без `hermes.yaml`.



После установки:



```bash

hermes -t

```



должно работать на built-in defaults.



Для подключения FunPay:



```bash

hermes secrets set funpay.golden\_key

```



Проверка:



```bash

hermes account auth test

```



Запуск:



```bash

systemctl enable --now hermes

```



Проверка:



```bash

hermes status

```



\---



\# 49. Design principles



Hermes должен придерживаться следующих принципов.



\### Simple by default



Минимальная конфигурация.



\### Secure by default



Секреты не лежат plaintext в configuration.



\### Extensible by design



Вся дополнительная функциональность реализуется через plugins.



\### Low resource usage



Работа на 1 CPU / 768 MB RAM.



\### Unix philosophy



CLI, systemd, filesystem hierarchy, predictable exit codes, signals.



\### Human-oriented configuration



Пользователь описывает намерение, а не внутреннюю реализацию.



\### Safe reload



Невалидная configuration никогда не ломает работающий экземпляр.



\---



\# 50. Итоговая архитектура



```text

&#x20;                        ┌──────────────────────┐

&#x20;                        │        Hermes        │

&#x20;                        │        Core          │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;      ┌────────────────────────────┼───────────────────────────┐

&#x20;      │                            │                           │

&#x20;      ▼                            ▼                           ▼

&#x20;Configuration                  Secrets                       CLI

&#x20;      │                            │                           │

&#x20;hermes.yaml                 Secret Store                Nginx-style

&#x20;      │                            │

&#x20;      │                ┌───────────┴───────────┐

&#x20;      │                │                       │

&#x20;      │             Argon2id               Encryption

&#x20;      │             passwords              operational

&#x20;      │                                      secrets

&#x20;      │

&#x20;      ▼

Effective Configuration

&#x20;      │

&#x20;┌─────┼──────────┬───────────┬──────────────┐

&#x20;▼     ▼          ▼           ▼              ▼

FunPay Scheduler Storage    Networking     Plugins

&#x20;│                  │           │              │

&#x20;│             ┌────┴────┐      │        ┌─────┼─────┐

&#x20;│             │         │      │        ▼     ▼     ▼

&#x20;│           SQLite   PostgreSQL Proxy    AI    TG   Web

&#x20;│

&#x20;├── Orders

&#x20;├── Lots

&#x20;├── Auto-bump

&#x20;└── Delivery

```



\---



\# 51. V1 scope



Первая версия Hermes должна сосредоточиться на:



```text

Core

├── FunPay

├── authentication

├── orders

├── lots

├── auto-bump

├── delivery

├── async HTTP

├── connection pool

├── proxy

├── rate limiter

├── SQLite

├── optional PostgreSQL

├── YAML configuration

├── built-in defaults

├── configuration validation

├── configuration reload

├── hierarchical logging

├── Secret Store

├── CLI

├── systemd

├── graceful shutdown

└── plugin API

```



Не включать в V1:



```text

Docker

Windows wrapper

Telegram

Discord

Web panel

AI

Account rental

```



Они должны добавляться после стабилизации Core.



\---



\# 52. Главная концепция Hermes



Hermes должен быть небольшим, автономным и production-oriented Unix daemon:



```text

&#x20;       ┌─────────────────────────┐

&#x20;       │        Hermes            │

&#x20;       │                         │

&#x20;       │  works out of the box   │

&#x20;       │  without hermes.yaml    │

&#x20;       └────────────┬────────────┘

&#x20;                    │

&#x20;            user configuration

&#x20;                    │

&#x20;                    ▼

&#x20;               hermes.yaml

&#x20;                    │

&#x20;                    ▼

&#x20;               overrides

```



Пользователь может начать с:



```bash

hermes

```



и практически ничего не знать о внутренней архитектуре.



По мере необходимости он получает:



```text

CLI

&#x20;↓

YAML

&#x20;↓

Secrets

&#x20;↓

Proxy

&#x20;↓

PostgreSQL

&#x20;↓

Plugins

&#x20;↓

GUI

```



При этом базовый Hermes остаётся маленьким и способен работать на \*\*1 CPU / 768 MB RAM\*\*.



\*\*Ключевой UX-принцип:\*\*



> Hermes должен быть простым для пользователя, но не примитивным внутри.



