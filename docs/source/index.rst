.. Comotion SDK documentation master file, created by
   sphinx-quickstart on Fri Jun 18 18:45:23 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started with Comotion Python SDK
========================================

This documentation helps you get set up on and use the python Comotion SDK.  This documentation includes this getting started page, and full documentation on the sdk functions:

.. toctree::
   :maxdepth: 1

   comotion.dash
   comotion.auth

This is an open source project, and can be `contributed to <https://github.com/ComotionLabs/comotion-sdk>`_ by the community.

The full Comotion documentation portal can be found here_.
   .. _here: https://docs.comotion.us

Installation
############

Install the comotion-sdk in your python environment using pip:
::

   pip install comotion-sdk


Uploading Data to Dash Using the SDK
####################################

In order to use it in your python file, you must first import it.  In these examples we will import the dash module directly as follows

::

   from comotion import dash

The dash module has a number of useful functions to interact with the Comotion Dash API.

Uploading a csv file to Dash
****************************

The ``read_and_upload_file_to_dash`` reads a csv file, breaks it up, gzips the files and pushes them to the Dash API.

::

   # Break up and upload file to Dash

   from comotion import dash
   from getpass import getpass

   # set relevant parameters
   dash_orgname = 'my_org_name'
   dash_api_key = ''
   dash_api_key = getpass(
       prompt='Enter your ' + dash_orgname + '.comodash.io api key:'
   ) # this prompts the user to enter the api key

   dash.read_and_upload_file_to_dash(
       './path/to/csv/file.csv',
       dash_table='my_table_name',
       dash_orgname=dash_orgname,
       dash_api_key=dash_api_key
   )


Modifying a file for upload
****************************

Often you will want to add a column - such as an upload timestamp or batch number - to the csv file to be uploaded.  This can easily be done by using the ``modify_lambda`` parameter.  It accepts a python function that recieves a `pandas.dataframe <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_  read from the csv. Here is an example of adding a timestamp as a column called ``snapshot_timestamp`` to the csv:

::

   # Break up and upload file to Dash with Extra Column

   from comotion import dash
   from getpass import getpass
   from datetime import datetime

   # define the function used to modify the file

   myTimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

   def addTimeStamp(df):
    df['snapshot_timestamp'] = myTimeStamp

   # set relevant parameters

   dash_orgname = 'my_org_name'
   dash_api_key = ''
   dash_api_key = getpass(
       prompt='Enter your ' + dash_orgname + '.comodash.io api key:'
   ) # this prompts the user to enter the api key

   dash.read_and_upload_file_to_dash(
       './path/to/csv/file.csv',
       dash_table='my_table_name',
       dash_orgname=dash_orgname,
       dash_api_key=dash_api_key,
       modify_lambda=addTimeStamp
   )


Testing and debugging an upload script
**************************************

In order to check that your script is working, you can run a dry run. This saves the files locally rather than uploading them to dash - so that you can check the result before uploading.
::

   # First test the upload using the dry_run feature

   from comotion import dash
   from getpass import getpass

   # set relevant parameters
   dash_orgname = 'my_org_name'
   dash_api_key = ''
   dash_api_key = getpass(
       prompt='Enter your ' + dash_orgname + '.comodash.io api key:'
   ) # this prompts the user to enter the api key

   dash.read_and_upload_file_to_dash(
       './path/to/csv/file.csv',
       dash_table='my_table_name',
       dash_orgname=dash_orgname,
       dash_api_key=dash_api_key,
       path_to_output_for_dryrun='./outputpath/'
   )

Instead of uploading, this will output the files that would have been uploaded to ``./outputpath/``. If the file to be uplaoded is large, it will break it up and all files would be placed in the output path.

Advanced usage with Pandas
**************************

Using this sdk in conjunction with `pandas <https://pandas.pydata.org>`_ provides a powerful toolset to integrate with any source.

Here is an example of reading a table named ``my_table`` from a postgres database:

::

   # upload a postgres table to dash using Pandas

   from comotion import dash
   from getpass import getpass
   import pandas as pd

   # set relevant parameters

   dash_orgname = 'my_org_name'
   dash_api_key = ''
   dash_api_key = getpass(
       prompt='Enter your ' + dash_orgname + '.comodash.io api key:'
   ) # this prompts the user to enter the api key


   # set timestamp to use as a snapshot indication
   myTimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

   # create dataframe from source db:
   df_iterable=pd.read_sql_table(
      table_name='my_table',
      'postgresql://username:password@address.of.db:5432/mydatabase',
      chunksize=30000
      )

   # note the use of chunksize which will ensure the whole table is not read at once.
   # this is also important to ensure that files uploaded to Dash are below the size limit


   for df in df_iterable:
      # add timestamp as a column
      df['snapshot_timestamp'] = myTimeStamp

      # create a gzipped csv stream from the dataframe
      csv_stream = dash.create_gzipped_csv_stream_from_df(df)

      # upload the stream to dash
      dash_response = dash.upload_csv_to_dash(
          dash_orgname,
          dash_api_key,
          'my_table_in_dash',
          csv_stream
      )


Running Queries and Extracting Data
####################################

You can use the sdk to run queries on Dash, as well as download the results in csv format.

Logging In
**********

The query API is built on v2 of the Comotion API - which uses a new way to authenticate.  You do not need an API key, but can log in with your normal user name and password.

In order to do this, after you have installed the SDK, you need to authenticate from the command line.  Type in the following from the command line

::

   > comotion authenticate

You will be prompted for your `orgname` which is your orgnisation's unique name, and then a browser will open for you to login.

Once this process is complete, the relevant keys will automatically be saved in your computers's credentials manager.

To prevent asking for orgname every time, you can save your orgname as an environment variable `COMOTION_ORGNAME`

::

   > export COMOTION_ORGNAME=orgname
   > comotion authenticate

or, include it directly in the comment line:

::

   > comotion -o orgname authenticate


Running a query
***************

You can then use the query object in the :doc:`./comotion.dash` to create  a query and download the results.  Here is an example code snippet.  You do not need to authenticate in your code - the Auth class takes care of that.

.. code-block::

   from comotion.dash import DashConfig
   from comotion.auth import Auth
   from comotion.dash import Query

   config = DashConfig(Auth("myorgname"))

   # this step creates the query object and kicks off the query
   query = Query(query_text="select 1", config=config)

   # this step blocks until the query is complete and provides the query metadata
   final_query_info = query.wait_to_complete()


   with open("myfile.csv", "wb") as file:
      with query.get_csv_for_streaming() as response:
         for chunk in response.stream(524288):
            file.write(chunk)


Authentication Using Client Secret
**********************************

We have introduced an additional method of authenticating to the Comotion API using a client secret.  This allows applications to consume the API without a user.

.. admonition::  User vs Application Authentication
      
      If your users are logging into an application which needs to consume data from Dash, a better approach is to integrate that app with our single signon functionality.
      
      That application can then use an access token generated for that user to consume the dash API.  This means better security as Dash will be aware of the user, and obey things like Service Client data siloing.
      
      This section deals with the scenario where the application itself is acting as the user, which is useful for various data extraction and loading scenarios.

In order to use this functionality, the dash team will need to create a new `client`, and supply a client_id and secret key that will be used to authenticate.  Get in touch with dash@comotion.co.za.

Once that is done, your application can authenticate using the secret key using the `application_secret_id` and `application_client_secret` parameters, as shown in the example below.

.. code-block:: python

   from comotion.dash import DashConfig
   from comotion.auth import Auth
   from comotion.dash import Query

   ## Authenticate as an application
   auth = Auth(
        entity_type=Auth.APPLICATION,
        application_client_id="test",
        application_client_secret="2shjkdfbjsdhfg2893847",  
        #best to pass to your application from an apprioriate secrets manager or environment variable
        orgname="myorgname"
   )
   config = DashConfig(auth)

   # this step creates the query object and kicks off the query
   query = Query(query_text="select 1", config=config)

   # this step blocks until the query is complete and provides the query metadata
   final_query_info = query.wait_to_complete()
   
   if final_query_info.status.state == 'FAILED':
      # deal with failure scenario
      raise Exception(f'Error while retrieving Dash data: Query failed; {final_query_info.status.state_change_reason}')
   
   elif final_query_info.status.state == 'CANCELLED':
      # deal with cancelled scenario
      raise Exception(f'Error while retrieving Dash data: Query cancelled; {final_query_info.status.state_change_reason}')
      
   else:
      # deal with success scenario
      with open("myfile.csv", "wb") as file:
         with query.get_csv_for_streaming() as response:
            for chunk in response.stream(524288):
               file.write(chunk)


To process the output data further instead of writing to a csv file, load the data into a dataframe:

.. code-block:: python
   
      response = query.get_csv_for_streaming()
      data = io.StringIO(response.data.decode('utf-8'))
      df = pd.read_csv(data)
      # further processing...


