# Python: Version 2.7.10
# Project: Import CSV of coach.me and scripts to format the data into a bunch of different useful sets for data analysis.
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

# loading data into python
def loadData():
    #file to import
    coach_me_in_file = "lifedata/coach.me.export.20150828020632.csv"
    coach_me_data = np.genfromtxt(coach_me_in_file,delimiter=',', dtype=None)

    print 'Data shape:'
    print coach_me_data.shape       #5922, 1 features row
    print 'Feature Set:'
    print coach_me_data[0]          #see the feature variables
    print 'Full Data Input:'
    print coach_me_data             #all data input received correctly
    
    #organize into all the tables that I want to run associative analysis on
    coach_me_organized_date = organizeByDate(coach_me_data)
    coach_me_organized_items = organizeByItem(coach_me_data)
    coach_me_organized_streak = organizeByStreak(coach_me_data)
    coach_me_organized_dotw = organizeByDateWithDOTW(coach_me_data)

    #return the tables to run the analysis
    return (coach_me_organized_date, coach_me_organized_items, coach_me_organized_streak, coach_me_organized_dotw)


    