from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
import requests

parser = reqparse.RequestParser()
parser.add_argument('content', type=str, help='Content Image URL')
parser.add_argument('style', type=str, help='Style Image URL')


app = Flask(__name__)
api = Api(app)

def write_image(url, filename):
    req = requests.get(url)
    image, ext = req.headers['Content-Type'].split('/')
    assert(image == 'image')
    with open(filename+'.'+ext, 'wb') as f:
        f.write(req.content)


class StyleTransfer(Resource):
    def post(self):
        args = parser.parse_args()
        content_url = args['content']
        style_url = args['style']

        try:
            write_image(content_url, 'content')
            write_image(style_url, 'style')
        except requests.exceptions.MissingSchema:
            return 'error'


        # TODO run the tensorflow script

        result_url = 'todo'
        
        return {'result_url': result_url}

api.add_resource(StyleTransfer, '/')


if __name__ == '__main__':
    app.run(debug=True)
