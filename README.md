# Wg
(**on going repo**)</br>
Simple wireguard telegram bot administration panel that you can see users data usage total use, average and see details of wireguard statistics.
</br></br>**NEW**</br>
Google sheet feature added that you can save your user usage into your google sheet. </br>
just import your google api keys to files.

# Tips
To use this bot you need to set name for peers in your server config file. </br>
like (setting sample1 to name of this peer): </br>
\### sample1 ### </br>
[peer] </br>
... </br>
and space between each state must be just one. </br></br>
![image](https://github.com/ceenaa/wg/assets/88087819/87bdb15b-f8b9-4779-b912-2de0a5327ddd)


# How to use
First install requirements.txt </br>
```
pip install -r requirements.txt
```
Then make .env file for your own and set env variables like
```
API_KEY="YOUR API KEY"
CONF_NAME="YOUR CONFIGS NAME"
SHEET_ID="Your google sheet ID"
SYSTEM_NAME="wg0.conf"
MAX_TRANSFER=60
```
Then you need to import your keys.json (keys for google sheet api) in the folder. </br>
At the end run main.py by the command
``` 
python3 main.py
```

# Bot Commands

### Reload ###
Refresh the data. (***Needed after starting the bot***) </br>
And save ussers usage to google sheet.

### All 
Returns all user info that has been sorted by their data transfer

### Total
Returns total usage

### Count
Returns count of active users

### Average
Returns total/count

### Total days
Returns total days that your data has been recorded since then. </br>
***(Note that you have to set starting date in code by your own, you can find it in analytics.py)***

### Daily average 
Returns Total/Total days

### Max
Returns user with maximum data transfer

### Pause x
Pause user x

### Reusme x
Resume user x

### x
send user x derails

### Paused users
list of paused users



