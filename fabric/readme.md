# BasicNetwork-2.0
Fork of https://github.com/adhavpavan/BasicNetwork-2.0
Initial hyperledger fabric setup for team NEC

# View Blockchain explorer
Navigate to the following address in your browser:
```
localhost:8080
```

# Manual Api Set-up

Assuming the network is running using `bash start_network.sh`, execute the following command.
```
cd fabric/api-2.0
npm run start 4000 clean
```
Note, the last two parameters can be left out (defaults to no cleaning of old files and port 40000).

Then in another terminal, use the `quicktest_api.py` script to try out various commands from the command line (Note: it needs the `requests` pip package).
Usage:
```
python3 quicktest_api.py <port> <username> 1|2|3(org id) req|post <chaincode> <function_name> <function params>...
```

Examples:
```
python3 quicktest_api.py 4000 nikita 1 req fabcar queryAllCars []
python3 quicktest_api.py 4000 nikita 1 post fabcar createCar "CAR14" "Tesla" "F1-Reloaded" "White" "nikitaorg2"
```


# Known issues
```
"tool x" is not recognised as a bash command
```
Add hyperledger Fabric binaries to the class path

```
Script is not executable
```
Set script as executable in your file system
```
chmod +x filename.sh
```

# Manual setup

See `start_network.sh` for the steps needed to start the full network.

To setup network first run. This generetates the cryptomaterial (genesis blocks, certificates):
```
bash ./setup_network.sh
```

To deploy a contract run:
```
./deployChaincode.sh ./artifacts/src/github.com/fabcar/javascript fabcar 1 initLedger []
```

Where the first argument is the path to the chaincode, the second is the chaincode name, third is version. Finally the 4th and 5th are optinal and execute a function (literal name) with the following arguments (JSON array) 


First make sure that `setup_network.sh` was run before. Then manage all certs with the following python scripts.
```
python3 generate_certificates.py 1
python3 generate_certificates.py 2
python3 generate_certificates.py 3
```


# Basic Manual Setup

1. Create cryptomaterial
```
./artifacts/channel/create-artifacts.sh
```
2. Start docker compose network
```
cd ./artifacts/
docker compose up -d
```
3. Create channel
```
./createChannel.sh
```
5. Check that all peers have joined the channel
```
docker ps
docker exec -it org0.peer... sh
peer channel list
```
6. Deploy chaincode
```
./deployChaincode.sh ./artifacts/src/github.com/fabcar/javascript fabcar
```
# Deploying Chaincode

Usage:
```
./deployChaincode.sh <PATH TO SMART CONTRACT> <NAME OF SMART CONTRACT>
```

