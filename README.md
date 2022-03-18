# comotion-sdk

comotion-sdk is the python SDK for interacting with the Comotion APIs.  Initial support is limited to Dash, but may expand in future.


# Documentation

Documentation for this module can be found [here](https://comotionlabs.github.io/comotion-sdk/).

# Contributing

In order to contribute to this project, fork this repo and submit a pull request to this project

In order to set up a local environment, pull this repo and install.

`pipenv` is used to manage dependencies on this project. in order to use it, ensure that pipenv is installed.

```
pip install --upgrade pip
pip install pipenv
```

And then enter the virtual environment for this project that will automatically ensure all dependencies are available

```
pipenv shell
pipenv install -e .
```


## Building docs

Run the following from the docs directly. Ensure to watch out for warnings.
`
make html
`
## Rerunning code generator

We use OpenApi generator to generate the python.

The requirements for this are a swagger file that can be gotten from WHERE?

The latest swagger file is stored in openapi_generator/comodash_api_swagger.json

Download latest [jar of OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator#13---download-jar)

`
java -jar \
./openapi_generator/openapi-generator-cli-5.2.1.jar generate \
  -i ./openapi_generator/comodash_api_swagger.yaml\
  -g python \
  --package-name comodash_api_client_lowlevel \
  --api-package comodash_api \
  --additional-properties generateSourceCodeOnly=True,library=asyncio \
  -o ./src/
`
