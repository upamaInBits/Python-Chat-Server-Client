import json  # Import the json module for encoding and decoding JSON data


class Client:
    """Represents a client connected to the chat server."""

    def __init__(self, socket):
        """Initializes a new Client object."""
        self.socket = socket  # The client's socket object
        self.channel = (
            None  # The channel the client is currently in (None if not in any channel)
        )
        self.nickname = (
            self.socket.getpeername()
        )  # The client's nickname (initially set to their address)


class Channel:
    """Represents a chat channel."""

    def __init__(self, name):
        """Initializes a new Channel object."""
        self.name = name  # The name of the channel
        self.clients = []  # The list of clients in the channel


def broadcast(client_socket, message, channel):
    """Broadcasts a message to all clients in a channel except the sender."""
    for client in channel.clients:  # Iterate over all clients in the channel
        if client.socket != client_socket:  # If the client is not the sender
            try:
                # Encode the message as JSON and send it to the client
                client.socket.send(json.dumps(message).encode())
            except Exception as e:  # Handle any exceptions during sending
                print(f"Error broadcasting message: {e}")


# Global lists to store channels and clients
channels = []  # The list of channels
clients = []  # The list of clients


# Help message to be sent to clients
help_msg = {
    "type": "help",  # Message type is 'help'
    "message": f"""  # The actual help message content
{"=" * 80}
{"/" * 80}
{"=" * 80}

/connect <server-name> [port#] - Connect to named server (port# optional)
/nick <nickname> - Pick a nickname (should be unique among active users)
/join <channel> - Join a channel
/leave [<channel>] - Leave the current (or named) channel
/list - List channels and number of users
/msg <nickname> <message> - Send a private message to a user
/help - Print out this help message

{"=" * 80}
{"/" * 80}
{"=" * 80}
""",
}
