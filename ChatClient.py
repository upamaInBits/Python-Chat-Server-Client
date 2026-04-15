import json
import signal  # For handling Ctrl-C
import threading
from socket import *

from colorama import Fore, Style, init

init(autoreset=True)  # Initialize colorama for automatic style resets

# Set up the client socket
server_port = 12000  # Define the server port
client_socket = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
client_socket.connect(("localhost", server_port))  # Connect to the server


def receive_messages():
    """Receives messages from the server and prints them to the console."""
    buffer = ""  # Initialize an empty buffer

    while True:
        try:
            response = client_socket.recv(2048).decode()  # Receive data from the server
            buffer += response  # Add the received data to the buffer

            while buffer:  # Keep processing while there's data in the buffer
                try:
                    message, index = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[
                        index:
                    ]  # Remove the processed message from the buffer

                    # Handle different message types
                    if message["type"] == "server_message":  # Server messages
                        print(Fore.GREEN + message["message"] + Style.RESET_ALL)
                    elif message["type"] == "chat_message":  # Chat messages
                        print(
                            Fore.CYAN
                            + f"{message['sender']}: {message['message']}"
                            + Style.RESET_ALL
                        )
                    elif message["type"] == "private_message":  # Private messages
                        if "sender" in message:
                            print(
                                Fore.YELLOW
                                + f"PRIVATE MESSAGE from {message['sender']}: {message['message']}"
                                + Style.RESET_ALL
                            )
                        else:
                            print(
                                Fore.YELLOW
                                + f"PRIVATE MESSAGE to {message['receiver']}: {message['message']}"
                                + Style.RESET_ALL
                            )
                    elif message["type"] == "help":  # Help message
                        print(Fore.BLUE + message["message"] + Style.RESET_ALL)
                    elif message["type"] == "list":  # List channels
                        if message["message"]:
                            print(Fore.MAGENTA + message["message"] + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "No channels available." + Style.RESET_ALL)

                except json.JSONDecodeError:
                    # Incomplete message, break the inner loop and wait for more data
                    break

        except:  # Handle any exceptions during message receiving
            break


def send_message(message_type, **kwargs):
    """Sends a message to the server with the given type and data."""
    message = {"type": message_type}  # Create a dictionary with the message type
    message.update(kwargs)  # Add any additional data to the message
    client_socket.send(json.dumps(message).encode())  # Send the JSON encoded message


def signal_handler(sig, frame):
    """Handles the Ctrl-C (KeyboardInterrupt) signal for graceful shutdown."""
    print(
        Fore.RED
        + "\nCtrl-C detected. Disconnecting from server gracefully..."
        + Style.RESET_ALL
    )
    send_message("quit")  # Notify the server that the client is disconnecting
    client_socket.close()  # Close the client socket
    exit(0)  # Exit the program


# Register the signal handler for Ctrl-C
signal.signal(signal.SIGINT, signal_handler)

# Create and start a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Main loop for sending messages to the server
while True:
    message = input()  # Get user input
    try:
        if message.startswith("/connect"):  # Connect to the server
            parts = message.split()
            send_message(
                "connect",
                server_name=parts[1],
                port=int(parts[2]) if len(parts) > 2 else None,
            )
        elif message.startswith("/join"):  # Join a channel
            send_message("join", channel_name=message.split("/join")[1].strip())
        elif message.startswith("/leave"):  # Leave a channel
            send_message("leave")
        elif message.startswith("/nick"):  # Change nickname
            send_message("nick", nickname=message.split("/nick")[1].strip())
        elif message.startswith("/list"):  # List channels
            send_message("list")
        elif message.startswith("/msg"):  # Send a private message
            parts = message.split()
            send_message(
                "msg", target_nickname=parts[1], private_message=" ".join(parts[2:])
            )
        elif message.startswith("/quit"):  # Quit the chat
            send_message("quit")
            print(Fore.RED + "Disconnecting from server..." + Style.RESET_ALL)
            break  # Exit the loop after sending the quit message
        elif message.startswith("/help"):  # Get help
            send_message("help")
        else:  # Send a normal chat message
            send_message("chat_message", message=message)
    except Exception as e:  # Handle any exceptions during message sending
        print(Fore.RED + f"Error sending message: {e}" + Style.RESET_ALL)
