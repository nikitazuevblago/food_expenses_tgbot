# food_expenses_tgbot


## Intro
The bot was created because I'm tired of using excel and wanted some easy bot which tracks my expenses in telegram.

## Deployment 
Digital Ocean Droplet - postgreSQL, + repo as docker image.
Check it out in telegram - @TrackFoodExpensesBot

## Installation and Setup 
```bash
git clone git@github.com:nikitazuevblago/food_expenses_tgbot.git
cd food_expenses_tgbot
pip install -r requirements.txt
python main.py
```
* Don't forget to create .env file with necessary variables

## Technologies Used
* aiogram
* psycopg2

## File structure
main.py - bot structure
db_interaction.py - interaction with database


