#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import random
import requests
import time
import threading
import os
import json

import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll


class Bot:

    def __init__(self, vk):

        self.spamDetected = {}
        self.commandsUsed = {}
        self.badwordsDetected = {}
        self.messagesParsed = {}
        self.totalInfo = {}
        self.spamming = 0
        self.session = requests.Session()
        self.vk_session = vk
        self.vk = vk.get_api()
        self.helloWorlds = ['Console.WriteLine("Hello World!");',
                            'System.out.println("Hello World!");',
                            'writeln("Hello World!");',
                            'print("Hello World")',
                            'cout<<"Hello World!"<<endl;',
                            '<html><head></head><body>Hello World!</body></html>',
                            'echo "Hello World!";',
                            'printf("Hello World!");']
        self.patterns = [r"([\w/ !,\\?\.\(\)]*)п[еeи]д[оoaа]*р([\w/ !,\\?\.\(\)]*)", r"([\w/ !,\\?\.\(\)]*)[оoаa ][xх][*уy][йеeяuи]([\w/ !,\\?\.\(\)]*)",
        r"([\w/ !,\\?\.\(\)]*)[еёиe]б[аauи]([нhтcс])([\w/ !,\\?\.\(\)]*)",
        r"([\w/ !,\\?\.\(\)]*)[пn][иueе\*]+" + r"[сc3з]+" + r"д([\w/ !,\\?\.\(\)]*)", r"([\w/ !,\\?\.\(\)]*) бля([\w/ !,\\?\.\(\)]*)",
        r"([\w/ !,\\?\.\(\)]*) бля([\w/ !,\\?\.\(\)]*)", r"([\w/ !,\\?\.\(\)]*)бля[т]([\w/ !,\\?\.\(\)]*)",
        r"([\w/ ]*)[ ь][eе]б[aаyу] ([\w\\\ ]*)", r"([\w\\\ ]*)д[oо]лб[aа][ёeе]б([\w\\\ ]*)"]
        self.help = 'команды:\n/hw - Сказать "Привет мир"\n' \
                    '/helloWorld - Привет мир на разных ЯП\n' \
                    '/сбор - призвать всех в беседу (только для админов)\n' \
                    '/онлайн - проверить, кто онлайн в беседе\n' \
                    '/кто <фраза, имя, прозвище, и т.д.> - рандомно выбирает\n' \
                    'человека\n' \
                    '/ или /help - показать команды.\n'
        self.startTime = time.time()

    def sendMsgToChat(self, event, message, image = False, url = 'https://pbs.twimg.com/media/D4aTJ8yWAAE4GJu.jpg', video = False, videoref = 'video213946714_456239065'):
        try:
            upload = VkUpload(self.vk_session)
            attachments = []
            if image:
                upload = VkUpload(self.vk_session)
                image_url = url
                image = self.session.get(image_url, stream=True)
                photo = upload.photo_messages(photos=image.raw)[0]
                attachments.append(
                'photo{}_{}'.format(photo['owner_id'], photo['id']))
            if video:
                attachments.append('video-' + videoref)
            self.vk.messages.send(
                        attachment=videoref if video else '',
                        chat_id=event.chat_id,
                        message=message,
                        random_id=1
                    )
        except Exception as e:
            print(e)

    def parseChat(self, event, msg):
        ################### INFO-COLLECT ####################
        try:
            self.messagesParsed[event.chat_id] += 1
        except:
            self.messagesParsed[event.chat_id] = 1
        try:
            self.totalInfo['messagesParsed'] += 1
        except:
            self.totalInfo['messagesParsed'] = 1
        ################### INFO-COLLECT ####################
        if "ааааааа" in msg.lower():
            self.sendMsgToChat(event, "Не кричи на меня! Я очень ранимый естественный разум.")
            return
        badwords = False
        for p in self.patterns:
            if re.match(p, msg.lower()):
                badwords = True
        '''if random.randint(1, 10) in (1, 3, 5, 7, 9):
            badwords = False'''
        if msg.startswith('/') and badwords:
            self.sendMsgToChat(event, "Команды с матами выполнять не буду!", image = True)
            return
        if badwords:
            ################### INFO-COLLECT ####################
            try:
                self.badwordsDetected[event.chat_id] += 1
            except:
                self.badwordsDetected[event.chat_id] = 1
            try:
                self.totalInfo['badwordsDetected'] += 1
            except:
                self.totalInfo['badwordsDetected'] = 1
            ################### INFO-COLLECT ####################
            self.sendMsgToChat(event, "Ребята, общайтесь без мата, пожалуйста", image = True)
        if not msg.startswith('/'):
            return
        ################### INFO-COLLECT ####################
        try:
            self.commandsUsed[event.chat_id] += 1
        except:
            self.commandsUsed[event.chat_id] = 1
        try:
            self.totalInfo['commandsUsed'] += 1
        except:
            self.totalInfo['commandsUsed'] = 1
        ################### INFO-COLLECT ####################
        args = msg.split()
        if not hasattr(self, 'lastCommandTime'):
            self.lastCommandTime = time.time() - 10
        currentTime = time.time()
        #print(str(currentTime - self.lastCommandTime))
        if currentTime - self.lastCommandTime < 4:
            self.spamming += 1
            if self.spamming > 4:
                ################### INFO-COLLECT ####################
                try:
                    self.spamDetected[event.chat_id] += 1
                except:
                    self.spamDetected[event.chat_id] = 1
                try:
                    self.totalInfo['spamDetected'] += 1
                except:
                    self.totalInfo['spamDetected'] = 1
                ################### INFO-COLLECT ####################
                self.sendMsgToChat(event, 'Хватит спамить командами!!!', video = True)
                self.lastCommandTime = time.time()
                return
        else:
            self.spamming = 0
        self.lastCommandTime = time.time()
        if args[0] == '/hw':
            self.sendMsgToChat(event, 'Привет мир!')
            #self.sendMsgToChat(event, '', video = True)
        elif args[0] == '/helloWorld':
            i = random.randint(0, len(self.helloWorlds) - 1)
            self.sendMsgToChat(event, self.helloWorlds[i])
        elif args[0] == '/сбор':
            cmembers = self.vk.messages.getConversationMembers(peer_id = 2000000000 + event.chat_id)
            items = cmembers['items']
            useSbor = self.isAdmin(items, event)
            if not useSbor:
                return
            m = ''
            if len(args) > 1:
                for i in range(1, len(args)):
                    m += args[i] + ' '
            else:
                m = 'Общий сбор!\n'

            members = self.vk.messages.getConversationMembers(peer_id = 2000000000 + event.chat_id)['profiles']
            for member in members:
                #print(member)
                if not 'screen_name' in member.keys():
                    continue
                m += '[' + member['screen_name'] + '|' + member['first_name'] + '], '
            self.sendMsgToChat(event, m)
        elif args[0] == '/кто':
            if len(args) == 1:
                args.append('Это ')
            members = self.vk.messages.getConversationMembers(peer_id = 2000000000 + event.chat_id)['profiles']
            i = random.randint(0, len(members) - 1)
            member = members[i]
            who = ''
            for word in args[1:]:
                who += word + ' '
            self.sendMsgToChat(event, who + 'естественно ' + \
                               member['first_name'] + ' ' + member['last_name'] + '!')
        elif args[0] == '/онлайн':
            online = []
            members = self.vk.messages.getConversationMembers(peer_id = 2000000000 + event.chat_id)['profiles']
            for member in members:
                if member['online']:
                    online.append(member['first_name'] + ' ' + member['last_name'])
            txt = 'Сейчас онлайн:' if len(online) > 1 else 'Никого нет онлайн, кроме вас.'
            for user in online:
                if len(online) < 2:
                    break
                txt += user + ', '
            txt += 'и бот.' if len(online) > 1 else ''
            self.sendMsgToChat(event, txt)
        elif msg in ('/help', '/'):
            self.sendMsgToChat(event, self.help)
        elif args[0] in ("/ъеь", "/ъуъ", "/ьеъ", "/ьуъ"):
            self.sendMsgToChat(event, "Логикаааа зашкаливает...")
        elif args[0] == "/exec":
            if event.object['from_id'] != 423904265:
                self.sendMsgToChat(event, "Доступ запрещен.")
                return
            if len(args) == 1:
                self.sendMsgToChat(event, "Неправильное использование. Используйте так: /bash [python/bash] [command]")
                return
            if args[1] == "python":
                err = False
                try:
                    res = eval(" ".join(args[2:]))
                except Exception  as e:
                    res = e
                    err = True
                if err:
                    self.sendMsgToChat(event, "Произошла ошибка: " + str(res))
                else:
                    self.sendMsgToChat(event, "Результат: " + str(res))
            elif args[1] == "bash":
                try:
                    self.sendMsgToChat(event, os.popen(" ".join(args[2:])))
                except:
                    self.sendMsgToChat(event, "Ошибка.")
            else:
                self.sendMsgToChat(event, "Неожиданный тип исполнения: " + args[1] + ".")
        elif args[0] == "/easterEgg":
            self.sendMsgToChat(event, "Автор сейчас ждет Соник Йожыг: кооператив злодеев, часть 2\n:3")
        elif args[0] == "/отчет":
            lastResetTime = (time.time() - self.startTime)/60
            if lastResetTime > 60:
                minutes = int(lastResetTime % 60)
                lastResetTime //= 60
                lastResetTime = int(lastResetTime)
                timeFromLastReset = str(lastResetTime)
                timeFromLastReset += " ч"
                timeFromLastReset += f", {minutes}" if minutes != 0 else ""
                timeFromLastReset += " мин."
            else:
                minutes = round(lastResetTime)
                timeFromLastReset = str(minutes)
                timeFromLastReset += " мин."

            #print(lastResetTime)
            if len(args) > 1:
                if args[1] == 'total':
                    msg = "Отчет с последнего сброса (все беседы):\n"
                    msg += "Время с последнего сброса: " + timeFromLastReset + "\n"
                    msg += "Всего матов обнаружено: " + str(self.totalInfo.get("badwordsDetected", 0)) + ".\n"
                    msg += "Всего реакций на спам: " + str(self.totalInfo.get("spamDetected", 0)) + ".\n"
                    msg += "Всего команд (или сообщений со знаком '/' в начале) пропарсено: " + str(self.totalInfo.get("commandsUsed", 0)) + ".\n"
                    msg += "Всего сообщений обработано: " + str(self.totalInfo.get("messagesParsed", 0)) + ".\n"
                else:
                    msg = "Неправильное использование команды. Использование: /отчет, или /отчет total"
            else:
                msg = "Отчет с последнего сброса (эта беседа):\n"
                msg += "Время с последнего сброса: " + timeFromLastReset + "\n"
                msg += "Всего матов обнаружено: " + str(self.badwordsDetected.get(event.chat_id, 0)) + ".\n"
                msg += "Всего реакций на спам: " + str(self.spamDetected.get(event.chat_id, 0)) + ".\n"
                msg += "Всего команд (или сообщений со знаком '/' в начале) пропарсено: " + str(self.commandsUsed.get(event.chat_id, 0)) + ".\n"
                msg += "Всего сообщений обработано: " + str(self.messagesParsed.get(event.chat_id, 0)) + ".\n"
            self.sendMsgToChat(event, msg)

    def isAdmin(self, items, event):
        admin = False
        for item in items:
            if item['member_id'] == event.object['from_id']:
                admin = item.get('is_admin')
        return admin

def main():
    try:
        file = open("data.json")
        data = json.load(file)
        token = data['token']
        group_id = data['groupId']
    except FileNotFoundError:
        print("Data file not found, make it by starting setup.py")
        input("Press <enter> to exit. ")
        return
    fileForErrors = open('errorLog.txt', 'w')
    while True:
        try:
            vk_session = vk_api.VkApi(token)

            longpoll = VkBotLongPoll(vk_session, group_id)

            bot = Bot(vk_session)

            for event in longpoll.listen():
                if event.from_chat:
                    t = threading.Thread(target=bot.parseChat, args=(event, event.obj.text))
                    t.start()
        except Exception as e:
            print(e)
            fileForErrors.write(str(type(e)) + ':' + str(e) + '\n')
            print("Happened error. Restarting...")
if __name__ == "__main__":
    main()