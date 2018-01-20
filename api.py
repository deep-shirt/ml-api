from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse

import requests
import os

parser = reqparse.RequestParser()
parser.add_argument('content', type=str, help='Content Image URL')
parser.add_argument('style', type=str, help='Style Image URL')


app = Flask(__name__)
api = Api(app)

def write_image(url, filename):
    req = requests.get(url)
    image, ext = req.headers['Content-Type'].split('/')
    assert(image == 'image')
    filename = filename+'.'+ext
    with open(filename, 'wb') as f:
        f.write(req.content)
    print('Written ' + filename + '.. ')
    return filename

def run_neural_style(content_filename, style_filename, output_filename='output.jpeg'):
    cmd = 'python ./neural-style/neural_style.py --content ' + content_filename +\
                                        '--styles ' + style_filename   +\
                                        '--output ' + output_filename 
    ret = os.system(cmd)
    print('Return Value = ' + str(ret))


class StyleTransfer(Resource):
    def post(self):
        args = parser.parse_args()
        content_url = args['content']
        style_url = args['style']

        try:
            content_filename = write_image(content_url, 'content')
            style_filename   = write_image(style_url, 'style')
        except requests.exceptions.MissingSchema:
            return 'error'

        output_filename = 'output.jpeg'

        run_neural_style(content_filename, style_filename)

        result_url = 'todo'
        
        return {'result_url': result_url}

api.add_resource(StyleTransfer, '/')


if __name__ == '__main__':
    app.run(debug=True)
