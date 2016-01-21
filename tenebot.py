#!/usr/bin/env python3

""" --- Tenebot by Tenebrae (twitch.tv/tenebrae101) --- 
""" Add necessary information to secrets.py before using the program """

TODO
- automatic repeats
- wordnet synset (noun)
- make a nice chart of comment count per user
"""

import re, sys, socket, goslate, wikipedia, datetime, os, nltk, requests, json
from random import randint
from urllib import request
from nltk.corpus import stopwords
from secrets import *



# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))

# --------------------------------------------- End Functions ------------------------------------------------------


# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result[1:] #remove an unnecessary colon
    return result


def parse_message(msg):
    if len(msg) >= 1:
        msg = msg.split(' ', 1)
        """ list of commands """
        if msg[0] == "!test" and sender in MODS:
            command_test()
        elif msg[0] == "!translate" and sender in MODS:
            command_translate(msg[1])
        elif msg[0] == "!commands":
            command_commands()
        elif msg[0] == "!quote" and sender in MODS:
            command_quote(msg[1].strip())
        elif msg[0] == "!quote" and sender not in MODS: # just trolling
#            command_quote(sender.strip())
             command_quote()
        elif msg[0] == "!wiki" and sender in MODS:
            command_wiki(msg[1])
        elif msg[0] == "!words" and sender in MODS:
            command_words()
        elif msg[0] == "!users" and sender in MODS:
            command_users()
        elif msg[0] == "!mike":
            send_message(CHAN, 'https://www.youtube.com/watch?v=w0DxF2OR2QA')
#        elif msg[0] == "!wr":
#            command_wr()


def get_comments():
    """Parse all comments and return a list of (comment, sender, year) tuple """
    comments = []

    for file in os.listdir(chatpath):
        if file.endswith(".txt"): # a bit redundant
            with open(chatpath + "/" + file, 'rb') as f:
                for line in f.readlines():
                    data = line.decode()[11:]
                    data = re.split(r": ", data)
                    comments.append((re.split(r" \n", data[1])[0], data[0], file[8:12]))
    return comments


def get_channel(name):
    """ Get the case-distinction of a username """
    url = 'https://api.twitch.tv/kraken/channels/' + name

    r = requests.get(url, headers=HEADERS)
    try:
        return r.json()['display_name']
    except KeyError:
        print("KeyError: Check what went wrong ")
        command_quote() #if something goes wrong, try again


def make_chatcorpus():
    """ Return a list of all words in every log file"""
    # you could also use nltk.word_tokenize or nltk.regexp_tokenize(text, pattern)
    # edit the code to filter out non-alphabetic characters
    messages = []

    for file in os.listdir(chatpath):
        if file.endswith(".txt"):
            with open(chatpath + "/" + file, 'rb') as f:
                for line in f.readlines():
                    #data = re.split(r"\] ", line.decode())
                    data = line.decode()[11:]
                    data = re.split(r": ", data)
                    del data[0]
                    
                    data = re.split(r" \n", data[0])
                    message = data[0].split() # message
                    messages += message
    return messages


def comments_per_nick():
    """ Return the frequency distribution of commenters """
    comments = get_comments()
    names = [name for _, name in comments]
    fdist = nltk.FreqDist(names)
    return fdist


def most_common_words():
    '''Print most used words '''
    #unused 
    words = make_chatcorpus()
    fdist = nltk.FreqDist(w.lower() for w in words)
    return fdist


def write_log(sender, message):
    """Write s comment to log"""
    with open(chatpath + "/" + filename, "ab") as f:# 'binary' because we must be able to write non-Latin characters
        f.write("[".encode())
        f.write(str(datetime.datetime.now().time())[:8].encode()) # current time(str(datetime.datetime.now().time())[:8])
        f.write("] ".encode())
        f.write(sender.encode())
        f.write(": ".encode())
        f.write(message.encode())
        f.write("\n".encode())

"""
def visualize_users():
    '''Make a graph of users ordered by sent messages'''
    #unused, needs to be a bar graph
    users = comments_per_nick()
    users.plot()


def visualize_words():
    '''Make a graph of words by their frequency (TODO logarithmic scale'''
    #unused
    words = most_common_words()
    words.plot()
"""

# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Chat Command Functions ---------------------------------------

def command_test():
    send_message(CHAN, 'Now I am become Speedrunner, the destroyer of games')


def command_translate(message):
    translated = gs.translate(message, 'ko')
    # Chinese pinyin would be >>> gs_roman = Goslate(WRITING_ROMAN) / print(gs_roman.translate('Hello', 'zh'))
    translated_back = gs.translate(translated, 'en')
    send_message(CHAN, "Korean: " + translated + " English: " + translated_back)


def command_commands():
    send_message(CHAN, 'Available commands: !quote, !wr')


def command_wiki(word):
    '''Post the wikipedia definition for a word'''
    definition = ""
    try:
        definition = wikipedia.summary(word, sentences=2)
        if len(definition) > 220:
            definition = wikipedia.summary(word, sentences=1)
            if len(definition) > 200:
                send_message(CHAN, definition[:197] + "...")
            else:
                send_message(CHAN, definition)
        elif len(definition) < 30:
            definition = wikipedia.summary(word, sentences=3)
            if len(definition) > 200:
                send_message(CHAN, definition[:197] + "...")
            else:
                send_message(CHAN, definition)
        else:
            send_message(CHAN, definition)

    except wikipedia.exceptions.DisambiguationError as e:
        send_message(CHAN, "Disambiguation: 1. " + e.options[0] + " 2. " + e.options[1] + " ...")

    except wikipedia.exceptions.PageError as e:
        send_message(CHAN, "Page error. Please try another word.")


def command_quote(nick = None):
    """ Find a comment by a random user or by a user defined by the first argument"""
    if nick:
        #search a comment by a certain person
        user_comments = []
        for comment, name, year in comments:
            if name == nick.lower():
                user_comments.append(comment)
        if len(user_comments) > 0:
            i = randint(0, len(user_comments)-1)
            send_message(CHAN, '\"%s\" - %s, 2015' % (user_comments[i], get_channel(nick.lower())))
        else:
            send_message(CHAN, 'Booooo, no such user in the database')
    else:
        #no arguments
        i = randint(0, len(comments)-1)
        send_message(CHAN, '\"%s\" - %s, %s' % (comments[i][0], get_channel(comments[i][1]), comments[i][2]))


def command_words():
    words = most_common_words()
    contentwords = [(word, count) for word, count in words.most_common(50) if word not in stopwords.words('english')]
    cleantext = ""
    for item in contentwords:
        i = "('" + str(item[0]) + "', " + str(item[1]) + "), "
        cleantext += str(i)
    send_message(CHAN, 'Most common words excluding stopwords: %s' % cleantext[:len(cleantext)-2])


def command_users():
    """Post a list of  most active users """
    users = comments_per_nick()
    print(users.most_common(10))


def command_wr():
    """Get the world record from speedrun.com"""
    #Get the title of current game on Twitch
    url = 'https://api.twitch.tv/kraken/channels/' + CHAN[1:]

    r = requests.get(url, headers=HEADERS)
    game = r.json()['game']

    #Find game title on speedrun.com 
    url = "http://www.speedrun.com/api/v1/games?name=" + game
    r = requests.get(url)
    game = str(r.json()['data'][0]['names']['international'])

    #and find wr
    url = "http://www.speedrun.com/api_records.php?game=" + game
    r = request.urlopen(url)

    data = json.loads(r.read().decode())
    print(data)
    print(url)
    print(json.dumps(data[list(data.keys())[0]], sort_keys=True, indent=4)) #pretty print for testing

    gamename = list(data.keys())[0]
    print(gamename)
    category = list(data[gamename].keys())[0]

    timeseconds = int(data[gamename][category]['time'])
    time = str(datetime.timedelta(seconds=timeseconds))
    
    player = data[gamename][category]['player']

    send_message(CHAN, 'WR in category %s is %s by %s' % (category, time, player))

   
# --------------------------------------------- End Command Functions ----------------------------------------------

""" connect to the chat server"""
con = socket.socket()
con.connect((HOST, PORT))

send_pass(PASS)
send_nick(NICK)
join_channel(CHAN)

""" global variables """
data = ""
gs = goslate.Goslate()
chatpath = os.path.relpath("chatlog")
filename = "chatlog_" + str(datetime.date.today()) + ".txt"
comments = get_comments() # load comments to memory for quick access. used in command_quote


while True:
    try:
        """ unparsed message looks like this:
            :nick!nick@nick.tmi.twitch.tv PRIVMSG #channel :message"""
        data = data + con.recv(1024).decode('UTF-8')
        data_split = re.split(r"[~\r\n]+", data) #[':nick!nick@nick.tmi.twitch.tv PRIVMSG #channel :message', '']
        data = data_split.pop()

        for line in data_split:
            line = str.rstrip(line)
            line = str.split(line)

            if len(line) >= 1:
                if line[0] == 'PING':
                    send_pong(line[1])

                if line[1] == 'PRIVMSG':
                    sender = get_sender(line[0])
                    message = get_message(line)
                    parse_message(message)
                    try:
                        print("%s: %s" %(sender, message))
                    except UnicodeEncodeError:
                        print(sender + ": [can't output unicode characters]")
                        pass
                    if message.startswith('!') == False: # don't log chat commands
                        write_log(sender, message)

    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")
