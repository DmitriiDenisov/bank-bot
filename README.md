# bank-bot


## How to Run whole project. Structure of whole project:

```
.
├── .env                  
├── docker-compose.yml           # Download it from [Pastebin](https://pastebin.com/D5uggnYc)                 
├── bank-bot                     # this repo
├── bank-bot-db                  # [data base repo](https://github.com/DmitriiDenisov/bank-bot-db)
├── cpp-service-bank-bot         # [cpp-service repo](https://github.com/DmitriiDenisov/cpp-service-bank-bot)         
├── currency-service-bank-bot   # [currency-service repo](https://github.com/DmitriiDenisov/currency-service-bank-bot)
└── node-apidemo                 # [node-apidemo repo](https://github.com/DmitriiDenisov/node-apidemo) 
```

1. Download docker-compose.yml file from [Pastebin](https://pastebin.com/D5uggnYc) 

2. Create `.env` file. You can download it from releases in this repo, it has only hidden file .env inside
It should look like this:
```
# Config for curr-serv
TOKEN=33c35846ca3537 # Token for https://fixer.io/
PORT=5004 # Port for curr-serv

# Config for front + rabbitmq workers (worker_own_transfer and worker_transactions)
HOST_RABBIT=localhost # Host for RabbitMq (if same server => localhost)
PORT_RABBIT=5672 # Port for Rabbit
USER_RABBIT=publisher # user name for RabbitMQ
PASSWORD_RABBIT=qwerty # password for RabbitMQ
HOST_CURR_SERV=localhost # host of curr-serv
PORT_CURR_SERV=5004 # port of curr-serv
URL_DB=postgresql://dmitryhse:mypassword@localhost:5432/bank_bot_db # DB URL and credentials
KEY_HS256=bcae2a8c35a0de3353977ed7af0de10731f62500e4588ca238 # Secret KEY which is used in `token_auth` method for decoding of JWT key
```
3. Run all services: `docker-compose up -d`
4. (optional) if you want multiple docker containers: 
`docker-compose up -d --scale worker-transaction=3 --scale worker-own-transfer=2`

## Services that are up on server:

1. AirFlow: port 8080 (**does not** automatically restarts once server is restarted)
2. RabbitMQ: port 15672 (automatically restarts once server is restarted). If you don't see queues check that you have access to virtual host. In order to do that in UI go to 'Admin' and check if you have access to virtual hosts
3. Jenkins: port 9090 (automatically restarts once server is restarted)
4. GitLab: port 9111 (automatically restarts once server is restarted, It may take some time or require additional computation power as developer recommends at least 4GB of RAM)


## How to Run only this repo (Flask and main api):
Add to credentials folder files:
1. Create file .env (see above)
2. In `constants.py` by default HS256 algorithm is used, if you want to use RS256 then you need to run `python3 crypto_utils/generate_keys_RS256.py`
3. `python3 main.py`

## Run workers (to own_transaction and transactions queues in RabbitMQ):

They will automatically run after command `docker-compose up -d`

If you have problem with pulling docker image then you can build it locally: 

`docker build -t worker_base -f Dockerfile_base_worker .`


## Detailed review of Repo:

### credentials: private_key and public_key only when you are using RS256 method for encoding
Can be generated by calling `python3 crypto_utils/generate_keys_RS256.py`

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
`generate_keys_RS256.py` generates public and private keys and saves them to `credentials/private_key_RS256` and `credentials/public_key_RS256`
`generate_key_HS256.py` generates and prints HS256 key, you need to put it into .env file
`generate_token.py` generates token and returns it using jwt library. Check also examples of how jwt works in `jwt_ex` folder
`hash_password.py` has two functions for get hash of password and check that password is legitimate
This script uses bcrypt library which adds salt (randomly generated string) to password so from this for equal passwords we obtain different hashes
Also Libraries like bcrypt are smart enough to store the salt IN the resulting string so that developers don’t need to do the extra work."
https://hackernoon.com/hashing-passwords-in-python-bcrypt-tutorial-with-examples-77dh36ef

 file `api_queries.py` - main file which uses everything else. In order to run: `python api_queries.py`

More about electronic digital signature [RUS](https://www.youtube.com/watch?v=Y5G7hg9CGIc)

### Trello 
https://trello.com/b/kuk4mthV/bank-bot
