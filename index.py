from bs4 import BeautifulSoup
import requests
import json
from elasticsearch import Elasticsearch
from colorama import Fore

def all_info(userName): 
        
        try:
            myName  = userName.lstrip('@')  ##We Dont need @ when finding Followers and Followings Count....
            response = requests.get('https://www.tiktok.com/'+userName+'')
            soup = BeautifulSoup(response.content, "html.parser")
            
            es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
            index_name = 'videos'
            
            script = soup.find("script", id="SIGI_STATE")
            
            max_tries = 3
            
            while max_tries > 0:
                if script:
                    # Extract the content of script.string and parse it as JSON
                    script_content = script.string
                    json_data = json.loads(script_content)
                    videos = json_data["ItemList"]["user-post"]["list"]
                        
                    ##Stor
                    profile = {
                    "Tiktok Account Title: ": json_data["SharingMetaState"]["value"]["og:title"],
                    'Total Followers of : '+userName+'':json_data["UserModule"]["stats"][''+myName+'']["followerCount"],
                    ''+userName+' Following: ':json_data["UserModule"]["stats"][''+myName+'']["followingCount"],
                    'Total likes of '+userName+'': json_data["UserModule"]["stats"][''+myName+'']["heart"]
                    }
                        
                    es.index(index=index_name,doc_type='doc',body=profile)
                        
                    ###Dump Profile Information One TIme
                    print("        ")
                    print(Fore.LIGHTGREEN_EX+"Profile Information............................................")
                    print("Tiktok Account Title: "+json_data["SharingMetaState"]["value"]["og:title"])
                    print('Total Followers of ' + userName + ': ' + str(json_data["UserModule"]["stats"][''+myName+'']["followerCount"]))
                    print(''+userName+' Following:'+str(json_data["UserModule"]["stats"][''+myName+'']["followingCount"]))
                    print('Total likes of '+userName+':'+str(json_data["UserModule"]["stats"][''+myName+'']["heart"]))
                        
                    print("   ")
                    print("Videos Information..............................................")
                    for video in videos:
                        videoInfo = json_data["ItemModule"][video]
                        videoDoc = {
                            "description: ": videoInfo["desc"],
                            "createdTime: ": videoInfo["createTime"],
                            "url of Video: ": 'https://www.tiktok.com/'+userName+'/video/'+video,
                            "likes: ":  str(videoInfo["stats"]["diggCount"]),
                            "shares: ": str(videoInfo["stats"]["shareCount"]),
                            "COMMENT COUNT: ":   str(videoInfo["stats"]["commentCount"]),
                            "SAVE COUNT: ":  str(videoInfo["stats"]["collectCount"])
                            }
                            
                            ###Video All Information...
                        print(Fore.LIGHTBLUE_EX+"Video Description:"+videoInfo["desc"])
                        print(Fore.LIGHTGREEN_EX+"Video Created On:"+videoInfo["createTime"])
                        print(Fore.LIGHTRED_EX + "URL of Video : " 'https://www.tiktok.com/'+userName+'/video/'+video)
                        print(Fore.CYAN+"Total Likes On Video:"+str(videoInfo["stats"]["diggCount"]))
                        print(Fore.LIGHTMAGENTA_EX+"Total Shares of the Video:"+str(videoInfo["stats"]["shareCount"]))
                        print(Fore.LIGHTYELLOW_EX+"Total Collect_Count:"+str(videoInfo["stats"]["collectCount"]))
                            
                        print("   ")
                        print("   ")
                            
                        ##Dump into ES...
                        response = es.index(index=index_name, doc_type='doc', body=videoDoc)
                        
                    # Define the file path where you want to save the JSON data
                    my_file = 'tiktok.json'
                    with open(my_file, 'w', encoding='utf-8') as json_file:
                       json.dump(json_data, json_file, ensure_ascii=False, indent=4)      
                    print(f"JSON data written to '{my_file}'")
                    print("Data Dumped into ElasticsSearch as well.......")
                    break
                
                else:
                   max_tries = max_tries - 1 
                   print("Requesting again with retries remaining: "+max_tries)
                
                
        except Exception as e:
           print(e)
          
all_info('@thenikosknifee')