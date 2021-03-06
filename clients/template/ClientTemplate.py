import flask
from flask import request, jsonify
import requests
from multiprocessing.dummy import Pool


# Flask config
app = flask.Flask(__name__)
app.config["DEBUG"] = True
local_port = 12000

# Other client URL config
addr_oo = "localhost:11500"
addr_mo_server = "localhost:11600"
addr_mo_user_api = "localhost:11620"
addr_dc = "localhost:11700"
addr_user = "localhost:11800"
addr_agg = "localhost:11900"


# HF connection config
addr_hf_api = "localhost:4000"
hf_token = None
org_id = str(1)  # TODO: change this appropriatly
# See /fabric/api-2.0/quicktest_api.py for example how to contact HF API via python


# Helper code
pool = Pool(10)

"""
Function to call a HTTP request async and only printing the result.
to_get: Bool, True = GET, False = POST
url: string URL to call
data: list/dict for POST data
headers: list/dict of headers
params: list/dict for GET params
"""
def fire_and_forget(to_get, url, data=[], headers=[], params=[]):
    # Example: fire_and_forget(True, "https://www.google.com/")

    def on_success(r):
        if r.status_code == 200:
            print(f'Call succeed: {r}')
        else:
            print(f'Call failed: {r}')

    def on_error(ex: Exception):
        print(f'Requests failed: {ex}')

    if to_get:
        pool.apply_async(requests.get, (url,), {'params': params, 'headers': headers},
                         callback=on_success, error_callback=on_error)
    else:
        pool.apply_async(requests.post, (url,), {'data': data, 'headers': headers},
                         callback=on_success, error_callback=on_error)


"""
Returns a HF API token needed for communication.
return: string of token
"""
def register_hf_api_token():
    # NOTE: not tested fully
    url_users = addr_hf_api + "/users"
    org_str = "Org" + str(org_id)
    username = "default_user"
    json_users = {"username": username, "orgName": org_str}
    r = requests.post(url_users, data=json_users)
    token = r.json()['token']
    r.close()
    return token


"""
Function to invoke (= HTTP POST) something from a chaincode via the HF API.
token: token which is returned by register_hf_api_token
chaincode_name: name of chaincode
function: function name
args: list of string args
returns: json of response
"""
def hf_invoke(token, chaincode_name, function, args):
    # NOTE: not tested fully
    url_post = addr_hf_api + "/channels/mychannel/chaincodes/" + chaincode_name
    body = {"fcn": function,
            "peers": "peer0.org" + org_id + ".example.com",
            "chaincodeName": chaincode_name,
            "channelName": "myChannel",
            "args": args}
    headers = {"Authorization": "Bearer " + token}
    r = requests.post(url_post, data=body, headers=headers)
    return r.json()


"""
Function to get something from a chaincode via the HF API.
token: token which is returned by register_hf_api_token
chaincode_name: name of chaincode
function: function name
args: list of string args
returns: json of response
"""
def hf_get(token, chaincode_name, function, args):
    # NOTE: not tested fully
    headers = {"Authorization": "Bearer " + token}
    params = {"args": args,
              "peer": "peer0.org" + org_id + ".example.com",
              "fcn": function}
    url_req = addr_hf_api + "/channels/mychannel/chaincodes/" + chaincode_name
    r = requests.get(url_req, headers=headers, params=params)
    return r.json()


"""
Helper function to invoke async operations i.e. you call the function but do not wait for the response.
function: reference to function to call
args: tuple of args to pass to function
"""
def invoke_async_function(function, args):
    pool.apply_async(function, args)


# Logic class
class TemplateLogic(object):

    def __init__(self):
        self.internal_var = None

    def set_var(self, new_value):
        # Do some processing or whatever
        self.internal_var = new_value

    def get_var(self):
        # Do some processing or whatever
        return self.internal_var


# Logic instance
logic = TemplateLogic()


# Endpoint management

@app.route('/get_value/', methods=['GET'])
def get_value():
    return jsonify(internal_var=logic.get_var())


@app.route('/set_value/', methods=['POST'])
def set_value():
    try:
        # If you need to do other HTTP calls, use fire_and_forget
        body = request.get_json(force=True)
        new_val = body['new_val']
        print("New value: " + str(new_val))
        logic.set_var(new_val)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(error=str(e))


@app.errorhandler(500)
def page_not_found(e):
    return jsonify(error=str(e))


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e))


@app.errorhandler(403)
def page_not_found(e):
    return jsonify(error=str(e))


if __name__ == '__main__':
    hf_token = register_hf_api_token()  # TODO: test
    app.run(port=local_port)

