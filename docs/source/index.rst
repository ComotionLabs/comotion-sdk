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

.. _data-model-v1-upload:

Uploading Data to Dash: Data Model v1
######################################

.. note::

   Comotion has released a new version of our data model in 2025. We refer to the original version as Data Model v1, and the new version as Data Model v2.

In order to use the SDK in your python file, you must first import it.  In these examples we will import the dash module directly as follows

::

   from comotion import dash

The ``read_and_upload_file_to_dash`` function can be used to upload a csv file or stream to Data Model v1.

Uploading a file to Dash
*************************

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
***************************************

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
***************************

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

Uploading Data to Dash: Data Model v2
#####################################

The following upload toolsets are available after :ref:`migrate-to-v2`:

* ``read_and_upload_file_to_dash``: :ref:`data-model-v1-upload`
* :ref:`dashbulkuploader`
* :ref:`load`

``read_and_upload_file_to_dash``
********************************

.. warning:: 

    Comotion will deprecate the ``read_and_upload_file_to_dash`` function on 1 December 2025, along with Data Model v1.

    Once you are operating in the new lake, we recommend you move to using the new :ref:`load` and :ref:`dashbulkuploader` class for uploads.  Reach out to us for assistance at dash@comotion.co.za .

The ``read_and_upload_file_to_dash`` function can also be used to upload to Data Model v2.  See the above section on using this function: 

* :ref:`data-model-v1-upload`.

The key considerations when uploading to the v2 data model with this function are as follows:

* The ``file`` parameter can now accept a path to a csv, excel, json, parquet or directory, a ``pandas.DataFrame`` or a ``dash.Query`` object. 
* The ``dash_api_key`` is no longer required.  Instead you will have to run the following in your command line to authenticate: ``comotion authenticate``
* You will need to specify ``data_model_version = 'v2'`` if you have not run a full migration (more on migrating below)
* The function will return a ``DashBulkUploader`` object.

Example of ETL change for Data Model v2
***************************************

**Python for v1 Upload**

.. code-block:: python

   from comotion.dash import read_and_upload_file_to_dash
   from datetime import datetime

   # In this example, we use the modify_lambda argument to add a column to the end of the lake table to mark the timestamp when the upload was started
   def add_upload_timestamp(df):
      upload_timestamp = datetime.now()
      df['upload_timestamp'] = upload_timestamp.strftime('%Y-%m-%d %H:%M:%S')

   upload_response = read_and_upload_file_to_dash(
      file = 'path/to/file.csv',
      dash_table = 'my_lake_table_name',
      dash_orgname = 'my_dash_orgname',
      dash_api_key = 'my_api_key',
      modify_lambda = add_upload_timestamp # Function defined above
   )

**Python for v2 Upload**

.. code-block:: python

   from comotion.dash import read_and_upload_file_to_dash
   from datetime import datetime

   # In this example, we use the modify_lambda argument to add a column to the end of the lake table to mark the timestamp when the upload was started
   def add_upload_timestamp(df):
      upload_timestamp = datetime.now()
      df['upload_timestamp'] = upload_timestamp.strftime('%Y-%m-%d %H:%M:%S')
      df['data_import_batch'] = upload_timestamp.strftime('%Y-%m-%d') # First change: Add the data import batch column.

   upload_response = read_and_upload_file_to_dash(
      file = 'path/to/file.csv',
      dash_table = 'my_lake_table_name',
      dash_orgname = 'my_dash_orgname',
      # API key is no longer required for the upload
      modify_lambda = add_upload_timestamp, # Function defined above
      data_model_version = 'v2' # Add this parameter to force an attempted upload to the new lake
   )


.. _dashbulkuploader:

DashBulkUploader
****************

The ``DashBulkUploader`` class is the recommended way to upload data to Dash. If more control is needed over the upload process, the :ref:`load` class can be used instead.

.. code-block:: python

   from comotion.dash import DashBulkUploader
   from comotion.auth import Auth 

   auth_token = Auth(orgname = 'my_org_name')
   my_lake_table = 'v1_policies'
   uploader = DashBulkUploader(auth_token = auth_token)

You can now add a load to the uploader.

.. code-block:: python

   uploader.add_load(
                     table_name = my_lake_table,
                     check_sum = {
                        # SQL aggregation: expected result
                        'sum(salary)': 12345 
                     }, # Alternatively, provide the track_rows_uploaded arg as true
                     load_as_service_client_id = '0'
                   )

This creates a Load and adds it to the ``uploader.uploads`` object.  Note that ``modify_lambda``, ``path_to_output_for_dryrun`` and ``chunksize`` can also be specified and will behave the same as for the ``read_and_upload_file_to_dash`` function.

The ``check_sum`` parameter can be used to verify a load before it is pushed to the lake.  Specify a dictionary of valid check sums as in the example above to ensure data quality and completeness. Any valid SQL aggregation can be provided in the keys, and a scalar value should be provided for the values.  You will need to calculate these check sums at source and then provide the expected result as the value.

If this is not required, you can set ``track_rows_uploaded = True``, which will automatically create the check_sum ``{'count(*)': x}``, where ``x`` is the number of rows in the source data. 

Now we need to add a data source to the load

.. code-block:: python

   uploader.add_data_to_load(
                              table_name = my_lake_table,
                              data = 'data/inforce_policies', # Can be a path to a csv, parquet or directory, a pandas dataframe or a dash.Query object
                              dtype={'id': 'int32', 'name': 'string', 'age': 'int32', 'salary': 'float64'} # The dtype parameter is recommended (but optional), as it allows control of lake schema from source and improves upload data quality.
                            )

   print(uploader.uploads) # Will print the dictionary containing loads and data sources added to the uploader.

This function will add the datasource to the applicable load.  You can add multiple data sources to 1 load.  We recommend using the ``dtype`` parameter, which should be compatible with the pandas ``dtype`` argument.

.. hint::

      If a path to a directory is specified, all valid files in the directory will be uploaded to the lake table specified.  
      
      This allows you to chunk files and store them in the same folder for more efficient extract and upload.

The ``file_key`` parameter is used to avoid duplicating a data source within a load.  This is automatically generated if not provided.

You can also use the ``uploader.remove_load()`` or ``uploader.remove_data_from_load()`` functions to remove loads or data sources from the uploader respectively.

.. admonition::  Obtaining the ``file_key`` to remove data from a load
   
   The ``remove_data_from_load`` function requires a file key to be specified, which you can get from the ``uploader.uploads`` object.

Finally, we can execute the upload.

.. code-block:: python

   uploader.execute_upload(table_name = my_lake_table) # Also see functions execute_multiple_uploads and execute_all_uploads.

This will execute the upload. 

You can also check on the load statuses at any time.

.. code-block:: python

   uploader.get_load_info()


.. _load:

Load
****

The ``Load`` class is the most flexible for uploading data to Dash.  The process can be outlined as follows:

1. Create a ``Load`` object
2. Upload data sources to the load 
3. Commit the load with a valid check sum

Creating the ``Load`` object is simple.

.. code-block:: python

   from comotion.dash import Load, Dashconfig 
   from comotion.auth import Auth

   dashconfig = DashConfig(Auth(orgname = 'my_org_name'))
   load = Load(config = DashConfig,
               load_type = 'APPEND_ONLY',
               table_name = 'v1_inforce_policies',
               load_as_service_client_id = '0',
               track_rows_uploaded = True
               # Note modify_lambda, chunksize and path_to_output_for_dryrun are also options
               )

This creates a ``Load`` object.  The ``load_type`` currently only supports ``APPEND_ONLY``, which means the data sources is added to the existing data in the lake table.

The ``load_as_service_client_id`` parameter is not required if the ``service_client_id`` column exists in the data already. You will receive a warning when this is not specified, but it can be ignored if the ``service_client_id`` column exists in the data source.

The ``modify_lambda``, ``path_to_output_for_dryrun`` and ``chunksize`` arguments are also available.

You can also re-create an existing load if you have the correct ``load_id``.

.. code-block:: python 

   load = Load(config = DashConfig,
               load_id = 'load_id'
               )

.. warning::
   Do not specify ``load_type``, ``table_name``, ``load_as_service_client_id`` or ``partitions`` if the ``load_id`` is provided. The Load object will not be created.

Now we can add data sources to the load.

.. code-block:: python

   # Several examples shown for demonstration, but typically only one of these functions will be required.

   dtype = {'id': 'int32', 'name': 'string', 'age': 'int32', 'salary': 'float64'}
   load.upload_df( # Uploads a pandas dataframe
      df = df_for_upload 
   )

   load.upload_file(# Uploads a csv, parquet, json or excel file or file .io stream. Note a file directory will not work here in the same was as for the DashBulkUploader.
      data = path_to_upload_file,
      dtype = dtype # Recommended usage
   )

   load.upload_dash_query(# Uploads the result of a dash.Query object.
      data = dash_query_object,
      dtype = dtype # Recommended usage
   )

Note that a file key can be specified, but a valid file key will be generated if not provided.

Uploads are always converted to a ``pandas.DataFrame`` before uploading the data.  This allows you to provide valid pandas arguments in the ``upload_file`` and ``upload_dash_query`` functions as well, e.g. for an excel spreadsheet:

.. code-block:: python

   load.upload_file(
      data = path_to_upload_file,
      sheet_name = 'inforce_book',
      skiprows = 2
      # Add any more valid pandas arguments here
   )

The following pandas arguments should not be provided: ``['filepath_or_buffer', 'chunksize', 'nrows', 'path', 'path_or_buf', 'io']``

Once all your data sources are added, you can commit the load.

.. code-block:: python

   load.commit(
      check_sum = {
         'sum(salary)': 12345
      }
   )

The ``check_sum`` parameter is used to verify a load before it is pushed to the lake.  Specify a dictionary of valid check sums as in the example above to ensure data quality and completeness. Any valid SQL aggregation can be provided in the keys, and a scalar value should be provided for the values.  You will need to calculate these check sums at source and then provide the expected result as the value.

Note that in this example, a check sum is not necessarily required because we specified ``track_rows_uploaded = True`` when creating the load.  If the load had been created with ``track_rows_uploaded = False``, a check sum is required on commit.

You can check the status of your load at any time.

.. code-block:: python

   load_info = load.get_load_info()
   print(load_info)


.. _migrate-to-v2:

Migrating to Data Model v2
**************************

You can migrate to data model v2 with the SDK.  First you will need to run a flash schema migration.

.. code-block:: python

   from comotion.dash import DashConfig, Migration
   from comotion.auth import Auth

   config = DashConfig(Auth("myorgname"))

   migration = Migration(config = config)
   migration.start(migration_type = 'FLASH_SCHEMA') # This is the default value so it does not need to be specified

This copies the schema of all your lake tables from the v1 lake to the v2 lake.

Now you will be able to test your ETL on the new lake, using the ``read_and_upload_file_to_dash`` function, ``DashBulkUploader`` class or ``Load`` class.

Once you are happy that your ETL will work with the new lake, you can run a full migration.

.. code-block:: python

   migration.start(migration_type = 'FULL_MIGRATION',
                   clear_out_new_lake = True)

This clears out the v2 lake and runs the full migration of data.  If ``clear_out_new_lake`` is false and there is data in the v2 lake, the full migration will fail.

Good practice when migrating would be:

1. Run the flash schema migration 
2. Test your ETL on the new lake until satisfied.
3. Stop ETL processes to the old lake.
4. Run the full migration (the length of time for this depends on the amount of data in your lake, but it should not take more than a couple of hours).
5. Deploy your new ETL processes.

Once the full migration is run, you can no longer upload to the v1 lake.

Check on the migration status at any time.

.. code-block:: python

   print(migration.status())
   
Running Queries and Extracting Data
####################################

You can use the sdk to run queries on Dash, as well as download the results in csv format.

Logging In
**********

The query API is built on v2 of the Comotion API - which uses a new way to authenticate.  You do not need an API key, but can log in with your normal user name and password.

In order to do this, after you have installed the SDK, you need to authenticate from the command line.  Type in the following from the command line

::

   > comotion authenticate

You will be prompted for your ``orgname`` which is your orgnisation's unique name, and then a browser will open for you to login.

Once this process is complete, the relevant keys will automatically be saved in your computers's credentials manager.

To prevent asking for orgname every time, you can save your orgname as an environment variable ``COMOTION_ORGNAME``

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

In order to use this functionality, the dash team will need to create a new ``client``, and supply a client_id and secret key that will be used to authenticate.  Get in touch with dash@comotion.co.za.

Once that is done, your application can authenticate using the secret key using the ``application_secret_id`` and ``application_client_secret`` parameters, as shown in the example below.

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


