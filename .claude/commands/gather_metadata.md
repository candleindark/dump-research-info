Gather metadata from: $ARGUMENTS

## Goal
Gather metadata from the resource specified by the provided arguments. 

## Context and requirements
The gathered metadata should be in records of JSON format that conform to the data models (classes)
defined in or referenced by the [demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml). 

### Notes
- The data models (classes) defined in or referenced by the [demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
are also specified by the OpenAPI documentation of the REST API of a dump-things-server instance 
which is set up to receive records of the schema. The OpenAPI documentation is located at
`http://localhost:8111/openapi.json`.


Execute the following steps to gather metadata:
1. Ensure the instance of the dump-things-server is running. (This can be done through a
   GET request its `/server` endpoint, which should return a 200 status code if the server is running.)
   If the server is not running, start the server by executing the following command in the terminal:
   ```
   hatch run dump-server:start
   ```
   (Please note the above command is blocking in the terminal, so you may want to start it in a separate terminal window.)
   Once the server is started, you should verify that it is running by checking the `/server` endpoint again.
   Once the server is running, you can proceed to the next step.
2. Gather metadata from the specified resource.
3. For each record of metadata gathered, validate it against the target data model (class) using
   the REST API of the dump-things-server instance. (This can be done by sending a POST request to the
   `/{collection}/validate/record/{class}` endpoint, where `{collection}` is `research_info` and `{class}` is the name 
   of the data model (class) that the record is supposed to conform to. The body of the POST request should be the JSON record to validate.)
