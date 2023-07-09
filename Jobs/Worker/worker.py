import redis
import json
import requests
from config import Config

'''
backend2worker queue message structure
{
    eventId: <eventId>,
    userId: <userId>,
    model: <model>,
    data: {
        endpoint: <str>
        ...
    }
}


worker2backend queue message structure

- starting process message structure
{
    eventId: <eventId>,
    type: "start"
}


- end process message structure
{
    eventId: <eventId>
    type: "finish"
    success: [True|False]
    message: Message from model describing success
}
'''


'''
data field specification for Alis endpoints

- /random_images
    Backend must provide the resource names for the generated files
{
    'endpoint': '/random_images'
    'images_names': [
        <filename_1>,
        <filename_2>,
    ]
}

- /run_projection
{
    'endpoint': '/run_projection'
    'image_id': <image_id>
}

- /run_pca
{
    'endpoint': '/run_projection'
    "vector_id": <pkl_vector>,
    "latent_edits": [
        {
            "principal_component_number": <component>,
            "start_layer": <layer_0>,
            "end_layer": <layer_1>,
            "lower_coeff_limit": <coeff_0>,
            "upper_coeff_limit": <coeff_1>
        },
        ... 
    ]
}


'''
def alisApi(data):
    if data['data']['endpoint'] == '/random_images':
        jsonData = {
            'images_names': data['data']['images_names']
        }
        response = requests.get(f"http://{Config.ALIS_ROUTE}:{Config.ALIS_PORT}/random_images", json=jsonData)
        return json.loads(response.content)
    
    elif data['data']['endpoint'] == '/run_projection':
        params = {
            'image_id': data['data']['image_id']
        }
        response = requests.get(f"http://{Config.ALIS_ROUTE}:{Config.ALIS_PORT}/run_projection", params=params)
        return json.loads(response.content)

    elif data['data']['endpoint'] == '/run_pca':
        jsonData = {
            'vector_id': data['data']['vector_id'],
            'latent_edits': data['data']['latent_edits']
        }
        response = requests.post(f"http://{Config.ALIS_ROUTE}:{Config.ALIS_PORT}/run_pca", json=jsonData)
        return json.loads(response.content)

    else:
        raise Exception(f"Unknown endpoint {data['data']['endpoint']} for Alis model")


def main():
    r = redis.Redis(host=Config.REDIS_ROUTE, port=Config.REDIS_PORT)

    pubsub = r.pubsub()
    pubsub.subscribe('backend2worker_queue')

    print('Starting message loop')
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])

            eventId = data['eventId']
            userId = data['userId']

            # acknowledge message received and starting process
            r.publish('worker2backend_queue', json.dumps({
                'eventId': eventId,
                'userId': userId,
                'type': 'start'
            }))
            
            # api call
            if data['model'] == 'alis':
                response = alisApi(data)
            else:
                raise NotImplementedError('Only alis model currently available')

            # inform process ended
            r.publish('worker2backend_queue', json.dumps({
                'eventId': eventId,
                'userId': userId,
                'type': 'finish',
                'success': response['success'],
                'message': response['message']
            }))


if __name__ == '__main__':
    main()
