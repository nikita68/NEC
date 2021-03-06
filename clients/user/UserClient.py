import flask
from flask import request, jsonify
import requests
from multiprocessing.dummy import Pool
import json
from flask_cors import CORS, cross_origin

# Flask config
app = flask.Flask(__name__)
cors = CORS(app)
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
org_id = str(1)


# Helper code
pool = Pool(10)


# logging
@app.before_request
def store_requests():
    url = request.url
    if "getRequestsHistory" not in url and "getQueryData" not in url:
        logic.requests_log.append(url)



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
        pool.apply_async(requests.post, (url,), {'json': data, 'headers': headers},
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
class UserClientLogic(object):

    def __init__ (self):
        self.hf_api_token = None  # str - String of HF API token
        self.user_id = "u1"  # id - Id of user
        self.data = "text_data"  # str - String of data generated by user, to be preprocessed and sent to OO
        self.wallet_id = "WAL2"  # str - String containing wallet of the user
        self.query_id = "q1"  # id - Id of query
        self.query_text = "test_query_text"  # Str - Query text
        self.received_query = False

        self.requests_log = []

    # NOTHING TO TEST HERE
    def notifyUser(self):
        #TODO: for GUI
        pass

    # TESTED, WORKS CORRECTLY
    def send_data_to_Aggregator(self):
        #send the dummy data to the aggregator

        aggregator_endpoint = addr_agg + "/receiveData/"
        json_data = {"user_data": self.data, "user_wallet_id": self.wallet_id, "query_id": self.query_id}
        fire_and_forget(False, aggregator_endpoint, data=json_data)
        #requests.post(aggregator_endpoint, json=json_data)

    # TESTED, WORKS CORRECTLY
    def accept_query(self):
        #tell MO that the User accepts the query

        MO_endpoint = addr_mo_server + "/acceptQuery/" + self.user_id + '/' + str(self.query_id) + '/'
        #json_data = {"query_id": self.query_id, "user_id": self.user_id}
        response = requests.get(MO_endpoint)
        print("ACCEPT QUERY RETURN")
        print(response)
        print(response.json())
        self.wallet_id = response.json()["wallet_id"]
        print("New wallet id: " + str(self.wallet_id))
        return self.wallet_id

    # NOTHING TO TEST HERE
    def preprocessData(self, data):
        #TODO: when we will have real data
        return data

# Logic instance
logic = UserClientLogic()


# Endpoint management
# TESTED, WORKS CORRECTLY
@app.route('/sendData/', methods=['POST'])
def send_data_to_Aggregator():
    #just call logic's function
    print("Sending data to Aggregator, " + logic.wallet_id)
    logic.send_data_to_Aggregator()
    return jsonify(logic.wallet_id)

# TESTED, WORKS CORRECTLY
@app.route('/notify/', methods=['GET', 'POST'])
def get_notified_for_query():
    #get notified by the MO about the query, also get the query's ID and text

    try:
        body = request.get_json()
        logic.query_id = body['query_id']
        logic.query_text = body['query_text']
        logic.received_query = True
        
        return jsonify(body)
    except Exception as e:
        print(str(e))
        return jsonify(erorr=str(e))
    
# TESTED, WORKS CORRECTLY
@app.route('/acceptQuery/', methods=['POST'])
def accept_query():
    #just call logic's function
    print("ACCEPT QUERY")
    return jsonify(logic.accept_query())
    #return jsonify(succes=True)

# TESTED, WORKS CORRECTLY
@app.route('/cashin/', methods=['POST'])
def cashIn():
    MO_endpoint = addr_mo_server + "/cashinCoins/" + logic.user_id + '/' + '2' + '/'
    # to change reward id
    try:
        response = requests.post(MO_endpoint)
        print(response.json())
        return jsonify(succes=True)
    except Exception as e:
        return jsonify(erorr=str(e))

@app.route('/getQueryData/', methods=['GET'])
def get_query_data():
    if logic.received_query is True:
        return jsonify({"query_id": logic.query_id, "query_text": logic.query_text})
    return jsonify({"query_id": "", "query_text": ""})

@app.route('/getRequestsHistory/', methods=['GET'])
def get_requests_history():
    return jsonify({"requests":logic.requests_log})

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
