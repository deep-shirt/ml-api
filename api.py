from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_api import status
from flask_cors import CORS

from PIL import Image
from io import BytesIO

import google.cloud.storage
from google.cloud.storage.blob import Blob


import requests
import os
import time

import datetime
import threading



app = Flask(__name__)
CORS(app)
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


def fast_style_transfer(content_filename, checkpoint):
    shape_ext = content_filename.split('_')[1]
    output_filename = 'output/FAST_output_' + shape_ext 

    cmd = 'python ./fast-style-transfer/evaluate.py --checkpoint ' + checkpoint +\
          ' --in-path ' + content_filename +\
          ' --out-path ' + output_filename 

    return run(cmd, output_filename)


def neural_style(content_filename, style_filename, num_iterations):
    shape_ext = content_filename.split('_')[1]
    output_filename = 'output/output' + str(num_iterations) + '_' + shape_ext 

    cmd = 'python ./neural-style/neural_style.py --content ' + content_filename +\
                                        ' --styles ' + style_filename   +\
                                        ' --output ' + output_filename  +\
                                        ' --network neural-style/imagenet-vgg-verydeep-19.mat' +\
                                        ' --iterations ' + str(num_iterations)
    return run(cmd, output_filename)


def store_to_firebase(output_file):
    blob = Blob(output_file, bucket)
    blob.upload_from_filename(filename=output_file)
    url = blob.generate_signed_url(datetime.timedelta(days=1000))
    print(url)
    return url 


def run(cmd, output_filename):

    lock.acquire() 

    print("Running " + cmd)
    start = time.time()
    ret = os.system(cmd)
    elapsed = int(time.time()-start)
    print('Return Value = ' + str(ret))
    print('Elapsed = ' + str(elapsed))
    result_url = store_to_firebase(output_filename)

    lock.release()

    return result_url


class NeuralArt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, help='Content Image URL')
        parser.add_argument('style', type=str, help='Style Image URL')
        parser.add_argument('num_iterations', type=int, help='Number of iterations')
        parser.add_argument('maxsize', type=int, help='Max size of image')
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
            return 'error', status.HTTP_400_BAD_REQUEST

        result_url = neural_style(content_filename, style_filename, num_iterations)

        return {'result_url': result_url}


class FastStyleTransfer(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, help='Content Image URL')
        parser.add_argument('checkpoint', type=str, help='Path to the checkpoint file')
        parser.add_argument('maxsize', type=int, help='Max size of image')
        args = parser.parse_args()
        
        if not args['checkpoint'].endswith('.ckpt'):
            return 'error - style file must end with .ckpt', status.HTTP_400_BAD_REQUEST

        content_url = args['content']
        checkpoint = 'fast-style-transfer/checkpoints/' + args['checkpoint']
        maxsize = args['maxsize']

        print(args)

        try:
            content_filename = write_image(content_url, 'content/content', maxsize)
        except (requests.exceptions.MissingSchema, Exception) as e:
            print(str(e))
            return 'error', status.HTTP_400_BAD_REQUEST

        result_url = fast_style_transfer(content_filename, checkpoint)
        
        return {'result_url': result_url}

api.add_resource(NeuralArt, '/neural-art')
api.add_resource(FastStyleTransfer, '/fast-style-transfer')

client = google.cloud.storage.Client(project='deep-shirt')

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate('/home/kvnrpb/deep-shirt-firebase-adminsdk.json')
firebase_admin.initialize_app(cred, { 'storageBucket': 'deep-shirt.appspot.com' })

bucket = storage.bucket()

lock = threading.Lock()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    path = '/home/kvnrpb/letsencrypt/certs/live/deep.deep-shirt.com/'
    # app.run(host='0.0.0.0', port=8080, debug=True, ssl_context=(path + 'fullchain.pem', path + 'privkey.pem'))
