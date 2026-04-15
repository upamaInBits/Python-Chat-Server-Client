import argparse
import json
import signal  # For handling Ctrl-C
import threading
import time
from socket import *

from colorama import Fore, Style, init

from CommandHandlers import *  # Import command handlers
from SharedData import *  # Import shared data (clients, channels, etc.)

lock = threading.Lock()

init(autoreset=True)  # Initialize colorama for automatic style resets

last_activity_time = time.time()  # Initialize with the current time
print(
    Fore.GREEN
    + f"Activity detected. Resetting idle timer: {last_activity_time}"
    + Style.RESET_ALL
)

IDLE_TIMEOUT = 3 * 60  # 3 minutes in seconds


def handle_client(client_socket, debug_level):
    """Handles communication with a single client."""
    global last_activity_time  # Use the global activity tracker

    # Create a Client object and add it to the clients list
    client = Client(client_socket)
    with lock:
        clients.append(client)

    while True:  # Main loop for handling client communication
        try:
            data = client_socket.recv(2048).decode()  # Receive data from the client
            if not data:  # If no data is received, client has disconnected
                if debug_level == 1:
                        print(Fore.YELLOW + f"Client has disconnected" + Style.RESET_ALL)
                break

            message = json.loads(data)  # Deserialize the JSON message

            last_activity_time = time.time()


            with lock:
                # Handle different message types
                if message["type"] == "join":
                    if debug_level == 1:
                        print(Fore.BLUE + "Joining a channel" + Style.RESET_ALL)
                    handle_join(client, message, channels)
                elif message["type"] == "leave":
                    if debug_level == 1:
                        print(Fore.BLUE + "Leaveing a channel" + Style.RESET_ALL)
                    handle_leave(client, message)
                elif message["type"] == "nick":
                    if debug_level == 1:
                        print(Fore.BLUE + "Changing nickname" + Style.RESET_ALL)
                    handle_nick(client, message)
                elif message["type"] == "list":
                    if debug_level == 1:
                        print(Fore.BLUE + "Listing channels" + Style.RESET_ALL)
                    handle_list(client, message)
                elif message["type"] == "msg":
                    if debug_level == 1:
                        print(Fore.BLUE + "Sending message" + Style.RESET_ALL)
                    handle_msg(client, message)
                elif message["type"] == "quit":
                    if debug_level == 1:
                        print(Fore.BLUE + "Leaving Server" + Style.RESET_ALL)
                    handle_quit(client, message)
                    break  # Exit the loop if the client quits
                elif message["type"] == "help":
                    if debug_level == 1:
                        print(Fore.BLUE + "Printing help message" + Style.RESET_ALL)
                    handle_help(client, message)
                else:  # If the message type is not recognized
                    if client.channel:  # If the client is in a channel
                        # Construct a chat message and broadcast it to the channel
                        response = {
                            "type": "chat_message",
                            "sender": client.nickname,
                            "message": message["message"],
                        }
                        broadcast(client_socket, response, client.channel)
                    else:  # If the client is not in a channel
                        # Send a server message informing the client to join a channel
                        send_server_message(
                            client,
                            Fore.RED
                            + "You are not in a channel. Use /join <channel_name> to join one."
                            + Style.RESET_ALL,
                        )

        except Exception as e:  # Handle any exceptions during client communication
            print(Fore.RED + f"Error handling client: {e}" + Style.RESET_ALL)
            if debug_level == 1:
                print(Fore.BLUE + "Error: Please try joining the server again!" + Style.RESET_ALL)
            break
    with lock:
        remove_client(client_socket, debug_level)  # Remove the client when the connection is closed


def remove_client(client_socket, debug_level):
    """Removes a client from the clients list and any channel they were in."""
    for client in clients:
        if client.socket == client_socket:
            if client.channel:
                try:
                    client.channel.clients.remove(client)
                    if debug_level == 1:
                        print(Fore.YELLOW + f"Removing client: {client.nickname}" + Style.RESET_ALL)
                except ValueError:

                    if debug_level == 1:
                        print(Fore.YELLOW + f"Could not remove client, not in channel: {client.nickname}" + Style.RESET_ALL)
            
            clients.remove(client)
            break
        
    client_socket.close()


stop_event = threading.Event()  # global event to signal threads to stop


def idle_timeout_checker():
    """Checks for idle timeout and shuts down the server if unused."""
    global last_activity_time

    while not stop_event.is_set():  # Check if stop event is set
        time_since_last_activity = time.time() - last_activity_time
        print(
            Fore.YELLOW
            + f"Checking idle timeout. Time since last activity: {time_since_last_activity}s"
            + Style.RESET_ALL
        )
        if time_since_last_activity > IDLE_TIMEOUT:
            print(
                Fore.RED
                + "Server has been idle for over 3 minutes. Shutting down..."
                + Style.RESET_ALL
            )
            shutdown_server()
            break
        time.sleep(10)  # Check every 10 seconds


def shutdown_server():
    """Shuts down the server gracefully."""
    global server_socket

    stop_event.set()

    for client in clients:
        try:
            client.socket.close()
        except Exception as e:
            print(Fore.RED + f"Error closing client socket: {e}" + Style.RESET_ALL)

    # Close the server socket
    try:
        server_socket.close()
    except Exception as e:
        print(Fore.RED + f"Error closing server socket: {e}" + Style.RESET_ALL)

    print(Fore.RED + "Server shutting down..." + Style.RESET_ALL)


def signal_handler(sig, frame):
    """Handles the Ctrl-C (KeyboardInterrupt) signal for graceful shutdown."""
    print(
        Fore.RED
        + "\nCtrl-C detected. Shutting down server gracefully..."
        + Style.RESET_ALL
    )
    shutdown_server()


running = True  # Add a flag to control the main loop

if __name__ == "__main__":

    # Register the signal handler for Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    # setting up argument parsing
    parser = argparse.ArgumentParser(
        prog="ChatServer",
        description="Basic chat server supporting multiple clients over the Internet",
    )
    parser.add_argument(
        "-p",
        type=int,
        choices=range(12000, 12050),
        default=12000,
        help="port number (between 12000 and 12049)",
    )
    parser.add_argument(
        "-d", type=int, choices=[0, 1], default=0, help="debug level (0 or 1)"
    )
    args = parser.parse_args()
    # parser.print_help()

    # storing values
    server_port = args.p  # Define the server port
    debug_level = args.d

    # Server setup
    server_socket = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
    server_socket.bind(("", server_port))  # Bind the socket to the port
    server_socket.listen(5)  # Listen for incoming connections

    server_socket.settimeout(1)

    print(Fore.GREEN + f"Server is ready to receive" + Style.RESET_ALL)

    idle_thread = threading.Thread(target=idle_timeout_checker, daemon=True)
    idle_thread.start()

    try:
        while running:  # Main loop for accepting client connections
            try:
                client_socket, addr = server_socket.accept()
                print(Fore.CYAN + f"Accepted connection from {addr}" + Style.RESET_ALL)
                client_socket.send(json.dumps(help_msg).encode())
                client_handler = threading.Thread(
                    target=handle_client, args=(client_socket,debug_level)
                )
                client_handler.start()
            except timeout:
                continue
            except OSError:  # Handle socket closure
                break
    except KeyboardInterrupt:
        running = False
        shutdown_server()
