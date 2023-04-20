# Wg
Simple wireguard telegram bot administration panel that you can see users data usage total use, average and see details of wireguard statistics.
</br>(**on going repo**)

# How to use
First install requirements.txt </br>
```
pip install requirements.txt
```
Then make .env file for your own and set env variables like
`API_KEY="YOUR API KEY` and `CONF_NAME="YOUR CONFIGS NAME" ` </br>
At the end run main.py by the command
``` 
python3 main.py
```

# Bot Commands

### Reload ###
Refresh the data. (***Needed after starting the bot***)

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



