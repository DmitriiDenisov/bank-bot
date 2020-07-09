from flask import Flask, jsonify, request, abort
app = Flask(__name__)


# Просто принт Hello world, без Celery
@app.route('/home', methods=['GET'])
def hello_world():
    return jsonify({'Hello, World!': 4})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',
            port=5001)  # host позволяет дать глобальный доступ для устройств в сети. Адрес в общем виде: http://<ip_addess>:5000. http://172.20.10.2:5000/
