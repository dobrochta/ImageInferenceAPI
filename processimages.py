from azure.storage.blob import BlobServiceClient
import os, glob
import sys
import json  
import requests
import base64
import io
import pandas as pd
from datetime import datetime
from flask import jsonify

def compileOutput(predictions):
    df = pd.DataFrame(predictions, columns =['Image', 'x','y','width','height','confidence','class'])
    partial = df.to_csv(index=False, encoding="utf-8")
    return partial

def makeInference(container_client):
    local_inference_server_address = "http://roboinference--tn0mzgl.victoriouspond-e52d83fc.eastus.azurecontainerapps.io/"
    version_number = 10
    project_id = "small-test-set/"
    predictions=[]
    for images in container_client.list_blobs():
        blob_client = container_client.get_blob_client(images.name)
        blob_content = blob_client.download_blob().content_as_bytes()
        base64_content = base64.b64encode(blob_content)      
        im_b64 = base64_content.decode('utf-8')
        payload = json.dumps({"image": im_b64})

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        params = {
            'api_key': 'USD0YyB5LFKUtdzAbF3I',
        }
        #Request Against Inference
        response = requests.post(local_inference_server_address+project_id+str(version_number), params=params, headers=headers, data=im_b64)
        
        try:
            data = response.json()
        except Exception as e:
            print(e)
            pass
        try:
            if len(data['predictions'])>0:
                for pred in data['predictions']:
                    val_list=[]
                    val_list.append(images.name)
                    val_list.append(pred['x'])
                    val_list.append(pred['y'])
                    val_list.append(pred['width'])
                    val_list.append(pred['height'])
                    val_list.append(pred['confidence'])
                    val_list.append(pred['class'])
                    predictions.append(val_list)
        except Exception as e:
            print(e)
            pass
    return predictions

def processImages(folder,id):
    #Define Blob Connection Variables
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=kcimachinelear2785621038;AccountKey=D7IXOEE8Z+uzujBZhrXmw7ISPUvtbrspGaD4blOxnff0vQTuH8bSANxAeZuuGlDfQ56G+FNqg4mG+ASt8VFIDw==;EndpointSuffix=core.windows.net'
    container_name = folder

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)
    
    predictions = makeInference(container_client)
    outputPreds= compileOutput(predictions)  
    inferenceRunTime=datetime.now()

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{id}_{inferenceRunTime}.csv") 
    blob_client.upload_blob(outputPreds,overwrite=True)

    return jsonify({"message": f"Jobid:{str(id)} Completed"})




# if __name__=='__main__':
#     processImages('inferencephotos','1234')