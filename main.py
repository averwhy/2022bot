import os, time, re, requests
from slackclient import SlackClient
from pprint import pprint
import pyowm
import json # For converting Weather API results to something not messy.

# instantiate Slack client
token = ''
slack_client = SlackClient(token)
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "-help"
COMMAND_FIVE = "-weather" 
VERSION = "`v0.1`"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not found. Try *{}* to view a list of commands.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "*Commands:*\n`-cmds` : See the list of commands.\n`-weather` : See the hourly weather forecast."
        print("Someone used !cmds.")

    if command.startswith(COMMAND_FIVE):
        owm = pyowm.OWM()

        owm.set_API_key('')
        observation = owm.weather_at_id(4744326)
        w = observation.get_weather()
        data= w.get_temperature('fahrenheit')
        RESPOND = [
        "The current temperature (Fahrenheit) is: {0:.2f}".format(data["temp"]),
        "The high is: {0:.2f}".format(data["temp_max"]),
        "The low is: {0:.2f}".format(data["temp_min"]),
        "*Note: This can change*"]
        response = "\n".join(RESPOND)
        print("Someone got the weather.")

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

print("current version is", VERSION)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("2022bot connected and running")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
