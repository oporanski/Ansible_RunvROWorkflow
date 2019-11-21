#!/usr/bin/python

DOCUMENTATION = '''
---
module: run_vro_wf
short_description: Run vRO workflow
version_added: -1.2
author: "Oktawiusz Poranski"

options:
    vro_server:
        description:
            - vRO server url e.g.: 'https://vro.mydomain.com:8281'
        required: True
        
    username:
        description:
            - vRO server username
        required: True
        
    password:
        description:
            - vRO server password 
        required: True
        
    workflow_id:
        description:
            - vRO Workflow ID to run
        required: True
        
    input_values:
        description:
          - Workflow input valuse in CSV form. Only string are supported, e.g.: "value1, value2, value3" 
        required: False
'''

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

def build_payload(input_values, check_mode, module):
    """
    Add new input value to JSQN object
    :param input_values: Input name:value in CVS format 
    :return: payload
    """
    params = []
    if(input_values):
        #module.log(msg='###Input_values: ' + str(input_values))
        #for input_value in input_values:
        for key, value in input_values.iteritems():
            module.log(msg='###Input: ' + str(key) + ', value: ' + str(value))
            val ={"value": {"string":{ "value": str(value)}},"type": "string","name": str(key),"scope": "local"}
            params.append(val)

    if check_mode:
        val ={"value": {"boolean":{ "value": True}},"type": "boolean","name": "test","scope": "local"}
        params.append(val)
    else:
        val ={"value": {"boolean":{ "value": False}},"type": "boolean","name": "test","scope": "local"}
        params.append(val)

    data = {}
    if params:
        data['parameters'] = params

    #module.log(msg='###data JSON: ' + str(data))
    return data

def make_rest_call(url, method, validate_cert, user, pwd, payload=''):
    """
    Make a basic REST Call to a vCenter server
    :param url: full url to call vCenter server url + rest endpoint
    :param method: a REST methot to call now accepting GET and POST 
    :param validate_cert: Check ssl certificates
    :param user: user name 
    :param pwd: user password
    :param payload: JSON formated (string) payload to send with a POST call
    :return: json object or empty string 
    """
    
    if method == "POST":
        headers = {'Content-Type': 'application/json','Accept': 'application/json'}
        if payload!='':
            r = open_url(url,method="POST",headers=headers,validate_certs=validate_cert,data=json.dumps(payload),url_username=user, url_password=pwd, force_basic_auth=True)
        else:
            r = open_url(url,method="POST",headers=headers,validate_certs=validate_cert,url_username=user, url_password=pwd, force_basic_auth=True)

    elif method == "GET":
        headers = {'Accept': 'application/json'}
        r = open_url(url,method="GET",headers=headers,validate_certs=validate_cert,url_username=user, url_password=pwd, force_basic_auth=True)

    response = r.read()
    if response != '':
        data = json.loads(response)
    else: 
        data = ''

    headers = r.headers
    return{'data':data, 'headers':headers}

def main():
    module = AnsibleModule(argument_spec=dict(
             vro_server = dict(type='str', required=True),
             username=dict(type='str', required=True),
             password=dict(type='str', required=True, no_log=True),
             workflow_id=dict(type='str', required=True),
             input_values=dict(type='dict', required=False),
        ),
        supports_check_mode=True
    )

    #GLOBALS
    validate_cert = False

    #GET PARAMS
    server_name = module.params['vro_server']
    user = module.params['username']
    pwd = module.params['password']
    workflow_id = module.params['workflow_id']
    input_values = module.params['input_values']
    check_mode = module.check_mode
    module.log(msg='###check_mode: ' + str(check_mode))
    
    api_endpoint = '/vco/api/workflows/' + workflow_id + '/executions/'
    url_action = server_name + api_endpoint
    payload = build_payload(input_values, check_mode, module)
    ret = make_rest_call(url_action, "POST", validate_cert, user, pwd, payload)

    #WAIT FOR RESULT
    location = ret['headers']['Location']
    #module.log(msg='###location: ' + str(location))
    
    ret = make_rest_call(location, "GET", validate_cert, user, pwd, '')
    module.log(msg='###state: ' + str(ret['data']['state']))
    while True:
        ret = make_rest_call(location, "GET", validate_cert, user, pwd, '')
        #module.log(msg='###state in loop: ' + str(ret['data']['state']))
        if (ret['data']['state'] == 'failed'):
            module.log(msg='###break the loop: ' + str(ret['data']['state']))
            break
        if (ret['data']['state'] == 'completed'):
            module.log(msg='###break the loop: ' + str(ret['data']['state']))
            break

    if ret['data']['state'] == 'completed':
        if check_mode:
            module.exit_json(changed=False, meta=ret['data'])
        else: 
            module.exit_json(changed=True, meta=ret['data'])
    else:
        module.fail_json(msg=ret['data'])


if __name__ == '__main__':
    main()
