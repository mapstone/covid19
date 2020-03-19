import csv
import requests
import pickle

'''
File: Find Weather Trend 
------------------------
This fle when run wil print out humidity and growth 
rates of covid 19 deaths to predict how summer humidity 
will effect spread of coronavirus.
'''

# Web address where we to weather data
WEATHER_URL = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx'
# first covid19 data point is from Jan 22nd (which is 21 days after Jan 1's weather data)
CODVID_DATA_START_DAY = 21 

# this is what main is...
def main():
  print('hello world')
  
  #weateher dict maps country name to the weather data in that country for each day
  weather_dict = load_weather_dict()

  # confirmed dict is the confirmed cases of coronavirus in each country
  confirmed_dict = make_confirmed_dict()

  #for loop over each country in weater dictionary 
  for country_name in weather_dict:
    # if country_name != 'United States': continue

    #and look up and get the matching name in the  different dataset
    nickname = get_nick_name(country_name)

    #if its not in the confirmed dictionary list then ignore the country and continue
    if not nickname in confirmed_dict: continue

    #defining a variable called weather data that will get all the weather data for current country
    weather_data = weather_dict[country_name]
    #create a variable of confirmed deaths for the current country 
    confirmed_data = confirmed_dict[nickname]

    # for each day (counted using a day index) in confirmed data (except last)
    for day_index in range(len(confirmed_data) - 1):
      
      #current day is the confirmed deaths on day index
      curr_day = confirmed_data[day_index]
      #next day is the confirmed deaths on the day after the index
      next_day = confirmed_data[day_index + 1]
      #difference is the next day minus the current day (absolute growth in one day)
      diff = next_day - curr_day

      #if the difference in absolute growth is greater than 5 and current day is not zero (add this last part so you never have to divide by zero)
      if diff >= 5 and curr_day != 0:
        # get growth rate for day
        growth_rate = next_day / curr_day
        
        # Looking up the weather starting on the day covid19 deaths started, minus one week (as these were the conditions leading to death)
        weather_index = (CODVID_DATA_START_DAY + day_index) - 7
        # watch out for lookup up a date before jan 1st
        if weather_index < 0: continue

        #get weather data for current country, look up the day, and the humidity and save it as humidity 
        humidity = weather_data[weather_index]['humidity']

        #print the country name, daynumber, humidty, and the growth rate  
        print(country_name+ "," + str(weather_index) + ','+humidity+ "," + str(growth_rate))
    


def get_nick_name(country_name):
  if country_name == 'South Korea':
    country_name = 'Korea, South'

  if country_name == 'United States':
    country_name = 'US'

  if country_name == 'Czech Republic':
    country_name = 'Czechia'

  return country_name
  

def make_confirmed_dict():
  reader = csv.reader(open('Deaths.csv'))
  header = next(reader)

  n_days = len(header) - 4

  # maps from country names, to a list of total confirmed cases (one elem per day) 
  confirmed_map = {}

  for row in reader:
    country_name = row[1]

    # if its the first time you have seen this country
    # start off the list as zeros
    if not country_name in confirmed_map:
      confirmed_map[country_name] = [0] * n_days

    # for each day in the row, increase the country day count
    for i in range(n_days):
      area_day_confirmed = int(row[i+4])
      country_list = confirmed_map[country_name]
      country_list[i] += area_day_confirmed

  return confirmed_map

def load_weather_dict():
  return pickle.load(open('weather_map.pkl', 'rb'))

def make_weather_map():
  country_names = get_country_names()
  weather_map = {}
  for country_name in country_names:
    print(country_name)
    if country_name in weather_map: continue
    weather = get_weather_for_location(country_name)
    weather_map[country_name] = weather
    print(weather)
    pickle.dump(weather_map, open('weather_map.pkl', 'wb'))

def get_country_names():
  reader = csv.reader(open('Confirmed.csv'))
  header = next(reader)

  country_names = {}

  for row in reader:
    country_name = row[1]

    if '*' in country_name: 
      country_name = country_name.replace('*', '')

    if 'Congo' in country_name:
      continue

    if country_name == 'Korea, South':
      country_name = 'South Korea'

    if country_name == 'occupied Palestinian territory':
      continue

    if country_name == 'Cruise Ship':
      continue

    if country_name == 'US':
      country_name = 'United States'

    if country_name == 'Czechia':
      country_name = 'Czech Republic'

    if country_name == 'Eswatini':
      continue

    country_names[country_name] = True

  return country_names

def get_weather_for_location(location):
  weather = []
  weather += get_weather_helper(location, '2020-01-01')
  weather += get_weather_helper(location, '2020-02-05')
  weather += get_weather_helper(location, '2020-03-11')
  return weather

def get_weather_helper(location, start_date):
  params = {
    'key':'e4f5b53d6c544cfbb0c31930201803',
    'q':location,
    'tp':'24',
    'format':'json',
    'date':start_date,
    'enddate':'2020-03-16'
  }
  r = requests.get(url = WEATHER_URL, params = params) 
  data = r.json()

  weather_raw = data['data']['weather'] 

  weather_nice = []
  for weather_entry in weather_raw:
    date = weather_entry['date']
    aveTemp = weather_entry['avgtempC']
    humidity = weather_entry['hourly'][0]['humidity']
    new_entry = {
      'date':date,
      'aveTemp':aveTemp,
      'humidity':humidity
    }
    print(date)
    weather_nice.append(new_entry)
  return weather_nice

def get_country_totals():
  reader = csv.reader(open('Confirmed.csv'))
  header = next(reader)
  # this var stores a map between country names and total count.
  # countries start empty, when we see them for the first time,
  # we insert them. If we see them again, we increment...
  country_totals = {}

  for row in reader:
    area_name = row[0]
    if "," in area_name: continue

    country_name = row[1]
    total_confirmed_in_area = int(row[len(row) - 1])

    if not country_name in country_totals:
      country_totals[country_name] = 0

    country_totals[country_name] += total_confirmed_in_area

  for country_name in country_totals:
    country_total = country_totals[country_name]
    print(country_name, country_total)

  
def get_growth_rate_oz():
  print('getting growth rate oz...')
  reader = csv.reader(open('Confirmed.csv'))
  header = next(reader)

  n_days = len(header) - 4

  n_confirmed_each_day_oz = [0] * n_days

  for row in reader:
    country_name = row[1]
    if country_name == 'Australia':
      for i in range(n_days):
        area_day_confirmed = int(row[i+4])
        n_confirmed_each_day_oz[i] += area_day_confirmed

  ratio_sum = 0
  n_counted = 0
  for i in range(n_days - 1):
    next_day = n_confirmed_each_day_oz[i+1]
    curr_day = n_confirmed_each_day_oz[i]
    # if n_confirmed_each_day_oz > 0:
    if curr_day != 0:
      ratio =  next_day / curr_day 
      ratio_sum += ratio
      n_counted += 1
  print(n_counted, ratio_sum / n_counted)



def get_total_confirmed():
  print('loading data...')

  # this makes a csv.reader called reader
  reader = csv.reader(open('Confirmed.csv'))
  total_cases = 0
  total_oz = 0
  # special syntax to have a csv.reader skip a row..
  header = next(reader)

  # you can loop over a csv.reader one row (list) at a time
  for row in reader:
    country_name = row[1]
    area_name = row[0]
    total_confirmed_in_area = int(row[len(row) - 1])
    total_cases += total_confirmed_in_area
    if country_name == 'Australia':
      total_oz += total_confirmed_in_area

  print('total oz: ' + str(total_oz))
  print('total cases: ' + str(total_cases))

# when you run this file, call main!
if __name__ == '__main__':
  main()