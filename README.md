# TG Bot Forwarder

## Description:
### This bot can forward messages to other users, chats, or groups based on hashtags.

## Manual:
To forward messages, you need to create a chat with the recipient or destination chat/group.
Add the bot as a user to the chat or group and execute the /reg command.
For the bot to send messages to a user, the user must find the bot and send the /reg command in a private message.

To set up forwarding, execute the /fwd command in the chat or group from which messages should be forwarded,
using the format: /fwd #hashtag *[list of usernames and/or chat/group names separated by commas]*.
After this, any message starting with #hashtag as the first line will be forwarded to all users, groups, or chats specified in the /fwd command.
