import sys, datetime

provider = sys.argv[1]

showcols = None
if len(sys.argv) > 2:
      showcols = sys.argv[2]

if showcols is not None:
      showcols = True
else:
      showcols = False

start_time = datetime.datetime.now()

import psycopg
from psycopg.rows import dict_row
import pandas as pd

conn = psycopg.connect(
      host="localhost", port=5444,
      autocommit = True,
      row_factory=dict_row
)

def run_show_insert(command):
      print("running %s..." % command)
      try:
            r = conn.execute(command)
            return r.fetchall()
      except Exception as e:
            if "error creating insert statement" in str(e):
                  print("ERROR [%s]" % str(e))
                  return None
            else:
                  sys.exit(1)

def run_query(query):
      print("running %s..." % query)
      try:
            r = conn.execute(query)
            data = r.fetchall()
            return pd.DataFrame([i.copy() for i in data])
      except Exception as e:
            print("ERROR [%s]" % str(e))
            sys.exit(1)

# SHOW SERVICES
iql_services_query = "SHOW SERVICES IN %s" % provider
services = run_query(iql_services_query)
num_services = len(services)

total_resources = 0
total_selectable_resources = 0
total_methods = 0

# SHOW RESOURCES
for serviceIx, serviceRow in services.iterrows():
      service = serviceRow['name']
      iql_resources_query = "SHOW EXTENDED RESOURCES IN %s.%s" % (provider, service)
      resources = run_query(iql_resources_query)
      num_resources = len(resources)
      print("processing %s resources in %s" % (num_resources, service))
      total_resources = total_resources + num_resources
      for resIx, resRow in resources.iterrows():
            resource = resRow['name']
            fqrn_len = len("%s.%s.%s" % (provider, service, resource))

            print("-------------------------------------------------")
            print("%s.%s.%s (length: %s)" % (provider, service, resource, fqrn_len))
            print("-------------------------------------------------")

            # SHOW METHODS
            iql_methods_query = "SHOW EXTENDED METHODS IN %s.%s.%s" % (provider, service, resource)
            methods = run_query(iql_methods_query)
            if showcols:
                  print(methods)            
            num_methods = len(methods)
            total_methods = total_methods + num_methods
            print("%s methods in %s.%s.%s" % (num_methods, provider, service, resource))

            if len(methods.query("SQLVerb == 'SELECT'")) > 0:
                  total_selectable_resources = total_selectable_resources + 1
                  iql_desc_query = "DESCRIBE EXTENDED %s.%s.%s" % (provider, service, resource)
                  desc = run_query(iql_desc_query)
                  if showcols:
                        print(desc)
                  print("%s columns in %s.%s.%s" % (len(desc), provider, service, resource))

            if len(methods.query("SQLVerb == 'INSERT'")) > 0:
                  iql_insert_query = "SHOW INSERT INTO %s.%s.%s" % (provider, service, resource)
                  show_insert = run_show_insert(iql_insert_query)

print("%s services processed" % (num_services))
print("%s total resources processed" % (total_resources))
print("%s total methods available" % (total_methods))
print("%s total selectable resources" % (total_selectable_resources))

print(datetime.datetime.now() - start_time)