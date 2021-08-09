#!/usr/bin/env python3
from simple_term_menu import TerminalMenu
#----------------------------------------
def createTimeline():
    print("timeline")
    pass

def createPosts():
    print("posts")
    pass

def createTheme():
    print("theme")
    pass

def main():
    print(">> Select function: ")
    options = ["1. create timeline event", "2. create posts", "3. create theme"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    # print(f"You have selected {options[menu_entry_index]}")
    if(menu_entry_index == 0):
        createTimeline()
    elif(menu_entry_index == 1):
        createPosts()
    elif(menu_entry_index == 2):
        createTheme()



if __name__ == "__main__":
    main()