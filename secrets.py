# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.twitch.tv"                          # Hostname of the IRC-server
PORT = 6667                                     # Default IRC-port
CHAN = "#"                                      # Channelname = #{Nickname} (must include the hashtag!)
NICK = ""                                       # Nickname = Twitch username
PASS = ""                                       # www.twitchapps.com/tmi/ will help to retrieve the required authkey
MODS = []                                       # Mods have access to the chat commands ['examplemod', 'mod2']
HEADERS = {
    'Accept': 'application/vnd.twitchtv.v3+json',
    'Client-ID': 'hstc5m6avaozavrejv5gdxzvrs78u68',
    }                                           # Client-ID of this application

# --------------------------------------------- End Settings -------------------------------------------------------
