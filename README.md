# EatOutTracker

## Overview
A web app that allows users to input places they have visited and the amount they spent at each place. The data is then displayed in a calendar to get an overview of the user's eating out habits for the month. Also featured is a charts section that shows daily expenditures, list of restaurants with times visited and amount spent at each restaurant. The app uses Yelp's Fusion API to get extra data such as address, phone, ratings, etc.

## Heroku Link
https://eat-out-tracker.herokuapp.com

## Technologies Used
| Technology | Use |
| ------------ | ----------|
| Python | 3.10.6 Programming Language |
| Flask | Web Framework for Python |
| SQLAlchemy | Object Relational Mapper (ORM) for SQL |
| psycopg2 | PostgreSQL adapter for Python |
| Jinja2 | Template engine |
| WTForms | Form validation and rendering |
| bcrypt | Hashing passwords |
| Flask-Login | Login library |
| BeautifulSoup | HTML parsing |
| chart.js | Charting library for javascript |

## How to run
1. Download code
2. Have Python at least 3.10.6 installed
3. Have PostgreSQL running with a db named capstone1
4. Add environment variable YELP_API_KEY by signing up for Yelp and getting an API key
5. Run `pip3 install -r requirements.txt` to install dependencies
6. Run `flask run` to run the application
