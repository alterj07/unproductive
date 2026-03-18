from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort

app = Flask(__name__)
api = Api(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

if __name__ == '__main__':
    app.run(debug=True)