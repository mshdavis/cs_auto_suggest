# AUTOSUGGESTION SERVER README

## Generating Data

The build_data.py script is used to generate the dataset(s) consumed by the server. It takes no arguments. 

`python build_data.py`

## Starting the Server

The server.py script is used to start the uwsgi server. It can take one input (-f) if you'd like to pass in a specific json file. It defaults to trigram_filtered.json.

`python server.py [-f brute_force.json]`

## Querying the Server

The server defaults to port 5000. A GET request to the autosuggest endpoint will return a response. This can be done either via curl or a browser.

`http://127.0.0.1:5000/autosuggest?q=how%20ca`
`http://127.0.0.1:5000/autosuggest?q=When+did`
