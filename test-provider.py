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

pd.set_option('display.max_columns', None)

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
            # google workaround
            if "SELECT not supported for this resource" in str(e):
                  print("WARN [%s]" % str(e))
                  return None
            elif "the last operation didn't produce a result" in str(e):
                  return None
            # elif "cannot describe view without context" in str(e):
            #       return None
            else:
                  print("ERROR [%s]" % str(e))
                  sys.exit(1)

# SHOW SERVICES
iql_services_query = "SHOW SERVICES IN %s" % provider
services = run_query(iql_services_query)
if services is None:
      print("ERROR [no services found for %s]" % provider)
      sys.exit(1)
num_services = len(services)

total_resources = 0
total_selectable_resources = 0
total_methods = 0
non_selectable_resources = []

def _service_is_show_insert_exmpted(provider: str, svc: str) -> bool:
      if provider == 'aws' and svc not in ('cloud_control', 'ec2_api', 'iam_api', 's3_api', 'cloudwatch_api', 'cloudhsm'):
            return True
      if provider == 'k8s':
            return True
      if provider == 'databricks_account':
            return True
      if provider == 'databricks_workspace':
            return True      
      return False

# SHOW RESOURCES
for serviceIx, serviceRow in services.iterrows():
      service = serviceRow['name']
      iql_resources_query = "SHOW EXTENDED RESOURCES IN %s.%s" % (provider, service)
      resources = run_query(iql_resources_query)
      if resources is None:
            print("ERROR [no resources found for %s.%s]" % (provider, service))
            sys.exit(1)
      num_resources = len(resources)
      print("processing %s resources in %s" % (num_resources, service))
      total_resources = total_resources + num_resources
      for resIx, resRow in resources.iterrows():
            resource = resRow['name']
            fqrn_len = len("%s.%s.%s" % (provider, service, resource))

            print("-------------------------------------------------")
            print("%s.%s.%s (length: %s)" % (provider, service, resource, fqrn_len))
            print("-------------------------------------------------")

            # test selectability
            is_selectable = True
            iql_desc_query = "DESCRIBE EXTENDED %s.%s.%s" % (provider, service, resource)
            desc = run_query(iql_desc_query)

            if desc is None:
                  print("[WARN] SELECT not supported for %s.%s.%s" % (provider, service, resource))
                  is_selectable = False
            else:
                  if len(desc) == 0:
                        print("ERROR [no columns found for %s.%s.%s]" % (provider, service, resource))
                        sys.exit(1)
                  
                  total_selectable_resources = total_selectable_resources + 1
                  if showcols:
                        print(desc)

            if not is_selectable:
                  non_selectable_resources.append("%s.%s" % (service, resource))

            # test methods
            iql_methods_query = "SHOW EXTENDED METHODS IN %s.%s.%s" % (provider, service, resource)
            methods = run_query(iql_methods_query)
            if methods is None:
                  if not is_selectable:
                        print("ERROR [no methods found for %s.%s.%s]" % (provider, service, resource))
                        sys.exit(1)
            else:
                  # we have methods      
                  if showcols:
                        print(methods)                  
                  num_methods = len(methods)
                  total_methods = total_methods + num_methods
                  print("%s methods in %s.%s.%s" % (num_methods, provider, service, resource))
                  if len(methods.query("SQLVerb == 'INSERT'")) > 0:
                        if _service_is_show_insert_exmpted(provider, service):
                              pass
                        else:
                              iql_insert_query = "SHOW INSERT INTO %s.%s.%s" % (provider, service, resource)
                              show_insert = run_show_insert(iql_insert_query)

print("%s services processed" % (num_services))
print("%s total resources processed" % (total_resources))
print("%s total methods available" % (total_methods))
print("%s total selectable resources" % (total_selectable_resources))
print("%s non selectable resources" % (len(non_selectable_resources)))
# print('non_selectable_resources:')
# for i in non_selectable_resources:
#       print("SHOW METHODS IN azure." + i + ";")

print(datetime.datetime.now() - start_time)