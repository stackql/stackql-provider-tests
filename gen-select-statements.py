# nohup ./stackql --pgsrv.port=5444 srv &
# python3 gen-select-statements.py github

import sys, datetime, json

provider = sys.argv[1]

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

def run_query(query):
    if query.find("SELECT") == 0:
        print("%s" % query)
    try:
        r = conn.execute(query)
        data = r.fetchall()
        return pd.DataFrame([i.copy() for i in data])
    except Exception as e:
        print("ERROR [%s]" % str(e))
        return pd.DataFrame()
        # if str(e).find("HTTP response error.  Status code 409.") == 0:
        #     return
        # if str(e).find("sql insert error") == 0:            
        #     return
        # if str(e).find("no matching operation was found") == 0:            
        #     return
        # sys.exit(1)

# REGISTRY PULL
iql_reg_query = "REGISTRY PULL %s" % provider
conn.execute(iql_reg_query)

# SHOW SERVICES
iql_services_query = "SHOW SERVICES IN %s" % provider
services = run_query(iql_services_query)

# SHOW RESOURCES
for serviceIx, serviceRow in services.iterrows():
      service = serviceRow['name']
      iql_resources_query = "SHOW EXTENDED RESOURCES IN %s.%s" % (provider, service)
      resources = run_query(iql_resources_query)
      for resIx, resRow in resources.iterrows():
            resource = resRow['name']

            if resource not in ['statistics_code_frequency', 'statistics_punch_cards']:

                # SHOW METHODS
                iql_methods_query = "SHOW EXTENDED METHODS IN %s.%s.%s" % (provider, service, resource)
                methods = run_query(iql_methods_query)

                if len(methods.query("SQLVerb == 'SELECT'")) > 0:
                    print('*******')
                    print("%s.%s.%s" % (provider, service, resource))
                    print('*******')
                    
                    iql_desc_query = "DESCRIBE EXTENDED %s.%s.%s" % (provider, service, resource)
                    desc = run_query(iql_desc_query)
                    print(desc)
                    print('')
                    print('-----------------')

                for methodIx, methodRow in methods.iterrows():
                    if methodRow['SQLVerb'] == 'SELECT':
                        if methodRow['RequiredParams']:
                            params_list = methodRow['RequiredParams'].replace(' ','').split(',')
                            where_clause = " AND ".join(["%s = ''" % p for p in params_list])
                            where_clause = where_clause.replace("org = ''", "org = 'stackql'") 
                            where_clause = where_clause.replace("repo = ''", "repo = 'stackql'") 
                            where_clause = where_clause.replace("owner = ''", "owner = 'stackql'") 
                            where_clause = where_clause.replace("username = ''", "username = 'jeffreyaven'") 
                            where_clause = where_clause.replace("team_slug = ''", "team_slug = 'stackql-dev'") 
                            select_query = "SELECT * FROM %s.%s.%s WHERE %s" % (provider, service, resource, where_clause)
                            if where_clause.find("= ''") == -1:
                                res = run_query(select_query).head(1)
                                # res.info(verbose=True)
                                # print(res.head(5))
                                result = res.to_json(orient="records")
                                parsed = json.loads(result)
                                print(json.dumps(parsed, indent=2))
                                print('')
                                print('-----------------')
                        else:
                            print("SELECT * FROM %s.%s.%s" % (provider, service, resource))
                            res = run_query(select_query).head(1)
                            # res.info(verbose=True)
                            # print(res.head(5))
                            result = res.to_json(orient="records")
                            parsed = json.loads(result)
                            print(json.dumps(parsed, indent=2))
                            print('')
                            print('-----------------')

                
# MethodName RequiredParams SQLVerb                                        description

            # if len(methods.query("SQLVerb == 'SELECT'")) > 0:
            #       iql_desc_query = "DESCRIBE EXTENDED %s.%s.%s" % (provider, service, resource)
            #       desc = run_query(iql_desc_query)

print(datetime.datetime.now() - start_time)