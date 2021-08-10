#!/usr/bin/env python3
import os
import json
from simple_term_menu import TerminalMenu
#----------------------------------------
def createTimeline(year_dict):
    print("timeline")

    date = input(">> Input date in the format (1998-10-10/yyyy-mm-dd):\n")
    print("[+] Entered Date: ", date)

    title = input(">> Input title for the timeline: ")
    print("[+] Entered Title: ", title)

    timeline_file = "./timelinecopy.json"
    parent_url = "https://raw.githubusercontent.com/wannabemrrobot/daily-progress/main/cron@daily/"
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]

    file_url = f"{parent_url}{year}/{month}-{year_dict.get(month)}/{day}-{year_dict.get(month)}-{year}.md"

    # create entry for updating timeline object json
    timeline_obj = {
        "date": date,
        "title": title,
        "url": file_url
    }


    json_file = open(timeline_file)
    data = json.load(json_file)

    data.insert(0, timeline_obj)
    print(data)
    with open(timeline_file, 'w') as json_out:
        json.dump(data, json_out, indent=4)

def createPosts():
    print(">> posts triggered")
    pass

def createTheme():
    print("theme")
    pass

def main():
    year_dict = { 
        '01': 'january', 
        '02': 'february', 
        '03': 'march', 
        '04': 'april',
        '05': 'may',
        '06': 'june',
        '07': 'july',
        '08': 'august',
        '09': 'september',
        '10': 'october',
        '11': 'november',
        '12': 'december' 
        }

    print(">> Select function: ")
    options = ["1. create timeline event", "2. create posts", "3. create theme"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    # print(f"You have selected {options[menu_entry_index]}")
    if(menu_entry_index == 0):
        createTimeline(year_dict)
    elif(menu_entry_index == 1):
        createPosts()
    elif(menu_entry_index == 2):
        createTheme()



if __name__ == "__main__":
    main()