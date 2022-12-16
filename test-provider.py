import json, sys, os, pandas as pd
from pystackql import StackQL
from io import StringIO

provider = sys.argv[1]
regpath = sys.argv[2]

anon_call_check = False

# manually invoke anon col checks
if len(sys.argv) > 3:
    if sys.argv[3] == "true":
        print("checking for anonymous columns...")
        anon_call_check = True    
    else:
        print("skipping anonymous column checks...")
        anon_call_check = False

registry = {
            "url": "file://" + regpath, 
            "localDocRoot": "'" + regpath + "'", 
            "verifyConfig": {
                "nopVerify": True
                }
            }

iql = StackQL(exe='./stackql', registry=json.dumps(registry))

print(iql.version())

# SHOW SERVICES
iql_query = "SHOW SERVICES IN %s" % provider

print("running %s..." % iql_query)
try:
    services = pd.read_json(iql.execute(iql_query))[['name']].copy()
except:
    print("ERROR [%s]" % iql_query)

# SHOW RESOURCES
for serviceIx, serviceRow in services.iterrows():
    service = serviceRow['name']
    iql_query = "SHOW EXTENDED RESOURCES IN %s.%s" % (provider, service)
    print("running %s..." % iql_query)
    try:
        resources = pd.read_json(iql.execute(iql_query))[['name']].copy()
    except:
        print("ERROR [%s]" % iql_query)
        print(iql.execute(iql_query))
        break
    for resIx, resRow in resources.iterrows():
        resource = resRow['name']
        # DESCRIBE RESOURCE
        iql_desc_query = "DESCRIBE EXTENDED %s.%s.%s" % (provider, service, resource)
        # get FQRP length
        fqrn_len = len("%s.%s.%s" % (provider, service, resource))
        # if fqrn_len > 55:
        #     err_str = "WARN [%s] - FQRN too long" % iql_desc_query
        #     print('------------------')
        #     print(err_str)
        #     print('------------------')
        #     # raise Exception(err_str)
        print("running %s... (length: %s)" % (iql_desc_query, str(fqrn_len)))
        try:
            desc = pd.read_json(StringIO(iql.execute(iql_desc_query)))
            # collist = desc['name'].tolist()
            # if len(collist) < 4:
            #     print("--------------------")
            #     print("[CHECK] %s" % str(collist))
            #     print("--------------------")
            if anon_call_check:
                # column_anon check (azure)
                print("checking for anon cols in %s.%s.%s" % (provider, service, resource))
                for colIx, colRow in desc.iterrows():
                    if colRow['name'] == 'column_anon':
                        raise Exception("column_anon in %s.%s.%s" % (provider, service, resource))    
            print("[OK] %s" % iql_desc_query)
        except:
            query_result = iql.execute(iql_desc_query)
            if 'SHOW METHODS' not in query_result:
                print("")
                print("--------------------")
                print("[ERROR] %s" % query_result)
                print("%s.%s.%s" % (provider, service, resource))
                print("--------------------")
                print("")
                raise Exception(query_result)
            else:
                print("[N/A] %s" % iql_desc_query)
            pass

        # SHOW METHODS
        iql_desc_query = "SHOW EXTENDED METHODS IN %s.%s.%s" % (provider, service, resource)
        print("running %s..." % iql_desc_query)
        try:
            resp = json.loads(iql.execute(iql_desc_query))
            print("[OK] %s" % iql_desc_query)
        except:
            query_result = iql.execute(iql_desc_query)
            print("")
            print("--------------------")
            print("[ERROR] %s" % query_result)
            print("%s.%s.%s" % (provider, service, resource))
            print("--------------------")
            print("")
            raise Exception(query_result)

        # SHOW INSERT INTO
        if (service == 'na' and resource == 'na'):
            print("skipping %s.%s.%s" % (provider, service, resource))
            pass
        else:
            iql_desc_query = "SHOW INSERT INTO %s.%s.%s" % (provider, service, resource)
            print("running %s..." % iql_desc_query)
            try:
                resp = json.loads(iql.execute(iql_desc_query))
                print("[OK] %s" % iql_desc_query)
            except:
                query_result = iql.execute(iql_desc_query)
                if query_result.startswith('Cannot find matching operation'):
                    pass
                elif query_result.startswith('error creating insert statement'):
                    print(query_result)
                    pass
                else:
                    print("")
                    print("--------------------")
                    print("[ERROR] %s" % query_result)
                    print("%s.%s.%s" % (provider, service, resource))
                    print("--------------------")
                    print("")
                    raise Exception(query_result)
