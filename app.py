from flask import Flask, request, jsonify
from processimages import processImages
import os
import json

app = Flask(__name__)

app_port = os.getenv('APP_PORT', '5000')

@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'jobqueu',
        'topic': 'jobs',
        'route': 'api/predImage'
    }]
    print('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    return jsonify(subscriptions)

@app.route('/api/predImage', methods=['POST'])
def orders_subscriber():
     data = request.json
     folder = data['folder']
     jobid = str(data['id'])
     return processImages(folder,jobid)  # return a response


###Original Flask Prediction
# @app.route('/api/predImage', methods=['POST'])
# def post_example():
#     data = request.json
#     folder = data['folder']
#     jobid = str(data['id'])


#     return processImages(folder,jobid)  # return a response

app.run(port=app_port)

# if __name__ == "__main__":
#     # Please do not set debug=True in production
#     app.run(host="0.0.0.0", port=app_port, debug=False)
    