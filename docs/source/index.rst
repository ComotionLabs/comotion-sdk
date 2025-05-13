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

If you have already installed the SDK, ensure it is up to date by running:
::

   pip install --upgrade comotion-sdk

Authentication
##############

.. _logging-in:

Logging In
**********

The Comotion Dash API is built on v2 of the Comotion API - which uses a new way to authenticate.  You do not need an API key, but can log in with your normal user name and password.

In order to do this, after you have installed the SDK, you need to authenticate from the command line.  Type in the following from the command line

::

   > comotion authenticate

You will be prompted for your ``orgname`` which is your orgnisation's unique name, and then a browser will open for you to login.

Once this process is complete, the relevant keys will automatically be saved in your computers's credentials manager.

Org Name Set-up
***************

To prevent asking for orgname every time, you can save your orgname as an environment variable ``COMOTION_ORGNAME``

::

   > export COMOTION_ORGNAME=orgname
   > comotion authenticate

or, include it directly in the comment line:

::

   > comotion -o orgname authenticate

Uploading Data to Dash: Data Model v2
#####################################

The following upload toolsets are available once you are on data model v2. Remember to authenticate if you haven't in a while: :ref:`logging-in`.

* :ref:`dashbulkuploader`
* :ref:`load`

For more information on migrating, see :ref:`migrate-to-v2`.

.. hint ::

   It is helpful to track the ``load_id`` of the loads you create.  
   
   This is a unique identifier for the load, and can be used to re-create the load if needed.

   Comotion can also provide support easily if the ``load_id`` is provided.

.. _dashbulkuploader:

DashBulkUploader
****************

The ``DashBulkUploader`` class is the recommended way to upload data to Dash.  This uses the ``Load`` class, but provides some default functionality and the ``uploads`` attribute to manage multiple loads.

If more control is needed over the upload process, the :ref:`load` class can be used instead.

The process can be summarized as follows: 

1. Create a ``DashBulkUploader`` object
2. Add loads to the uploader 
3. Add data sources to each load
4. Execute the uploads
5. Check the status of the loads

Below is a simple example of how to use the ``DashBulkUploader`` class.

.. code-block:: python

   from comotion.dash import DashBulkUploader, DashConfig
   from comotion.auth import Auth 

   # 1. Create the uploader object
   config = DashConfig(Auth(orgname = 'my_org_name'))
   uploader = DashBulkUploader(config = config)

   # 2. Add a Load -> essentially creates a Load object and adds it to the uploader
   lake_tables_and_sources = [
       ('v1_policies', 'data/inforce_policies'),
       ('v1_claims', 'data/claims'),
       ('v1_customers', 'data/customers')
   ]

   for my_lake_table, source_data in lake_tables_and_sources:
      uploader.add_load(
         table_name=my_lake_table,
         load_as_service_client_id='0',
         track_rows_uploaded=True  # This automatically creates a check_sum {'count(*)': x} where x is the number of rows in the source data.
         # See cheat sheet for more options available for the load.
      )

      # Add data source(s) to the Load. At least one data source is required, but multiple can be added to the same load.
      uploader.add_data_to_load(
         table_name=my_lake_table,
         data=source_data  # Can be a path to a csv, parquet or directory, a pandas dataframe or a dash.Query object
         # See cheat sheet for more options available for the data source.
      )

   # 4. Execute the uploads - this commits the loads.
   print(uploader.uploads)
   uploader.execute_all_uploads() # You can also execute specific uploads with execute_multiple_uploads() and execute_upload()

   # 5. Check the status of the loads
   print(uploader.get_load_info())

See the :ref:`v2_cheat-sheet` for different configuration options available, and if they should be specified for the load or the data source.

If your data source has specific read requirements, see :ref:`pandas-usage` for more information on how to use pandas arguments to handle your use case.

.. hint::

      If a path to a directory is specified as a data source, all valid files in the directory will be uploaded to the lake table specified.  
      
      This allows you to chunk files and store them in the same folder for more efficient extract and upload.

      Note this is not an option for the ``Load`` class.

.. admonition::  Obtaining the ``file_key`` to remove data from a load

   The ``file_key`` parameter is used to avoid duplicating a data source within a load.  This is automatically generated if not provided.

   You can also use the ``uploader.remove_load()`` or ``uploader.remove_data_from_load()`` functions to remove loads or data sources from the uploader respectively.
   
   The ``remove_data_from_load`` function requires a file key to be specified, which can be retrieved from the ``uploader.uploads`` object.

.. _load:

Load
****

The ``Load`` class is the primary class for uploading data to Dash. The process of using this class can be outlined as follows:

1. Create a ``Load`` object
2. Upload data sources to the load 
3. Commit the load with a valid check sum
4. Check the status of the load

.. code-block:: python

   from comotion.dash import Load, DashConfig, Query
   from comotion.auth import Auth
   import pandas as pd

   # 1. Create the load object and data source variables
   dashconfig = DashConfig(Auth(orgname = 'my_org_name'))

   load = Load(config = dashconfig,
               load_type = 'APPEND_ONLY',
               table_name = 'v1_inforce_policies',
               load_as_service_client_id = '0',
               track_rows_uploaded = True
               # See cheat sheet for more options available for the load.
               )
   print("Load ID: " + load.load_id) # It is helpful to track the load_id

   # 2. Upload data sources to the load. At least one data source is required, but multiple can be added to the same load.

   # Several examples shown for demonstration, but typically only one of these functions will be required.
   # 2.1: Upload a pandas dataframe. This is useful if your source is not part of the standard data sources supported.
   df_for_upload = pd.read_sql(query, connection)
   load.upload_df(
      data = df_for_upload 
   )
   # 2.2: Upload a file. This can be a csv, parquet, json or excel file or file .io stream.
   path_to_upload_file = 'data/inforce_policies.csv'
   load.upload_file(
      data = path_to_upload_file
   )
   # 2.3: Uploaed a dash.Query object. This is useful, for example, for moving data from one lake table to another.
   dash_query = Query(query_text = 'select * from orgname_lake_v2.v1_staging_policies', config = dashconfig)
   load.upload_dash_query(# Uploads the result of a dash.Query object.
      data = dash_query
   )

   # 3. Commit the load with a valid check sum.
   load.commit(
      check_sum = {
         'sum(salary)': 12345
      }
   )

   # 4. Check the status of the load
   print(load.wait_to_complete())
   load_info = load.get_load_info()
   print(load_info)

See the :ref:`v2_cheat-sheet` for different configuration options available.

You can also re-create an existing load if you have the correct ``load_id``.

.. code-block:: python 

   load = Load(config = dashconfig,
               load_id = 'load_id'
               # The other arguments should not be specified when re-creating a load.
               )

.. _data-model-v1-upload:

Uploading Data to Dash: Data Model v1
######################################

.. note::

   Comotion has released a new version of our data model in 2025. We refer to the original version as Data Model v1, and the new version as Data Model v2.

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

Custom Upload Usage
###################

.. _testing-and-debugging:

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

.. _pandas-usage:

Pandas Usage
************

Using this sdk in conjunction with `pandas <https://pandas.pydata.org>`_ provides a powerful toolset to integrate with any source.

.. hint::

   Uploads are always converted to a ``pandas.DataFrame`` when uploading with the SDK when using the ``Load`` and ``DashBulkUploader`` classes.  This allows you to provide valid pandas arguments in the ``Load.upload_file()``, ``Load.upload_dash_query()`` and ``DashBulkUploader.add_data_to_load()`` functions.

   For production uploads, the dtype argument is highly recommended: `pandas dtypes <https://pandas.pydata.org/docs/user_guide/basics.html#dtypes>`_.

   The following 3 examples are equivalent ways to upload data into Dash.  Notice how the exact same arguments which can be passed to a ``pandas`` read function can be passed to the SDK classes:
   
   .. code-block:: python

      # 1: Using pandas arguments in the Load class
      load.upload_file(
         data = 'my_data.csv',
         dtype = {'column_1': 'int', 'column_2': 'object'}
         sep = ';',
         encoding = 'utf-16'
         # Could add any more valid pandas arguments here
      )

      # 2: Using pandas arguments in the DashBulkUploader class
      uploader.add_data_to_load(
         table_name = my_lake_table,
         data = 'my_data.csv',
         dtype = {'column_1': 'int', 'column_2': 'object'},
         sep = ';',
         encoding = 'utf-16'
         # Could add any more valid pandas arguments here
      )

      # 3: Read with pandas and upload df with the SDK
      df = pd.read_csv('my_data.csv', 
                       dtype = {'column_1': 'int', 'column_2': 'object'},         
                       sep = ';',
                       encoding = 'utf-16')

      # 3.1: Then upload a df with the DashBulkUploader
      uploader.add_data_to_load(
         table_name = my_lake_table,
         data = df
      )

      # OR 3.2: Upload a df with the Load class
      load.upload_df(
         data = df
      )

   But there are many more pandas arguments available to read your source correctly.  Refer to the applicable pandas read function documentation in the table below to see the available arguments for your source data.

   (Almost) All of the arguments available in the applicable read function can be used with the SDK.

   .. list-table:: Pandas Read Options for Source Types
      :header-rows: 1

      * - Data Source Type
        - Pandas Read Function Documentation
      * - CSV
        - `pd.read_csv <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html>`_
      * - Excel
        - `pd.read_excel <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html>`_
      * - JSON
        - `pd.read_json <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_json.html>`_
      * - Parquet
        - `pd.read_parquet <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_parquet.html>`_
      * - Other 
        - See example 3 above. First read the data into a pandas dataframe using the appropriate pandas read function, and then use the ``Load.upload_df()`` or ``DashBulkUploader.add_data_to_load()`` function to upload it.

   .. note::

      The following pandas arguments should not be provided as they are used by the default functionality of the SDK: 
      ``['filepath_or_buffer', 'chunksize', 'nrows', 'path', 'path_or_buf', 'io']``.

.. hint::

   Often you will want to process your source data before uploading. For example, you may want to add metadata to the data, or hash PII before uploading.

   Simple operations on the source data can be applied for the upload using the ``modify_lambda`` parameter.  It accepts a python function that recieves a `pandas.dataframe <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.
   
   Here is simple example of adding a timestamp as a column called ``snapshot_timestamp`` to the csv.  The function provided can apply several manipulations to the data if required:

   .. code-block:: python

      # Break up and upload file to Dash with Extra Column

      from comotion import dash
      from getpass import getpass
      from datetime import datetime
      import pandas as pd

      # define the function used to modify the file

      myTimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

      def addTimeStamp(df: pd.DataFrame): # Do not need to specify the type of df, but shown for demonstration
         df['snapshot_timestamp'] = myTimeStamp
         # Can provide more manipulations in this function if needed

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

.. _migrate-to-v2:

Migrating to Data Model v2
##########################

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

Running Queries and Extracting Data
###################################

You can use the sdk to run queries on Dash, as well as download the results in csv format.

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
   
      import io
      response = query.get_csv_for_streaming()
      data = io.StringIO(response.data.decode('utf-8'))
      df = pd.read_csv(data)
      # further processing...

Data Zones
##########

If an upload or query needs to be run in a specific data zone, the ``zone`` argument can be specified when creating the ``DashConfig`` object.

.. code-block:: python

   from comotion.dash import DashConfig, Query, Load
   from comotion.auth import Auth

   zone_1_config = DashConfig(Auth("myorgname"), zone = 'zone_1')
   zone_2_config = DashConfig(Auth("myorgname"), zone = 'zone_2')

   # This runs the query in zone_1
   query = Query(query_text="select 1", config=zone_1_config)

   # This creates a load in zone_2
   load = Load(config = zone_2_config,
               load_type = 'APPEND_ONLY',
               table_name = 'v1_inforce_policies',
               load_as_service_client_id = '0',
               track_rows_uploaded = True
               )
   
.. _v2_cheat-sheet:

v2 Upload Cheat sheet
#####################

Below is a cheat sheet for the important arguments available for the ``DashBulkUploader`` and ``Load`` classes.

.. list-table:: Argument Cheat Sheet
   :header-rows: 1

   * - Arg
     - Required
     - Description
     - DashBulkUploader: Use when calling
     - Load: Use when calling
     - Comments
   * - config
     - Yes
     - :class:`DashConfig <comotion.dash.DashConfig>`
     - :class:`DashBulkUploader <comotion.dash.DashBulkUploader>`
     - :class:`Load <comotion.dash.Load>`
     - 
   * - table_name
     - Yes
     - Name of the lake table to upload to.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     - 
   * - load_type
     - Yes for ``Load``, No for ``DashBulkUploader``
     - Type of load to create.  Currently only 'APPEND_ONLY' is supported.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     - 
   * - load_as_service_client_id
     - No if service_client_id field is created in data source, otherwise Yes.
     - Service client id to add to each row of data in the Load.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     - 
   * - partitions
     - No
     - List of fields to partition on
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     - 
   * - load_id
     - No
     - Load id to use when re-creating a load.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     -
   * - track_rows_uploaded
     - No
     - Indicate if row count check sum should be created for the load automatically.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     -
   * - path_to_output_for_dryrun
     - No
     - Path to the directory to save the files to when running a test run, i.e. not uploading to Dash.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     - :ref:`testing-and-debugging`
   * - modify_lambda
     - No
     - Function to modify the data before uploading.  This function should take a pandas dataframe as input and manipulate the dataframe in-place as needed.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     - :ref:`pandas-usage`
   * - chunksize 
     - No
     - Size of the chunks to break the data into for uploading.  This is a legacy argument, but smaller chunksize can be specified if required.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :class:`Load <comotion.dash.Load>`
     -
   * - check_sum 
     - Yes (or ``specify track_rows_uploaded = True``)
     - Check sum to use for the load.  This is a dictionary of SQL aggregations and expected values. The sql aggregation is run on unioned combined data sources, and if the result does not match the expected value, the load is rejected.
     - :meth:`DashBulkUploader.add_load <comotion.dash.DashBulkUploader.add_load>`
     - :meth:`Load.commit <comotion.dash.Load.commit>`
     - 
   * - data 
     - Yes
     - Specification of data source to be uploaded.  Exact type depends on the function used to upload the data and the source data format.
     - :meth:`DashBulkUploader.add_data_to_load <comotion.dash.DashBulkUploader.add_data_to_load>`
     - :meth:`Load.upload_df <comotion.dash.Load.upload_df>` ; :meth:`Load.upload_file <comotion.dash.Load.upload_file>` ; :meth:`Load.upload_dash_query <comotion.dash.Load.upload_dash_query>`
     - A directory can only be specified as a data source using the :meth:`DashBulkUploader.add_data_to_load <comotion.dash.DashBulkUploader.add_data_to_load>` function.
   * - file_key
     - No
     - Unique key to identify the data source.  This is automatically generated if not provided.
     - :meth:`DashBulkUploader.add_data_to_load <comotion.dash.DashBulkUploader.add_data_to_load>`
     - :meth:`Load.upload_df <comotion.dash.Load.upload_df>` ; :meth:`Load.upload_file <comotion.dash.Load.upload_file>` ; :meth:`Load.upload_dash_query <comotion.dash.Load.upload_dash_query>`
     - This is used to avoid duplicating a data source within a load, as well as to remove data sources from a load in the ``DashBulkUploader`` class.
   * - ``**pd_read_kwargs``
     - No
     - Placeholder for additional arguments to pass to the pandas read function. E.g. dtype, sep, sheet_name, skiprows etc.
     - :meth:`DashBulkUploader.add_data_to_load <comotion.dash.DashBulkUploader.add_data_to_load>`
     - :meth:`Load.upload_file <comotion.dash.Load.upload_file>` ; :meth:`Load.upload_dash_query <comotion.dash.Load.upload_dash_query>`
     - :ref:`pandas-usage`
