# bot_repo


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
