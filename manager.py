#!/usr/bin/env python3
import os
import json
#----------------------------------------

def createTimeline(year_dict):

    # get the date and title from the user to populate the json file
    date = input(">> Input date in the format (1998-10-10/yyyy-mm-dd):\n   date: ")
    print("-----------------------")
    title = input(">> Input title for the timeline:\n   title: ")
    print("-----------------------")


    print("[+] Entered Date: ", date)
    print("[+] Entered Title: ", title)
    print("-----------------------")

    # json file to populate data
    timeline_file = "./timeline.json"
    # current working directory for the task
    working_dir = "./cron@daily"
    # github url to fetch the timeline markdown file
    github_url = "https://raw.githubusercontent.com/wannabemrrobot/daily-progress/main/cron@daily/"

    
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]

    # the file that needs to be created
    file_name = f"{day}-{year_dict.get(month)}-{year}.md"
    # the complete file url for public access
    file_url = f"{github_url}{year}/{month}-{year_dict.get(month)}/{day}-{year_dict.get(month)}-{year}.md"

    # json object with data from the user
    timeline_obj = {
        "date": date,
        "title": title,
        "url": file_url
    }

    # open json file to get the file contents(json list)
    json_file = open(timeline_file)
    data = json.load(json_file)

    # insert new json object into existing list of json objects
    data.insert(0, timeline_obj)
    file_exist = False

    if(os.path.isdir(f"{working_dir}/{year}") == False):
        print(f"[!] {working_dir}/{year} : no such directory, creating directory and timeline markdown...")
        os.mkdir(f"{working_dir}/{year}")
        os.mkdir(f"{working_dir}/{year}/{month}-{year_dict.get(month)}")
        file = open(f"{working_dir}/{year}/{month}-{year_dict.get(month)}/{file_name}", "x")
        file.close()
    else:
        if(os.path.isdir(f"{working_dir}/{year}/{month}-{year_dict.get(month)}") == False):
            print(f"[!] {working_dir}/{year}/{month}-{year_dict.get(month)} : no such directory, creating directory and timeline markdown...")
            os.mkdir(f"{working_dir}/{year}/{month}-{year_dict.get(month)}")
            file = open(f"{working_dir}/{year}/{month}-{year_dict.get(month)}/{file_name}", "x")
            file.close()
        else:
            if(os.path.isfile(f"{working_dir}/{year}/{month}-{year_dict.get(month)}/{file_name}") == False):
                print(f"[!] {working_dir}/{year}/{month}-{year_dict.get(month)}/{file_name} : no such file, creating timeline markdown...")
                file = open(f"{working_dir}/{year}/{month}-{year_dict.get(month)}/{file_name}", "x")
                file.close()
            else:
                print(f"[!] {working_dir}/{year}/{month}-{year_dict.get(month)}/{file_name} : file already exists.")
                file_exist = True
    
    if(file_exist == False):
        with open(timeline_file, 'w') as json_out:
            json.dump(data, json_out, indent=4)
            print("-----------------------")
            print("[!] Timeline entry addition successful")
            print("-----------------------")
            json_out.close()


def createPost():
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

    print("\n>> Select function: \n   1. Create Timeline\n   2. Create post\n   3. Create Theme\n")
    choice = input("\nSelection: ")
    print("-----------------------")

    if(int(choice) == 1):
        createTimeline(year_dict)
    elif(int(choice) == 2):
        createPost(year_dict)
    elif(int(choice) == 3):
        createTheme()
    else:
        main()




if __name__ == "__main__":
    main()