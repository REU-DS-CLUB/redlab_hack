send: # отправить репозиторий на удаленный сервер
	scp -r ../redlab_hack root@80.87.104.231:

deploy: # поднять все сервисы на удаленном сервере
	ssh root@80.87.104.231 'cd redlabhack; docker compose build; docker compose up'

stop: # остановить все сервисы на удаленном сервере
	ssh root@80.87.104.231 'cd redlabhack; docker compose down'

clean: # очистить все на удаленн
	ssh root@80.87.104.231 'docker system prune -a -f'