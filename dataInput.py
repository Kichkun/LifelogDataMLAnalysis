# Python: Version 2.7.10
# Project: Import CSV of coach.me and scripts to format the data into a bunch of different useful sets for data analysis.
# - 9/1 add organization sets
# - 9/8 add "by habit" sets for the date and dotw
# - 9/15 final polishing, organizing what is left
# By: Bryan Dickens, Summer 2015
 
__author__ = "bryan"
__date__ = "$Sep 1, 2015 8:34:52 AM$"

import numpy as np

# organize by all items of the data, for use on just full feature detection. 
#ex: {ID:'1' : [habit,date,note,checkin count, streak, props, comments, url], etc.}
def organizeByItem(data):
    item_dictionary = dict()
    features = data[0]
    firstrow = True   
    #loop to add each item into the dictionary
    for row in data:
        if firstrow:
            firstrow = False
        else:
            item_dictionary[row[0]] = []
            firstcol = True
            for i in range(len(row)):
                if firstcol:
                    firstcol = False
                else:
                    value = features[i] + ':' + row[i]
                    item_dictionary[row[0]].append(value)
  
    return item_dictionary

# organize by all streaks of the days and a day before to find out streak relations
# could not really find a use. but streak 2->streak 1 has confidence of 71% and streak1->streak 2 has confidence of 45%
# ex: {ID:'1' : [streak of today, streak of yesterday], etc.}
def organizeByStreak(data):
    streak_dictionary = dict()

    habit_streaks = dict()
    for row in data:
        streak_dictionary[row[0]] = [row[5]]
        #if habit already exists append that old streak count and then update with new count
        if row[1] in habit_streaks:
            streak_dictionary[row[0]].append(habit_streaks[row[1]])
            habit_streaks[row[1]] = row[5]
        else:
            #habit does not exist and create it
            habit_streaks[row[1]] = row[5]
        
    return streak_dictionary

#organize the data by each date 
#ex: {'date1': [all habits on that day],'date2': [all habits in day 2],etc}
def organizeByDate(data):
    date_dictionary = dict()
    
    for row in data:
        if row[2] in date_dictionary:
            #add the habit to the array
            date_dictionary[row[2]].append(row[1])
        else:
            date_dictionary[row[2]] = [row[1]]
            
    return date_dictionary

#organize the data by each date including day of the week(DOTW) 
#ex: {'date1': [all habits on that day, monday],'date2': [all habits in day 2, thursday],etc}
#0-6, 0 = sunday -> 6 = saturday
def organizeByDateWithDOTW(data):
    date_dictionary = dict()
    import datetime # for day of the week calculations
    
    firstrow = True
    for row in data:
        if row[2] in date_dictionary:
            #add the habit to the array
            date_dictionary[row[2]].append(row[1])
        else:
            date_dictionary[row[2]] = [row[1]]
        if firstrow:
            firstrow = False
        else:
            dateVal = datetime.datetime.strptime(row[2],'%Y-%m-%d').date().weekday()
            if dateVal not in date_dictionary[row[2]]:
                date_dictionary[row[2]].append(dateVal)
            
    return date_dictionary

#start with the data input organized by date
#return a dictionary of each of the habits and then their data sets from the time that habit was first created
#{key:'habit',value:{dataset from that start date}}
def createItemDictionary(data):
    item_dictionary = dict()
    data = data.tolist()
    #go through the data, if item has not been seen yet, create a new key and start that dataset with that date
    firstrow = True
    current_date = ''
    current_date_origin_index = 0
    for row in data:
        if firstrow:
            firstrow = False
            #update the first item in the current date
            current_date = row[2]
            #get the row to start on
            current_date_origin_index = data.index(row)
        else:
            if current_date != row[2]:
                #update the new index and date
                current_date = row[2]
                current_date_origin_index = data.index(row)
            if row[1] not in item_dictionary:
                #create data dictionary of all stuff after that date                
                item_dictionary[row[1]] = data[current_date_origin_index:]
                
                #print 'Started Goal: ' + row[1] + ' on ' + current_date
            
    return item_dictionary

# loading data into python
#just in general the goal here now is to get analytics for each habit
def loadData():
    #file to import
    coach_me_in_file = "lifedata/coach.me.export.20150828020632.csv"
    coach_me_data = np.genfromtxt(coach_me_in_file,delimiter=',', dtype=None)

#    print 'Data shape:'
#    print coach_me_data.shape       #5922, 1 features row
#    print 'Feature Set:'
#    print coach_me_data[0]          #see the feature variables
#    print 'Full Data Input:'
#    print coach_me_data             #all data input received correctly

    #turns data into {Habit: [dataset from that habit start date], etc.}
    coach_me_data_per_item = createItemDictionary(coach_me_data)
    
    coach_me_organized_date = {}
    coach_me_organized_dotw = {}
    for key in coach_me_data_per_item:
        #organize into all the tables that I want to run associative analysis on
        #turns data into {Habit: {date: [habits that day], etc.}, etc.}
        coach_me_organized_date[key] = organizeByDate(coach_me_data_per_item[key])
        coach_me_organized_dotw[key] = organizeByDateWithDOTW(coach_me_data_per_item[key])

    #organize other ways, via all general items and via streak usage
    coach_me_organized_items = organizeByItem(coach_me_data)
    coach_me_organized_streak = organizeByStreak(coach_me_data)

    #return the dictionaries of tables to run the analysis
    return (coach_me_organized_date, coach_me_organized_items, coach_me_organized_streak, coach_me_organized_dotw)


#potential TODO for dataInput.py
#TODO:if key is not in the date add it for the date/dotw? ex: !pray -> workout
#TODO:plot all of these habits, color coded via the habit. try to get each habit as the series in the data, and then calendar on the x axis, occured or not on the y axis, maybe just the count of them as a column
#TODO:histograms of each variable?
#TODO:% likelihood of a habit GIVEN did it previous day, previous 3 days, etc.
#TODO:Azure Web service offer it on the Gallery
#TODO:add different data sources! Sleep, Finance, Phone Usage, etc.