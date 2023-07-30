import os
import sys

from flask import Flask, jsonify, request
from config import DevelopmentConfig, ProductionConfig
from superresolution import run_superresolution


app = Flask(__name__)
app.config.from_object(ProductionConfig)

@app.route('/run_superresolution', methods=['GET'])
def run_projection():
    image_id = request.args.get('image_id')
    if image_id is None:
        return jsonify ({
            'success' : False,
            'message': 'File not found',
        })

    file_path = f"{app.config['UPLOAD_FOLDER']}/{image_id}"

    if not os.path.exists(file_path):
        return jsonify ({
            'success' : False,
            'message': 'File not found',
        })


    file_name, ext = image_id.split('.')

    if ext != 'png':
        return jsonify ({
            'success' : False,
            'message': 'Only png files supported for superresolution',
        })

    output_path = f"{app.config['UPSCALED_FOLDER']}/{file_name}.{ext}"

    run_superresolution(file_path, output_path)

    return jsonify({
        'success' : True,
        'message': 'Succesfully ran downscale + upscaled',
        'image_id': f"{file_name}.{ext}"
    })
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=app.config['DEBUG'])
