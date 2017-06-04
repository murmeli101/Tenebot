#!/usr/bin/env python3

""" --- Tenebot by Tenebrae (twitch.tv/tenebrae101) --- 

IMPORTANT: Add necessary information to secrets.py before using the program 
"""

import re, sys, socket, datetime, os, nltk, requests, json
from time import sleep
from random import randint
from urllib import request
from nltk.corpus import stopwords
from secrets import *

""" global variables """
chatpath = os.path.relpath("chatlog")
con = socket.socket()

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


def parse_message(sender, msg, comments):
    if len(msg) >= 1:
        msg = msg.split(' ', 1)
        """ list of commands """
        if msg[0] == "!test" and sender in MODS:
            command_test()
        elif msg[0] == "!commands":
            command_commands()
        elif msg[0] == "!quote":
            command_quote(comments, msg[1].strip())
        elif msg[0] == "!faq":
            command_faq()


def get_comments():
    """Parse all comments and return a list of (comment, sender, year) tuple """
    comments = []
    data = ""

    print("Loading comments...")
    for file in os.listdir(chatpath):
        if file.endswith(".txt"): # a bit redundant
            try:
                with open(chatpath + "/" + file, 'rb') as f:
                    for line in f.readlines():
                        data = line.decode()[11:]
                        data = re.split(r": ", data)
                        comments.append((re.split(r" \n", data[1])[0], data[0], file[8:12]))
            except Exception:
                print("Error while loading comments.")
    print("Loading comments... Done")
    return comments


def get_channel(name):
    """ Get the case-distinction of a username """
    url = 'https://api.twitch.tv/kraken/channels/' + name

    r = requests.get(url, headers=HEADERS)
    try:
        return r.json()['display_name']
    except KeyError:
        return name #if their Twitch account is deleted, just return the nick (no uppercases)


def write_log(sender, message):
    """Write s comment to log"""
    filename = "chatlog_" + str(datetime.date.today()) + ".txt"
    try:
        with open(chatpath + "/" + filename, "ab") as f:# 'binary' because we must be able to write non-Latin characters
            f.write("[".encode())
            f.write(str(datetime.datetime.now().time())[:8].encode())
            f.write("] ".encode())
            f.write(sender.encode())
            f.write(": ".encode())
            f.write(message.encode())
            f.write("\n".encode())
    except Exception:
        print("Error while writing a message to a file.")

def connect():
    """Connect to the chat server"""
    con.connect((HOST, PORT))
    send_pass(PASS)
    send_nick(NICK)
    join_channel(CHAN)
    

# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Chat Command Functions ---------------------------------------

def command_test():
    send_message(CHAN, 'Now I am become Speedrunner, the destroyer of games')

def command_commands():
    send_message(CHAN, 'Available commands: !quote, !faq')

def command_faq():
    send_message(CHAN, 'Sonic 1 notes: http://pastebin.com/EXknRQKg')


def command_quote(comments, nick = None):
    """ Find a comment by a random user or by a user defined by the first argument"""
    if nick:
        #search a comment by a certain person
        user_comments = []
        for comment, name, year in comments:
            if name == nick.lower():
                user_comments.append((comment,year))
        if len(user_comments) > 0:
            try:
                i = randint(0, len(user_comments)-1)
            except Exception:
                print("Exception while using randint")
                pass
            send_message(CHAN, '\"%s\" - %s, %s' % (user_comments[i][0], get_channel(nick), user_comments[i][1]))
        else:
            send_message(CHAN, 'Booooo, no such user in the database')
    else:
        #no arguments
        i = randint(0, len(comments)-1)
        send_message(CHAN, '\"%s\" - %s, %s' % (comments[i][0], get_channel(comments[i][1]), comments[i][2]))

# --------------------------------------------- End Chat Command Functions ----------------------------------------------

# --------------------------------------------- Main Loop ----------------------------------------------

def main():
    connect()
    data = ""
    comments = get_comments()

    while True:
        try:
            """ unparsed message looks like this:
                :nick!nick@nick.tmi.twitch.tv PRIVMSG #channel :message"""
            if (str(datetime.datetime.now())[11:19] == "00:07:00"):
                comments = get_comments()
                print('Comments refreshed')
                try:
                    with open(chatpath + "/" + 'log.log', "ab") as f:
                        f.write("Comments refreshed ".encode())
                        f.write((str(datetime.datetime.now()) + "\n").encode())
                except Exception:
                    print("Error while writing to a file.")
                sleep(1)
    
            data = data + con.recv(1024).decode('UTF-8')
            data_split = re.split(r"[~\r\n]+", data) #[':nick!nick@nick.tmi.twitch.tv PRIVMSG #channel :message', '']
            data = data_split.pop()
    
            for line in data_split:
                line = str.rstrip(line)
                line = str.split(line)
    
                if len(line) >= 1:
                    if line[0] == 'PING':
                        send_pong(line[1])
                        print('pong')
    
                    if line[1] == 'PRIVMSG':
                        sender = get_sender(line[0])
                        message = get_message(line)
                        parse_message(sender, message, comments)
                        try:
                            print("%s: %s" %(sender, message))
                        except UnicodeEncodeError:
                            print(sender + ": [can't output unicode characters]")
                            pass
                        if message.startswith('!') == False: # don't log chat commands
                            write_log(sender, message)
    
        except socket.error:
            print("Socket died")
            try:
                with open(chatpath + "/" + 'log.log', "ab") as f:
                    f.write("socket error ".encode())
                    f.write((str(datetime.datetime.now()) + "\n").encode())
            except Exception:
                print("Error while writing to a file.")
            connect()
            pass
    
        except socket.timeout:
            print("Socket timeout")
            try:
                with open(chatpath + "/" + 'log.log', "ab") as f:
                    f.write("socket died ".encode())
                    f.write((str(datetime.datetime.now()) + "\n").encode())
            except Exception:
                print("Error while writing to a file.")
            connect()
            pass
    
        except:
            print("Unexpected error:")
            try:
                with open(chatpath + "/" + 'log.log', "ab") as f:
                    f.write("unexpected error  ".encode())
                    f.write((str(datetime.datetime.now()) + "\n").encode())
            except Exception:
                print("Error while writing to a file.")
            exit(1)

# --------------------------------------------- Main Loop End ----------------------------------------------

main()
