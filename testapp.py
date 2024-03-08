# This is a testing script for the notebook system.
# By using the concurrent.futures.ThreadPoolExecutor module, the script can make multiple concurrent POST requests to the server,
# which resembles multiple user inputs to the system, to test if the system is able to handle multiple client requests at once.

import requests
from concurrent.futures import ThreadPoolExecutor # Imports ThreadPoolExecutor for concurrent execution.

server_url = "http://localhost:8080/add_note" # Sets the URL to which the POST requests will be sent.

# The function that sends POST request to the server.
def send_request():
    # Parse the data to be sent in the POST request to a dictionary.
    data = {'topic': 'Concurrent Test', 'name': 'Test Note', 'text': 'This is a test note.'}
    response = requests.post(server_url, json=data) # Sends a POST request to the server URL with the specified data in JSON format.
    try:
        print(response.json()) # Try to parse the JSON response and print it.

    # Handle the error if the response cannot be decoded as JSON.
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON from response: {response.text}, status code: {response.status_code}")


# Creates a ThreadPoolExecutor as a context manager with 5 worker threads,
# and submits the send_request function to be executed 5 times concurrently.
# This creates 5 futures representing the outcomes of the submitted function calls.

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_request) for _ in range(5)]

# Wait for all the requests to complete.
for future in futures:
    future.result()
