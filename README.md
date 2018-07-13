# STX_BRO_BOT

## Deployment guide to Debian 9+ server.

#### Update system.
    - apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y
    - apt-get remove --purge unscd
    - userdel -r debian

#### Install python last version , dev tools, pip3, virtualenv
	- nano /etc/apt/sources.list
	  #### # Test repo for python3+
	  deb http://ftp.de.debian.org/debian testing main
	-     # echo 'APT::Default-Release "stable";' | sudo tee -a /etc/apt/apt.conf.d/00local
	- sudo apt-get update
	- sudo apt-get -t testing install python3.6
	- python3 -V
	
	- sudo apt-get install python3-dev python3-pip
	- sudo pip3 install virtualenv
	  (make project dir; virtualenv venv; source /bin/activate)
	- sudo apt-get install git
	- sudo apt-get install man-db 

	Install nodejs
	- su root
	- apt-get install curl
	- curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
	- sudo apt-get install -y nodejs
	- sudo apt-get install build-essential
	- sudo apt-get update
	- sudo apt-get install build-essential libssl-dev
	

#### Install smartholdem rpc lib.
	- http://api.smartholdem.io/#rpc-daemon
	- add to autorun https://community.smartholdem.io/topic/21/chastye-voprosy-po-yspolzovanyiu-full-node-level-a/2

#### Git clone repo with project.
    - git clone ...

#### Gen priv key.
	- sudo apt-get install openssl
	- openssl genrsa -out webhook_pkey.pem 2048

#### Gen cert.
	- openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem

#### Make venv.
	- sudo apt-get install python3-pip python3-dev
	- sudo pip3 install virtualenv
	- virtualenv BRObot
	- cd BRObot/
	- source bin/activate
	- pip3 install -r requirements.txt

#### Current default time zone: 'Etc/UTC'
Local time is now:      Tue Apr 17 11:36:21 UTC 2018.
Universal Time is now:  Tue Apr 17 11:36:21 UTC 2018.
Run 'dpkg-reconfigure tzdata' if you wish to change it.

#### Insalling mongodb.
	- sudo apt-get install dirmngr
	- sudo apt-get install mongodb
	- sudo systemctl start mongodb
	- sudo systemctl enable mongodb

#### Installing gettext and tools.
	- apt-get install gettext
	- msgfmt -o <output.mo file> <base.po file>

#### Installing and setting supervisord.
	- sudo apt-get install supervisor
	- add conf file in /etc/supervisor/conf.d/...
	- sudo supervisorctl reread
	- sudo supervisorctl update
	

### Supervisor app conf example.
```
[program:stx_bro_bot]
command=/home/brobot/BRObot/venv/bin/python3 /home/brobot/BRObot/STX_BRO_BOT/stx_bro.py
stdout_logfile=/var/log/stx_bro_bot.log
autostart=true
autorestart=true
user=brobot
stopsignal=KILL
numprocs=1
```

#### Set smartholdemrpc in pm2 
	- cd smartholdemrpc
	- npm install pm2 -g 
	- pm2 start server.js
	- pm2 startup (exec output command)
	
#### Install memcached.
    - sudo apt-get -y install memcached
    - sudo systemctl enable memcached
