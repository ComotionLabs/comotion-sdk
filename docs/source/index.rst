.. Comotion SDK documentation master file, created by
   sphinx-quickstart on Fri Jun 18 18:45:23 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started with the Comotion SDK 
=====================================

Welcome to the Comotion SDK documentation, your comprehensive resource for getting started and harnessing the full power of the SDK functions.

.. toctree::
   :maxdepth: 2

   comotion.dash
   comotion.auth

-----------------

Installation
############

To install the Comotion SDK in your Python environment, simply use pip:

::

   pip install comotion-sdk

-----------------

Authentication & Log In
#######################

The query API is built on V2 of the Comotion API - which uses a new way to authenticate.  You do not need an API key, but can log in with your normal username and password.

In order to do this, after you have installed the SDK, you need to authenticate from the Command Line Interface (CLI).  Type in the following from the command line

::

   > comotion authenticate

You will be prompted for your `orgname` which is your orgnisation's unique name, and then a browser will open for you to login.

Upon successful authentication, the relevant authentication keys will be automatically stored in your computer's credentials manager.

You can save your orgname as an environment variable COMOTION_ORGNAME to prevent the need to enter it each time you use the CLI.

::

   > export COMOTION_ORGNAME=orgname
   > comotion authenticate

or, include it directly in the comment line:

::

   > comotion -o orgname authenticate

-----------------

Uploading Data to Dash Using the SDK
####################################

To begin using the SDK in your Python project, you'll need to import it. Here's how to import the dash module:

::

   from comotion import dash

The dash module has several useful functions to interact with the Comotion Dash API.

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

Often you will want to add a column - such as an upload timestamp or batch number - to the csv file to be uploaded.  This can easily be done by using the ``modify_lambda`` parameter.  It accepts a python function that receives a `pandas.dataframe <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_  read from the csv. 

Here is an example of adding a timestamp as a column called ``snapshot_timestamp`` to the csv:

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

Instead of uploading, this will output the files that would have been uploaded to ``./outputpath/``. If the file to be uploaded is large, it will break it up and all files would be placed in the output path.

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

-----------------

Running Queries and Extracting Data
####################################

You can use the sdk to run queries on Dash, as well as download the results in csv format.

You can then use the query object in the :doc:`./comotion.dash` to create  a query and download the results.  Here is an example code snippet.  You do not need to authenticate in your code - the Auth class takes care of that.

::

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

-----------------

Contribution
############

This is an open source project, and can be `contributed to <https://github.com/ComotionLabs/comotion-sdk>`_ by the community.

The full Comotion documentation portal can be found here_.
   .. _here: https://docs.comotion.us

-----------------
