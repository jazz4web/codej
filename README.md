How to start it...

```
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone https://github.com/jazz4web/codej.git
$ cd codej
$ sudo apt install $(cat deploy/packages)
$ ln -s -T /usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf ~/workspace/codej/codej/captcha/picturize/Caladea-Regular.ttf
$ ln -s -T /usr/share/fonts/truetype/freefont/FreeSerif.ttf ~/workspace/codej/codej/captcha/picturize/FreeSerif.ttf
$ ln -s -T /usr/share/fonts/truetype/gentium/Gentium-R.ttf ~/workspace/codej/codej/captcha/picturize/Gentium-R.ttf
$ createdb codejdev
$ psql -d codejdev -f sql/db.sql
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade wheel
$ pip install -r requirements.txt
$ tar xvaf deploy/vendor.tar.gz -C codej/static
$ cp env_template .env
$ mkdir codej/static/generic
$ ln -s -T ~/workspace/codej/codej/static/vendor/bootstrap/fonts codej/static/generic/fonts
$ python insert_captchas.py -n 100
$ python create_root.py
$ python runserver.py
```
После выполнения всех команд можно обнаружить приложение в браузере по адресу
localhost:5000.

Дополнительную информацию о проекте можно найти на
[CodeJ](https://codej.ru/8ffdIqY4). Донат проекту можно перевести
[сюда](https://yoomoney.ru/to/410015590807463) - перевод на 5 рублей лучше,
чем никакого перевода, а ваш донат гарантирует, что я не закрою проект уже в
ближайшее время. И да, процесс развёртывания этого приложения на сервер тоже
могу продемонстрировать по запросу конечного пользователя, все контакты на
[главной](https://codej.ru/).
