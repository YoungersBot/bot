# bot_repo
#### START
- $ git clone git@github.com:YoungersBot/bot.git
- $ git checkout develop
- $ git checkout -b feature/<task_description>

###
#### GIT 
Ветка с задачей:
- $ git checkout develop
- $ git pull origin develop
- $ git checkout -b feature/<task_description>
- делаем задачу, добавляем изменения, коммитим и пушим:  
$ git add <file_name>  
$ git commit -m '<commit_message>'  
$ git push origin <your_branch_name>

###
#### DOCKER
- **$ docker-compose build**  
Собираем контейнеры.
- **$ docker-compose up -d**  
Запуск БД в фоновом режиме.  
- **$ docker-compose run --rm bot bash**  
Заходим внутрь контейнера.
- **$ docker-compose stop**  
Останавливаем контейнеры.



###
#### ЗАПУСК, ОТЛАДКА, ЛИНТЕРЫ
Все комманды внутри контейнера:

###
###### Bot (start / stop):
- $ python main.py
- $ Ctrl + C

###
###### Run file:
- $ python my_file.py

###
###### Lint (проверка кода):
Перед отправкой ПР нужно проверить и отформатировать свой код  
black и isort убрать --check для автоформата
- $ isort --check .
- $ black --check .
- $ flake8

###
###### Установка / удаление пакетов:
- $ poetry add <new_package>
- $ poetry remove <old_package>


###
#### GIT rebase
Если ветка develop ушла вперед пока вы делаете свою задачу  
и возникли конфликты:

- $ git commit -m '<commit_message>'  
- $ git pull --rebase origin develop
- $ git log   
проверяем историю все сделанные локально коммиты должны быть после 
последнего коммита в develop на GitHub:
- $ git push -f origin <your_branch_name>
=======

#### процесс
- клонируем репозиторий:  
$ git clone git@github.com:YoungersBot/bot.git  

- у себя локально переключаемся на ветку develop (в первый раз: git checkout -B develop):  
$ git checkout develop

- обновляем develop:  
$ git pull origin develop  

- создаем ветку с задачей:  
$ git checkout -B feature/<task_description>  

- делаем задачу, добавляем изменения, коммитим и пушим:  
$ git add <file_name>  
$ git commit -m '<commit_message>'  
$ git push origin <your_branch_name>

- заходим на github, делаем PR в __develop__, ждем code-review,
  после 2х аппрувов нажимаем Squash & Merge.
