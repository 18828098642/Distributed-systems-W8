# Intro:
# This is the server's side of the notebook system. It allows clients to perform operations such as adding notes, retrieving notes, deleting notes,
# appending Wikipedia information to notes, and deleting all notes under a specific topic.
# This system uses an XML file (notes.xml) as a simple database to store and manage the notes, which is organized by topics.
# This system adopted Flask module, which allows for creating, retrieving, and deleting notes, as well as integrating with Wikipedia to add information to notes.
# All the possible failures are properly handled, including non-existence of the XML file, and the non-existence of the queried topic, and non-existence of queried name etc.

# Import necessary libraries
import requests
from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from datetime import datetime
import threading
from urllib.parse import quote

# Creates an instance of the Flask class.
app = Flask(__name__)

# Creates a reentrant lock to ensure thread-safe operations on the XML database.
lock = threading.RLock()

# Loading the XML database if there is one, initialize the XML database if there isn't one.
try:
    tree = ET.parse('notes.xml')
    root = tree.getroot()
except Exception as e:
    root = ET.Element('data')

# Function 1: Add a note with a given note topic, note name and note content.
@app.route('/add_note', methods=['POST'])
def add_note():
    global root, tree

    with lock: # Locks the code block to ensure thread-safe operations. This facilitates the handling of multiple inputs.
        try:
            # Load the notes.xml file.
            tree = ET.parse('notes.xml')
            root = tree.getroot()

        # If the file doesn't exist, creates a new 'data' root element.
        except FileNotFoundError:
            root = ET.Element('data')

        data = request.json
        topic = data['topic']
        name = data['name']
        text = data['text']
        timestamp = datetime.now().strftime("%m/%d/%y - %H:%M:%S")

        # Checks if the topic already exists in the XML tree.
        topic_exists = root.find(f".//topic[@name='{topic}']")
        if topic_exists is None: # If not, creates a new 'topic' element.
            topic_element = ET.SubElement(root, 'topic', name=topic)
        else:
            topic_element = topic_exists

        # If yes, creates a new 'note' element under the topic.
        note_element = ET.SubElement(topic_element, 'note', name=name)
        ET.SubElement(note_element, 'text').text = text
        ET.SubElement(note_element, 'timestamp').text = timestamp

        tree = ET.ElementTree(root)
        tree.write('notes.xml')

    return jsonify({'message': 'Note added successfully'}), 200

# Function 2: Get all the notes under a given topic.
@app.route('/get_notes', methods=['GET'])
def get_notes():
    topic = request.args.get('topic') # Gets the topic from the query parameters of the GET request.

    with lock:
        try:
            # Load the notes.xml file.
            tree = ET.parse('notes.xml')
            root = tree.getroot()

        # If the file is not found, returns an error.
        except FileNotFoundError:
            return jsonify({'message': 'Database not found'}), 404

        # Searches for the specified topic in the XML document.
        topic_element = root.find(f".//topic[@name='{topic}']")
        if topic_element is None: # Returns an error if the topic doesn't exist.
            return jsonify({'message': f'Topic "{topic}" not found'}), 404

        # Create an empty list to hold the node contents and appends each note's details to the list.
        notes = []
        for note in topic_element.findall('note'):
            notes.append({'name': note.get('name'), 'text': note.find('text').text, 'timestamp': note.find('timestamp').text})

    return jsonify(notes), 200

# Function 3: Delete the note under a given topic. If multiple notes are with the same name, the first created note among them will be deleted.
@app.route('/delete_note', methods=['POST'])
def delete_note():
    with lock:
        tree = ET.parse('notes.xml')
        root = tree.getroot()

        data = request.json
        topic = data['topic']
        name = data['name']

        # Locate the specified topic.
        topic_element = root.find(f".//topic[@name='{topic}']")
        if topic_element is not None:
            # Find and remove the specified note within the topic.
            note_element = topic_element.find(f"./note[@name='{name}']")
            if note_element is not None:
                topic_element.remove(note_element)
                # After removing the note, check if there are no more notes under the topic.
                if not list(topic_element):  # If the topic has no more note elements.
                    root.remove(topic_element)  # Remove the topic from the root.
                tree.write('notes.xml')
                return jsonify({'message': 'Note deleted successfully'}), 200
            else:
                return jsonify({'message': 'Note not found'}), 404 # Raise an error when the given name of the note does not match any of the existing ones.
        else:
            return jsonify({'message': 'Topic not found'}), 404 # Raise an error when the given topic does not match any of the existing ones.

# Function 4: Search for the given term on Wikipedia and add the first 3 urls of the searched result to the given topic.
@app.route('/add_wiki_info', methods=['POST'])
def add_wiki_info():
    global root, tree
    data = request.json
    topic = data['topic'] # Extracts the 'topic' to which Wikipedia info will be added.
    search_term = data['search_term'] # Extracts the 'search_term' used for querying Wikipedia.

    with lock:
        try:
            tree = ET.parse('notes.xml')
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('data')

        # URL-encodes the search term for safe inclusion in the query URL.
        search_term_quoted = quote(search_term)
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={search_term_quoted}&format=json"

        # URL for querying the Wikipedia API.
        try:
            response = requests.get(url)
            response.raise_for_status()  # Failure handling: Raises an exception for HTTP errors.

            search_results = response.json()['query']['search'] # Extracts search results from the response.
            if search_results:
                added_urls = []
                for index, result in enumerate(search_results[:3], start=1):  # Set the getting number of wiki urls to 3.
                    page_id = result['pageid']
                    wiki_url = f"https://en.wikipedia.org/?curid={page_id}"
                    added_urls.append(wiki_url)

                    # Construct the query for wiki.
                    topic_exists = root.find(f".//topic[@name='{topic}']")
                    if topic_exists is None:
                        topic_element = ET.SubElement(root, 'topic', name=topic)
                    else:
                        topic_element = topic_exists
                    note_element = ET.SubElement(topic_element, 'note',
                                                 name=f'Wikipedia Link {index} for {search_term}')
                    ET.SubElement(note_element, 'text').text = wiki_url
                    ET.SubElement(note_element, 'timestamp').text = datetime.now().strftime("%m/%d/%y - %H:%M:%S")

                # Adds a new note to the topic with the Wikipedia link.
                tree = ET.ElementTree(root)
                tree.write('notes.xml')

                return jsonify({'message': 'Wikipedia links added successfully', 'wiki_urls': added_urls}), 200
            else:
                return jsonify({'message': 'No Wikipedia article found for the search term'}), 404

        except requests.RequestException as e:
            app.logger.error(f"Error querying Wikipedia API: {e}")
            return jsonify({'message': 'Failed to query Wikipedia'}), 500 # Raise an error when the query of Wikipedia fails.
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return jsonify({'message': 'An unexpected error occurred'}), 500 # Raise an error when other failures occur.

# Function 5: Delete all the notes under a given topic.
@app.route('/delete_all_notes', methods=['POST'])
def delete_all_notes():
    global root, tree
    data = request.json
    topic = data['topic'] # Extracts the 'topic' from which all notes will be deleted.

    with lock:
        try:
            tree = ET.parse('notes.xml')
            root = tree.getroot()
        except FileNotFoundError:
            return jsonify({'message': 'Database not found'}), 404 # Raise an error if the file doesn't exist.

        # Looks for the specified topic and delete all the notes under it.
        topic_element = root.find(f".//topic[@name='{topic}']")
        if topic_element is not None:
            root.remove(topic_element)  # Removes the entire topic element if found.
            tree.write('notes.xml')  # Saves the updated XML document.
            return jsonify({'message': f'All notes under topic "{topic}" have been deleted successfully'}), 200
        else:
            return jsonify({'message': 'Topic not found'}), 404 # Raise an error when the given topic is not found.


if __name__ == '__main__':
    app.run(debug=True, port=8080) # Starts the Flask application on port 8080 with debug mode enabled.
