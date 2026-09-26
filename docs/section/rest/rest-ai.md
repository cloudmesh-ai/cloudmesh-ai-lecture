# REST AI Services Example {#sec:restai-kmeans}

!!! info "Learning Objectives"
    After completing this chapter, you will be able to:
    * Implement an AI routine using scikit-learn and expose it via REST services.
    * Use OpenAPI 3.0 specifications to define AI service endpoints.
    * Manage data uploads and model state using job IDs in a RESTful API.
    * Handle multipart/form-data for training and prediction files.

## Overview

This chapter demonstrates a practical example of invoking a K-means Clustering routine in scikit-learn using an OpenAPI 3.0 specification.

The workflow consists of the following steps:

* Uploading a file containing data points to create the k-means clustering model.
* Invoking the scikit-learn KMeans module to fit the model.
* Uploading a file with points for prediction and receiving the predicted cluster IDs.
* Exposing auxiliary routines, such as retrieving cluster centers and labels, as REST services.

The REST services are created using FastAPI, which provides native support for OpenAPI 3.0.

## Project Files

The example files are available in the [GitHub repository](https://github.com/cloudmesh-community/book/tree/master/examples/rest/kmeans).

* OpenAPI 3 service definitions: [api.yaml](https://github.com/cloudmesh-community/book/blob/master/examples/rest/kmeans/api.yaml)
* FastAPI server: [server.py](https://github.com/cloudmesh-community/book/blob/master/examples/rest/kmeans/server.py)
* Kmeans service implementation: [kmeans.py](https://github.com/cloudmesh-community/book/blob/master/examples/rest/kmeans/kmeans.py)
* Python requirements: [requirements.txt](https://github.com/cloudmesh-community/book/blob/master/examples/rest/kmeans/requirements.txt)
* Example data: [model.csv](https://github.com/cloudmesh-community/book/blob/master/examples/rest/kmeans/model.csv) and [predict.csv](https://github.com/cloudmesh-community/book/blob/master/examples/rest/kmeans/predict.csv)

## Implementation

The following implementation provides a complete server including imports, global state, and the service logic for uploading data, fitting the model, and performing predictions.

```python
import os
import numpy as np
from sklearn.cluster import KMeans
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# Global state
INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"
inputs: Dict[int, str] = {}
inputs_r: Dict[str, int] = {}
models: Dict[int, Any] = {}
default_model_params = {"n_clusters": 8, "max_iter": 300}

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class FitRequest(BaseModel):
    job_id: int
    model_params: Dict[str, Any]

@app.post("/kmeans/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    in_file = os.path.join(INPUT_DIR, filename)
    
    if not os.path.exists(in_file):
        with open(in_file, "wb") as buffer:
            buffer.write(await file.read())

    if in_file not in inputs_r:
        job_id = len(inputs)
        inputs.update({job_id: in_file})
        inputs_r.update({in_file: job_id})
    else:
        job_id = inputs_r[in_file]

    return {"job_id": job_id, "filename": filename}

@app.post("/kmeans/fit")
def kmeans_fit(body: FitRequest):
    job_id = body.job_id

    if job_id not in inputs or not os.path.exists(inputs[job_id]):
        raise HTTPException(status_code=500, detail=f"input file missing for job id {job_id}")
    
    in_file = inputs[job_id]
    X = np.genfromtxt(in_file, delimiter=",")

    params = dict(default_model_params)
    params.update(body.model_params)

    kmeans = KMeans(**params).fit(X)
    models.update({job_id: kmeans})

    labels_file = os.path.join(OUTPUT_DIR, f"{job_id}.labels")
    np.savetxt(labels_file, kmeans.labels_, delimiter=",")

    return FileResponse(labels_file, media_type="text/csv")

@app.post("/kmeans/predict")
async def kmeans_predict(job_id: int = Form(...), file: UploadFile = File(...)):
    if job_id in models:
        p_file = os.path.join(OUTPUT_DIR, f"{job_id}.p")
        with open(p_file, "wb") as buffer:
            buffer.write(await file.read())

        p = np.genfromtxt(p_file, delimiter=",")
        result = models[job_id].predict(p)

        res_file = os.path.join(OUTPUT_DIR, f"{job_id}.out")
        np.savetxt(res_file, result, delimiter=",")

        return FileResponse(res_file, media_type="text/csv")
    else:
        raise HTTPException(status_code=500, detail=f"model not found for job id {job_id}")
```

## Running the Example

Follow these steps to run the K-means REST service example:

1. Navigate to the example directory.
2. Activate the Python 3 virtual environment.
3. Install the required dependencies:

```bash
$ pip install -r requirements.txt
```

4. Start the server using uvicorn:

```bash
$ uvicorn server:app --reload --port 8000
```

5. Upload the training file:

```bash
$ curl -X POST "http://localhost:8000/kmeans/upload" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@model.csv;type=text/csv"
```

6. Fit the KMeans model:

```bash
$ curl -X POST "http://localhost:8000/kmeans/fit" \
    -H "accept: text/csv" \
    -H "Content-Type: application/json" \
    -d "{\"job_id\":0,\"model_params\":{\"n_clusters\":3}}"
```

7. Perform predictions:

```bash
$ curl -X POST "http://localhost:8000/kmeans/predict" \
    -H "accept: text/csv" \
    -H "Content-Type: multipart/form-data" \
    -F "job_id=0" \
    -F "file=@predict.csv;type=text/csv"
```

The Swagger UI is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Service Endpoints

### Path kmeans/upload

A POST request is used to upload a file containing points to create the k-means clustering model. The content type must be `multipart/form-data`.

Example input data (6 points in XY dimensions):

```text
1, 2
1, 4
1, 0
10, 2
10, 4
10, 0
```

Curl command:

```bash
$ curl -X POST "http://localhost:8000/kmeans/upload" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@model.csv;type=text/csv"
```

A successful request returns a JSON response containing the filename and the associated Job ID.

```json
{
  "filename": "model.csv",
  "job_id": 0
}
```

### Path kmeans/fit

A POST request with a JSON body provides the Job ID and model parameters for scikit-learn KMeans initialization.

Example request body:

```json
{
  "job_id": 0,
  "model_params": {
    "n_clusters": 3
  }
}
```

Curl command:

```bash
$ curl -X POST "http://localhost:8000/kmeans/fit" \
        -H "accept: text/csv" \
        -H "Content-Type: application/json" \
        -d "{\"job_id\":0,\"model_params\":{\"n_clusters\":3}}"
```

The response is a CSV file containing the labels for the input points.

```text
1.000000000000000000e+00
1.000000000000000000e+00
1.000000000000000000e+00
0.000000000000000000e+00
0.000000000000000000e+00
2.000000000000000000e+00
```

### Path kmeans/predict

A POST request with `multipart/form-data` contains the Job ID and a file containing the points to be predicted.

Request parameters:
* `job_id=0`
* File content:

```text
0, 0
12, 3
```

Curl command:

```bash
$ curl -X POST "http://localhost:8000/kmeans/predict" \
        -H "accept: text/csv" \
        -H "Content-Type: multipart/form-data" \
        -F "job_id=0" \
        -F "file=@predict.csv;type=text/csv"
```

The response is a CSV file with the labels for the provided points.

```text
1.000000000000000000e+00
0.000000000000000000e+00
```

## Implementation Notes

!!! warning "Asynchronous Processing"
    AI jobs are often long-running. While the examples provided are synchronous, production implementations should handle these operations asynchronously to avoid timeouts.

* Services can be combined to accept a model file and prediction input in a single request to return predicted outputs synchronously.
* Model fitting and prediction are separated into different services to allow users to reuse a fitted model for multiple predictions.

## Summary Checklist

* [ ] Define OpenAPI 3.0 specifications for AI endpoints.
* [ ] Implement file upload handling using `multipart/form-data`.
* [ ] Create a mechanism to map Job IDs to model state and data.
* [ ] Integrate scikit-learn KMeans for fitting and prediction.
* [ ] Verify service endpoints using curl and Swagger UI.

## Assignments

!!! note "Exercise: Model Parameterization"
    Modify the `kmeans/fit` endpoint to accept additional scikit-learn KMeans parameters, such as `init` or `max_iter`, and verify that the model behaves as expected.

!!! note "Exercise: Result Export"
    Create a new endpoint `kmeans/centers` that returns the cluster centers for a given Job ID in JSON format.

## Self-Evaluation

??? note "How does the Job ID facilitate the separation of the fit and predict services?"
    The Job ID acts as a unique identifier that links the uploaded training data, the resulting fitted model stored in memory, and the subsequent prediction requests. This allows the server to remain stateless regarding the client session while maintaining state regarding the AI model.

??? note "Why is multipart/form-data used for the upload and predict endpoints instead of a JSON body?"
    `multipart/form-data` is more efficient for transferring large binary or text files (like CSVs) compared to encoding file content as a base64 string within a JSON payload, which increases the data size and processing overhead.

??? note "What are the limitations of storing fitted models in an in-memory dictionary?"
    In-memory storage is volatile; if the server restarts, all fitted models are lost. Additionally, this approach does not scale across multiple server instances (load balancing), as the model would only exist on the instance that performed the fitting. A distributed cache or database would be required for production scalability.
