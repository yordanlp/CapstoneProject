import os
import sys 
alis_path = os.path.abspath('./alis')
sys.path.append(alis_path)

from flask import Flask, jsonify, abort, request
from werkzeug.utils import secure_filename
import secrets

from Alis import AlisWrapper

from config import DevelopmentConfig
import PIL
import pickle as pkl

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            abort(500, 'Missping file parameter in rquest')

        file = request.files['file']
        if file is None:
            return jsonify({
                'success': False,
                'message': 'You must upload a file'
                })
        
        random_hex = secrets.token_hex(8)
        filename = random_hex + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'image_id': filename
        })
    except PermissionError:
        return jsonify({
            'success': False,
            'message': 'Error: permission denied'
        })


@app.route('/random_images', methods=['GET'])
def random_images():
    try:
        image_count = int(request.args.get('image_count'))
    except:
        return jsonify({
            'success' : False,
            'message' : 'Incorrect data format'
        })
    
    if image_count > 10:
        return jsonify({
            'success': False,
            'message': 'You can generate up to 10 images'   
        })
    
    w_list, img_list = AlisWrapper.get_random_images(n_samples=image_count)
    img_names, w_names = [], []
    for i in range(image_count):
        filename = secrets.token_hex(8)
        PIL.Image.fromarray(img_list[i], 'RGB').save(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.png'))
        with open(os.path.join(app.config['OUTPUT_PROJECTION'], filename + '.pkl'), 'wb') as f:
            pkl.dump(w_list[i], f)
        img_names.append(filename + '.png')
        w_names.append(filename + '.pkl')        
    
    return jsonify({
        'images' : img_names,
        'latents' : w_names
    })

@app.route('/run_projection', methods=['GET'])
def run_projection():
    image_id = request.args.get('image_id')
    if image_id is None:
        abort(404, 'File not found')

    file_path = f"{app.config['UPLOAD_FOLDER']}/{image_id}"

    if not os.path.exists(file_path):
        abort(404, 'File not found')

    AlisWrapper.run_projection_on_file(
        file_path=file_path,
        out_folder=app.config['OUTPUT_PROJECTION'],
        save_video=False,
        num_steps=2000,
        verbose=True
    )

    file_name = image_id.split('.')[0]
    return jsonify({
        'success' : True,
        'message': 'Projection run successfully',
        'vector_id': f"{file_name}.pkl"
    })
        
@app.route('/run_pca', methods=['POST'])
def run_pca():
    params = request.get_json()
    vector_id = params['vector_id']
    latent_edits = [( i['principal_component_number'], (i['start_layer'], i['end_layer']), (i['lower_coeff_limit'], i['upper_coeff_limit']) ) for i in params['latent_edits']]
    if vector_id is None:
        abort(404, 'Vector not found')

    vector_path = f"{app.config['OUTPUT_PROJECTION']}/{vector_id}"

    if not os.path.exists(vector_path):
        abort(404, 'Vector not found')

    AlisWrapper.run_pca_moving_on_file(
        file_path = vector_path,
        out_folder = app.config['OUTPUT_PCA'], 
        interpolation_steps = 1,
        latent_edits = latent_edits
    )

    return jsonify({
        'success' : True,
        'message': 'PCA run successfully'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
