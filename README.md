# bank-bot


## How to Run whole project. Structure of whole project:

```
.
├── .env                  
├── docker-compose.yml           # Download it from [Pastebin](https://pastebin.com/D5uggnYc)                 
├── bank-bot                     # this repo
├── bank-bot-db                  # [data base repo](https://github.com/DmitriiDenisov/bank-bot-db)
├── cpp-service-bank-bot         # [cpp-service repo](https://github.com/DmitriiDenisov/cpp-service-bank-bot)         
├── currency-service-bank-bot.   # [currency-service repo](https://github.com/DmitriiDenisov/currency-service-bank-bot)
└── node-apidemo                 # [node-apidemo repo](https://github.com/DmitriiDenisov/node-apidemo) 
```

1. Download docker-compose.yml file from [Pastebin](https://pastebin.com/D5uggnYc) 

2. Create `.env` file. You can download it from releases in this repo, it has only hidden file .env inside
It should look like this:
```
TOKEN=abcd # Token for currency-service from https://fixer.io/
PORT=5004 # Port for currency-service
HOST_RABBIT=localhost # Host for RabbitMq (if same server => localhost)
USER_RABBIT=publisher # user name for RabbitMQ
PASSWORD_RABBIT=1234 # password for RabbitMQ
URL_DB=postgresql://username:mypassword@localhost:5432/bank_bot_db # URL for DB
KEY_HS256=1353977sfsde10f731f625004e4588ca238 # Secret KEY which is used in `token_auth` method for decoding of JWT key
```
3. Run all services: `docker-compose up -d`
4. (optional) if you want multiple docker containers: 
`docker-compose up -d --scale worker-transaction=3 --scale worker-own-transfer=2`

## Services that are up on server:

1. AirFlow: port 8080 (**does not** automaticlly restarts once server is restarted)
2. RabbitMQ: port 15672 (automaticlly restarts once server is restarted)
3. Jenkins: port 9090 (automaticlly restarts once server is restarted)

## How to Run only this repo (Flask and main api):
Add to credentials folder files:
1. `credentials_db` - URL for Postgres, for example `postgresql://user:password@35.213.279.96:5432/bank_bot_db`
2. `private_key_HS256` - see `constants.py`, it will be used in `token_auth` method for decoding of JWT key
3. `private_key_RS256` - see `constants.py`, it will be used in `token_auth` method for decoding of JWT key
4. `public_key_RS256` - see `constants.py`, it will be used in `token_auth` method for decoding of JWT key
5. `python3 api_queries.py`

## Run workers (to own_transaction and transactions queues in RabbitMQ):
Add to credentials folder files:
`credentials_db` - URL for Postgres, for example `postgresql://user:password@35.213.279.96:5432/bank_bot_db`

To run Worker connected to own_transaction queue:
`bash run_worker_own_transfer.sh`

To run Worker connected to transactions queue:
`bash run_worker_transaction.sh`

If you have problem with pulling docker image then you can build it locally: 

`docker build -t worker_base -f Dockerfile_base_worker .`


## Detailed review of Repo:

### credentials: folder which should consist of private_key, public_key, credentials_db which are not presented in repo
credentials_db should have only one row of text which is url to the DB, for example postgresql://username:mypass@34.71.210.249:5432/bank_bot_db
Files private_key and public_key can be generated by calling `python crypto_utils/generate_keys.py`

### jwt_ex: folder with an example of how JWT works. 
JWT creates a Token. Token consists of header, payload and signature. Payload and header are not encrypted meanwhile signature is encrypted with private_key.
In oder to see how it works go to jwt.io 

### flask_ex
Folder has one simple example of hello_world with Flask library

### models
For each table SQLAlchemy requires a description of a table. Detailed examples and descriptions of what is relationship, ForeignKey you can find in `bank-bot-db` repo

### utils 
Utils folder consists of:
`add_user.py` - to add_user to DB with SQLAlchemy
`base.py` - creation of session
`constants.py` - all constants
`schemas.py` - schemas for Marshmallow library for automatic check of parameters fed to API
`token_auth.py` - decorator for for API which checks that token is legitimate 

### crypto_utils: 
`generate_keys.py` generates public and private keys and saves them to `credentials/private_key` and `credentials/public_key`
`generate_token.py` generates token and returns it using jwt library. Check also examples of how jwt works in `jwt_ex` folder
`hash_password.py` has two functions for get hash of password and check that password is legitimate
This script uses bcrypt library which adds salt (randomly generated string) to password so from this for equal passwords we obtain different hashes
Also Libraries like bcrypt are smart enough to store the salt IN the resulting string so that developers don’t need to do the extra work."
https://hackernoon.com/hashing-passwords-in-python-bcrypt-tutorial-with-examples-77dh36ef

 file `api_queries.py` - main file which uses everything else. In order to run: `python api_queries.py`

About ЭЦП:
https://www.youtube.com/watch?v=Y5G7hg9CGIc

