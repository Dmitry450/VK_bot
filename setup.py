#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

def main():
    data = {}
    data['token'] = input("Token >>> ")
    data['groupId'] = input("Group ID >>> ")
    print("Saving...")
    json.dump(data, open("data.json"))
    print("Succes!")
    input("Press <enter> to exit.")

if __name__ == '__main__':
    main()