import json
import threading

from SharedData import *  # Import shared data (clients, channels, etc.)


def send_server_message(client, message):
    """Sends a server message to the client."""
    # Construct the server message dictionary and send it to the client
    client.socket.send(
        json.dumps({"type": "server_message", "message": message}).encode()
    )


def handle_join(client, message, channels):
    """Handles the /join command."""
    channel_name = message["channel_name"]  # Get the channel name from the message
    # Check if the channel already exists

    if client.channel:
        handle_leave(client, message)

    channel = next((c for c in channels if c.name == channel_name), None)

    if not channel:  # If the channel doesn't exist, create it
        channel = Channel(channel_name)
        channels.append(channel)
        send_server_message(client, f"Channel {channel_name} has been created.\n")

    channel.clients.append(client)  # Add the client to the channel's client list
    client.channel = channel  # Set the client's current channel

    # Send messages to the client and the channel to confirm the join
    send_server_message(client, f"You have joined channel: {channel.name}")
    broadcast(
        client.socket,
        {
            "type": "server_message",
            "message": f"SERVER: {client.nickname} has joined the channel.",
        },
        channel,
    )


def handle_leave(client, message):
    """Handles the /leave command."""
    if client.channel:  # Check if the client is in a channel
        channel_name = client.channel.name  # Get the channel name

        # Send messages to the client and the channel to confirm the leave
        send_server_message(client, f"You are leaving channel: {channel_name}")
        broadcast(
            client.socket,
            {
                "type": "server_message",
                "message": f"SERVER: {client.nickname} has left the channel.",
            },
            client.channel,
        )

        client.channel.clients.remove(
            client
        )  # Remove the client from the channel's client list
        client.channel = None  # Set the client's current channel to None


def handle_nick(client, message):
    """Handles the /nick command."""
    new_nickname = message["nickname"]  # Get the new nickname from the message
    if new_nickname:  # If a new nickname is provided
        old_nickname = client.nickname  # Store the old nickname
        client.nickname = new_nickname  # Update the client's nickname
        if client.channel:  # If the client is in a channel
            # Broadcast a message to the channel to inform about the nickname change
            broadcast(
                client.socket,
                {
                    "type": "server_message",
                    "message": f"SERVER: {old_nickname} is now known as {client.nickname}.",
                },
                client.channel,
            )


def handle_list(client, message):
    """Handles the /list command."""
    if channels:  # If there are any channels
        # Construct a string with the list of channels and their user count
        channel_list = "Channels:\n" + "\n".join(
            [f"{c.name} ({len(c.clients)} users)" for c in channels]
        )
        send_server_message(client, channel_list)  # Send the channel list to the client
    else:  # If there are no channels
        send_server_message(client, "No channels available.")  # Inform the client


def handle_msg(client, message):
    """Handles the /msg command."""
    try:
        target_nickname = message[
            "target_nickname"
        ]  # Get the target nickname from the message
        private_message = message["private_message"]  # Get the private message content

        # Find the target client in the clients list
        target_client = next(
            (c for c in clients if c.nickname == target_nickname), None
        )
        if target_client:  # If the target client is found
            # Send the private message to both the target client and the sender
            target_client.socket.send(
                json.dumps(
                    {
                        "type": "private_message",
                        "sender": client.nickname,
                        "message": private_message,
                    }
                ).encode()
            )
            client.socket.send(
                json.dumps(
                    {
                        "type": "private_message",
                        "receiver": target_nickname,
                        "message": private_message,
                    }
                ).encode()
            )
        else:  # If the target client is not found
            send_server_message(
                client, f"SERVER: User {target_nickname} not found."
            )  # Inform the sender
    except IndexError:  # Handle potential errors in message formatting
        send_server_message(
            client, "Invalid /msg command format. Usage: /msg <nickname> <message>"
        )  # Inform the sender


def handle_quit(client, message):
    """Handles the /quit command."""
    send_server_message(client, "Goodbye!")  # Send a goodbye message to the client


def handle_help(client, message):
    """Handles the /help command."""
    # Send the help message (assuming help_msg is a dictionary)
    client.socket.send(json.dumps(help_msg).encode())
