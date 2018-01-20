from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse

from PIL import Image
from io import BytesIO

import requests
import os
import time


parser = reqparse.RequestParser()
parser.add_argument('content', type=str, help='Content Image URL')
parser.add_argument('style', type=str, help='Style Image URL')
parser.add_argument('num_iterations', type=int, help='Number of iterations')
parser.add_argument('maxsize', type=int, help='Max size of image')


app = Flask(__name__)
api = Api(app)


def resize_img(img, maxsize):
    # w, h = img.size
    # size = w//2, h//2
    size = maxsize, maxsize
    img.thumbnail(size, Image.ANTIALIAS)
    return img.size


def write_image(url, filename, maxsize):
    req = requests.get(url)
    image, ext = req.headers['Content-Type'].split('/')
    assert(image == 'image')
    
    img = Image.open(BytesIO(req.content)) 

    w, h = resize_img(img, maxsize)

    filename = filename + '_' + str(w) + 'x' + str(h) + '.' + ext
    img.save(filename)
    # raise Exception()

    # with open(filename, 'wb') as f:
        # f.write(req.content)

    print('Written ' + filename + '.. ')
    return filename


def run_neural_style(content_filename, 
                     style_filename, 
                     num_iterations):
    
    shape_ext = content_filename.split('_')[1]
    output_filename = 'output/output' + str(num_iterations) + '_' + shape_ext 

    cmd = 'python ./neural-style/neural_style.py --content ' + content_filename +\
                                        ' --styles ' + style_filename   +\
                                        ' --output ' + output_filename  +\
                                        ' --network neural-style/imagenet-vgg-verydeep-19.mat' +\
                                        ' --iterations ' + str(num_iterations)
    print("Running " + cmd)
    start = time.time()
    ret = os.system(cmd)
    elapsed = int(time.time()-start)
    print('Return Value = ' + str(ret))
    print('Elapsed = ' + str(elapsed))
    new_filename = output_filename.split('.')[0] + '_' + str(elapsed) + 's' + output_filename.split('.')[1]
    os.system('mv ' + output_filename + ' ' + new_filename)
    print('Created ' + new_filename)


class StyleTransfer(Resource):
    def post(self):
        args = parser.parse_args()
        content_url = args['content']
        style_url = args['style']
        num_iterations = args['num_iterations']
        maxsize = args['maxsize']

        try:
            content_filename = write_image(content_url, 'content/content', maxsize)
            style_filename   = write_image(style_url, 'style/style', maxsize)
        except (requests.exceptions.MissingSchema, Exception) as e:
            print(str(e))
            return 'error'

        run_neural_style(content_filename, 
                         style_filename,
                         num_iterations)

        result_url = 'todo'
        
        return {'result_url': result_url}

api.add_resource(StyleTransfer, '/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
