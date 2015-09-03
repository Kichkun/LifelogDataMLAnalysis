# LifelogDataMLAnalysis
Machine learning algorithm for mining Coach.Me data for associative analysis, frequent sets, and association rules

This project is for my blog on https://bryandickens.com and https://medium.com/@brDick

I wanted to analyze my college data tracking through the app Coach.Me where I inputted the goals/habits that I accomplished each day. This data can be broken down using Machine Learning, and my first attempt was to apply the Apriori algorithm to find common sets of habits that occured and also useful association rules.

The code can easily be transferable if you want to analyze your own Coach.Me data! Just swap out my .csv for yours.

The changable variables rely on the 4 different ways I organized the data.

organizeByItem          -> ex: {ID:'1' : [habit,date,note,checkin count, streak, props, comments, url], etc.}

organizeByStreak        -> ex: {ID:'1' : [streak of today, streak of yesterday], etc.}

organizeByDate          -> ex: {'date1': [all habits on that day],'date2': [all habits in day 2],etc}

organizeByDateWithDOTW  -> ex: {'date1': [all habits on that day, monday],'date2': [all habits in day 2, thursday],etc}

There is interesting questions that can be answered from each of these organizations of the data.
-The support and confidence both have a minimum value that can be changed to find less frequent occurances, or more sparse rules.
-remove common items variable just trims the common habits that I did often and were clouding the results from interesting data conclusions
-isDOTW just shows a simplified support/rules output that focuses on how the day of the week effects the habits that I performed.

There is a ton of future expansion on this project! The two other data sets are from my phone usage (Moment), and my sleep (Azumio). I plan to use them both and tie it into my data mining for further analysis.

Thanks for reading this! If you want to use this please cite me and shoot me an email or tweet first is all I ask. bryanrusselldickens@gmail.com or @brdick
