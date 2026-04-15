# Chat Server and Client

## Team Members

*   [Saxton Dees]
*   [Upama Thapa Magar]
*   [Emily Wolfe]

## Demo Video

[https://drive.google.com/file/d/1yg6GJQoQHJ9sx_7LDegCyyvGKQu8njTq/view]

## Overview

This project implements a basic chat server and client using Python. The server supports multiple clients connecting over the internet, allowing them to join channels, send private messages, and change their nicknames.

## Reflection 

Building this chat system taught us the basics of network programming, threading, and handling real-time communication. We used threading to manage multiple clients and JSON to structure messages. Creating commands like /join and /msg required testing to make them simple and user-friendly. Team collaboration and regular discussions helped us stay organized and resolve challenges. This project highlighted the value of clear design, testing, and teamwork.                                                                                                         

Team members role - Emily focused on ensuring thread safety in the chat server, implementing argument parsing for the server, and managing debug levels and statements to enhance functionality and usability. Upama worked on improving the user interface by adding features like colored terminal fonts, a graceful shutdown with Ctrl-C, an idle timeout that shuts down the server after three minutes of inactivity, and recorded and edited the five-minute demo video. Saxton handled the core functionalities of the chat system, including message handling, channel management, and client-server communication. The project was a collaborative effort where all team members contributed to testing, maintained open communication, and worked together to create the README file, ensuring a well-documented and functional chat system.

## Features

* **Multiple Clients:** Handles concurrent connections from multiple users.
* **Channels:** Users can join and leave channels to communicate in groups.
* **Private Messaging:**  Users can send private messages to other users.
* **Nickname Changes:** Users can change their nicknames.
* **Command-line Interface:** Simple and easy-to-use command-line interface for both server and client.

## File/Folder Manifest

*   `ChatServer.py`: The chat server implementation.
*   `ChatClient.py`: The chat client implementation.
*   `SharedData.py`: Contains shared data structures (clients, channels) and functions used by both server and client.
*   `CommandHandlers.py`: Contains functions to handle different client commands (join, leave, nick, etc.).
*   `requirements.txt`: Lists the project's Python dependencies.

## Building and Running

//if you are not using the virtual environment, if you are please see instructions under Client 

Use the command python ./ChatServer.py -p 12000 -d 1
The -p is the port number please choose between 1200 and 13000
The -d is the debug level, please choose between 0 for little output and 1 for more debug statements

//if you want to use venv please see instructions under Client 

Use the command python ./ChatClient
This will allow you to connect to the server and message others
Please use the commands: 
/join a
a can be replaced with any word or letter
/leave a
to leave the channel
/nick foobar
to change your name in the server
/quit 
disconnects from server
/msg user: message:
sends a private message to foobar if he is in the same channel
any message you want to send here
it will broadcast to the channel you are in, so to everyone who is in that channel
/help
prints help menu



### Prerequisites

* Python 3.x

### Server

1.  Clone the repository: `git clone <repository_url>`
2.  Navigate to the project directory: `cd chat-server-client`
3.  Create and activate a virtual environment (recommended):
    ```bash
    python3 -m venv venv
    . venv/bin/activate
    ```
4.  Install dependencies: `pip install -r requirements.txt`
5.  Run the server: 
    ```bash
    python ChatServer.py -p <port-number> -d <debug-level> 
    ```
    (e.g., `python ChatServer.py -p 12000 -d 0`)

### Client

1.  Open a **new** terminal window.
2.  Activate the same virtual environment: `source venv/bin/activate`
3.  Run the client: `python ChatClient.py`
4.  You can run multiple clients in separate terminal windows to simulate multiple users.


## Testing

In order to test I used anaconda3 and set up a conda environment with python 3.9 and git installed. I then cloned the project and pulled up multiple terminals in the environment and CDed into the project. I then rant the Server on one and two clients on the other two terminals. At this point we tested the commands and went back and revised when needed. 

##  Development

This project uses `black` and `isort` to maintain code style and consistency.

*   **black:**  Code formatter.
*   **isort:**  Sorts imports alphabetically and separates them into sections.

To format your code, run:

```bash
black .
isort .
