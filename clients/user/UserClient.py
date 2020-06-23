import flask
from flask import request, jsonify
import requests
from multiprocessing.dummy import Pool
import json


# Flask config
app = flask.Flask(__name__)
app.config["DEBUG"] = True
local_port = 11800

# Other client URL config
addr_oo = "http://localhost:11500"
addr_mo_server = "http://localhost:11600"
addr_mo_user_api = "http://localhost:11620"
addr_dc = "http://localhost:11700"
addr_user = "http://localhost:11800"
addr_agg = "http://localhost:11900"


# HF connection config
addr_hf_api = "http://localhost:4000"
org_id = str(1)  # TODO: needs to be changed to ??????????


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
#NOTHING TESTED
class UserClientLogic(obejct):

    def __init__ (self):
        self.hf_api_token = None  # str - String of HF API token
        self.data = "text_data" # str - String of data generated by user, to be preprocessed and sent to OO
        self.wallet = None # str - String containing wallet of the user
        self.query_id = None # id - Id of query
        self.query_text = None # Str - Query text


    def notifyUser(self):
        #TODO: for GUI

    def send_data_to_Aggregator(self):
        #send the dummy data to the aggregator

        aggregator_endpoint = addr_agg + "/receiveData"
        json_data = {"data": data, "userWalletID": wallet, "query_id": query_id}
        fire_and_forget(False, aggregator_endpoint, json_data)

    def accept_query(self):
        #tell MO that the User accepts the query

        MO_endpoint = addr_mo_server + "/accept"
        fire_and_forget(True, MO_endpoint, [query_id])

    def preprocessData(self, data):
        #TODO: when we will have real data
        return data

# Logic instance
logic = UserClientLogic()


# Endpoint management
#NOTHING TESTED
@app.route('/sendData/', methods=['POST'])
def send_data_to_Aggregator():
    #just call logic's function

    logic.send_data_to_Aggregator()


@app.route('/notify/', methods=['POST'])
def get_notified_for_query():
    #get notified by the MO about the query, also get the query's ID and text

    try:
        body = request.get_json(force=True)
        logic.query_id = body['query_id']
        logic.query_text = body['query_text']
        
        return jsonify(succes=True)
    except Exception as e:
        return jsonify(erorr = str(e))
    
@app.route('/acceptQuery/', methods=['POST'])
def accept_query():
    #just call logic's function

    logic.accept_query()

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
    hf_token = register_hf_api_token()
    logic.hf_api_token = hf_token
    app.run(port=local_port)