#!/usr/bin/env python3
#
# Client for the UINames.com service.
#
# 1. Decode the JSON data returned by the UINames.com API.
# 2. Print the fields in the specified format.
#
# Example output:
# My name is Tyler Hudson and the PIN on my card is 4840.

import requests
import json

def SampleRecord():
    r = requests.get("http://uinames.com/api?ext&region=United%20States",
                     timeout=2.0)
    # 1. Add a line of code here to decode JSON from the response.
    r_json = json.loads(r.content)
    #print(type(r_json))
    #print(r_json) 
    return "My name is {0} {1} and the PIN on my card is {2}.".format(
        r_json["name"],
        r_json["surname"],
        r_json["credit_card"]["pin"]
         # 2. Add the correct fields from the JSON data structure.
    )

if __name__ == '__main__':
    print(SampleRecord())
