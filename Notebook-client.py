# This is the client's side of the notebook system, including the interfaces and input boxes.
# Failures are properly handled.

import requests

server_url = "http://localhost:8080" # Defines the base URL of the Flask server.

# Interface and sender for function 1.
def add_note():
    topic = input("Input the topic: ")
    name = input("Input the note's name: ")
    text = input("Input the text of the note: ")
    data = {'topic': topic, 'name': name, 'text': text} # Packs the input into a dictionary.
    response = requests.post(f"{server_url}/add_note", json=data) # Sends a POST request to add the note to the server.
    print(response.json()) # Prints the response from the server for users to check.

# Interface and sender for function 2.
def get_notes():
    topic = input("Input the topic to retrieve: ")
    response = requests.get(f"{server_url}/get_notes", params={'topic': topic}) # Sends a GET request to retrieve notes.
    if response.status_code == 200:
        notes = response.json() # Parses the JSON response containing the notes.
        if isinstance(notes, list): # Checks if the response is a list, which is the expected format for notes.
            for note in notes:
                print(f"{note['name']}: {note['text']} (Timestamp: {note['timestamp']})\n") # Prints details of each note.
        else:
            # Handles failure raised by the response is not a list (e.g., an error message).
            print(notes.get('message', 'An error occurred\n'))
    else:
        # Raise an error when the queried note topic does not exist.
        print(f"Error: Server responded with status code {response.status_code}.\nThis error is likely to raise when you are query a topic that does not exist, or the queried topic has no note.\n")

# Interface and sender for function 3.
def delete_note():
    topic = input("Input the topic of the note to delete: ")
    name = input("Input the name of the note to delete: ")
    data = {'topic': topic, 'name': name} # Packs the topic and name into a dictionary.
    response = requests.post(f"{server_url}/delete_note", json=data) # Sends a POST request to delete the specific note.
    print(response.json())

# Interface and sender for function 4.
def add_wiki_info():
    topic = input("Input the topic to append Wikipedia info to: ")
    search_term = input("Input the search term for Wikipedia: ")
    data = {'topic': topic, 'search_term': search_term} # Packs the topic and search term into a dictionary.
    response = requests.post(f"{server_url}/add_wiki_info", json=data) # Sends a POST request to append Wikipedia searching results.
    print(response.json())

# Interface and sender for function 5.
def delete_all_notes():
    topic = input("Input the topic to delete all notes from: ")
    data = {'topic': topic} # Packs the topic into a dictionary.
    response = requests.post(f"{server_url}/delete_all_notes", json=data) # Sends a POST request to delete all notes under a topic.
    print(response.json())

# The main user interface, where users are able to choose the function by inputing their names.
while True:
    action = input('''The system supports the following functions:
1. Add a note (input 'add');
2. Get a note based on its topic (input 'get');
3. Delete the first note with a topic (input 'delete');
4. Delete all the notes with a topic (input 'delete all');
5. Wiki a term (input 'wiki');
6. Exit (input 'exit').
Input your need here: ''')
    if action == 'add':
        add_note()
    elif action == 'get':
        get_notes()
    elif action == 'delete':
        delete_note()
    elif action == 'wiki':
        add_wiki_info()
    elif action == 'delete all':
        delete_all_notes()
    elif action == 'exit':
        break
    else:
        print("Invalid input.")
