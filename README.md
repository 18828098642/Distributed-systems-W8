# Distributed-systems-Assignment 2

This repository includes the python files needed for the assignment 2 for course Distributed Systems：Notebook application based on XML.

The files are one program for server's side, the main functions supporting the system;

One program for client's side, the interfaces for inputs, and senders that connects servers;

One script for testing the system's capability to handle multiple concurrent inputs.

5 functions are developed: Add a note, get a note based on its topic and name, delete a note based on its topic and name, delete all note under a given topic, and wiki search for a given term, and append to a given topic.

Note that when the name for the note to be deleted is not unique in the XML database, the first note with the name will be deleted.

Failures are properly handled.

How does the developed program address the challenges of distributed systems?

Heterogeneity: The server and client communicate over HTTP using JSON, which is universally supported across different platforms, programming languages, and environments. This ensures that the various heterogeneous components can interoperate seamlessly.

Openness: The server is defined with a clear API with endpoints for adding, retrieving, deleting notes, and Wiki search function. This allows for the addition or replacement of components without impacting the overall system. For example, a new client application could be developed and interact with the server without requiring changes to the server itself.

Security: The way how the server validates requests (e.g., checking for the existence of topics or notes before performing operations) and other operations are well protected from errors, which may cause the crush of the entire system.

Scalability: The simple Flask server is suitable for handling a moderate load of user operations, and the developed system has passed the concurrent loading test for 5 concurrent input, exhibiting good scalability.

Failure Handling: The server application includes comprehensive error handling (e.g., returning appropriate error messages when a requested note or topic does not exist). This helps in ensuring that failures in one component (such as a bad request from a client) do not crash the entire system. 

Transparency: The client interacts with the server through a simple API without needing to know about the underlying implementation details, such as how and where the notes are stored. This hides the distributed nature of the system from the clients, allowing them to focus on the functionality rather than the complexities of distributed data management.

- Zixuan Zhong
- 000834360
