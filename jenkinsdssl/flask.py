from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

def _webhook():
    return 'Hoi, imma webhook'

def init(token: str):
    app.route(f'/{token}', _webhook)


def run():
    app.run()
