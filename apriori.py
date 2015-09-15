# Python: Version 2.7.10
# Project: Data analysis of Coach.me data
# By: Bryan Dickens, Summer 2015
 
__author__ = "bryan"
__date__ = "$Sep 1, 2015 8:34:52 AM$"

import operator

#grabs data input from dataInput.py
def doDataInput(removedCommons):
    import dataInput
    coach_me_organized_date, coach_me_organized_items, coach_me_organized_streak, coach_me_organized_dotw = dataInput.loadData()
    
    #input is {Habit: {date: [habits that day], etc.}, etc.}
    #for each habit
        #trim the keys of the dates in the dictionary to just have it be relational
    for k,v in coach_me_organized_date.iteritems():
        coach_me_organized_date[k] = [v[key] for key in coach_me_organized_date[k].keys()]
    for k,v in coach_me_organized_dotw.iteritems():
        coach_me_organized_dotw[k] = [v[key] for key in coach_me_organized_dotw[k].keys()]
        
    #trim the keys of the dictionary because associative analysis is solely relational in the group
    coach_me_organized_items = [coach_me_organized_items[key] for key in coach_me_organized_items.keys()]
    coach_me_organized_streak = [coach_me_organized_streak[key] for key in coach_me_organized_streak.keys()]
        
    if(removedCommons):
        #remove common data sometimes works best
        coach_me_organized_items = [[x for x in y if x not in ['Note:','Comment Count:0','Prop Count:0']] for y in coach_me_organized_items]
        coach_me_organized_streak = [[x for x in y if x not in ['Pray','NoP!','Laugh','Set priorities for your day']] for y in coach_me_organized_streak]

    return coach_me_organized_date, coach_me_organized_items, coach_me_organized_streak, coach_me_organized_dotw

#create the full frozen itemset from going through each day
def createItemset(data):
    itemset = []
    for date in data:
        for item in date:
            if not [item] in itemset:
                itemset.append([item])
    itemset.sort()
    return map(frozenset, itemset)

#narrow the full data to just the sets that meet the minimum support level. input is sets of each day's habits, all potential habits, and min support
def scanData(data, items, minSupport):
    itemCountDictionary = {}
    for date in data:
        for item in items:
            #if item is in the current day, +1 to that occurance of that habit happening
            if item.issubset(date):
                if not itemCountDictionary.has_key(item):
                    itemCountDictionary[item] = 1
                else:
                    itemCountDictionary[item] += 1
    
    totalItemCount = float(len(data))
    saveItemList = []
    supportData = {}
    #for each habit that showed up
    for item in itemCountDictionary:
        #calculate support as the % of days the habit occured
        support = itemCountDictionary[item]/totalItemCount
        #if support is above min support, save this item
        if support >= minSupport:
            saveItemList.insert(0,item)
        #save the support of that habit
        supportData[item] = support
    
    #return the saved habit/habit combo list and the support data of those habits/habit combos
    return saveItemList, supportData
    
#take frequent itemsets and create the next combination of itemsets. ex: (0),(1),(2) => (01),(02),(12)
def aprioriGenerator(itemsets, size):
    saveList = []
    itemsetCount = len(itemsets)
    for i in range(itemsetCount):
        for j in range(i+1, itemsetCount):
            item1 = list(itemsets[i])[:size-2]; item2 = list(itemsets[j])[:size-2]
            item1.sort(); item2.sort()
            if item1 == item2:
                #combine the sets in a union
                saveList.append(itemsets[i] | itemsets[j])
    return saveList

#confidence calculation of a rule
def calculateConfidence(itemSet, individualSet, supportData, ruleList, minConfidence):
    prunedSet = []
    for item in individualSet:
        #BUGFIX: try/except, not sure why this breaks on some odd combos... would be fixed by limiting to just 4 item lattices
        try:
            confidence = supportData[itemSet] / supportData[itemSet-item] # this breaks sometimes...

            if confidence >= minConfidence:
                ruleList.append((itemSet-item, item, confidence))
                prunedSet.append(item)
        except KeyError:
            pass #ignore error the support in question is a made up combination that does not exist in the dataset
    return prunedSet

#generate rules from recursion
def recursiveRuleCalculation(itemSet, individualSet, supportData, ruleList, minConfidence):
    size = len(individualSet[0])
    if (len(itemSet) > (size + 1)):
        newSet = aprioriGenerator(individualSet, size+1)
        newSet = calculateConfidence(itemSet, newSet, supportData, ruleList, minConfidence)
        if (len(newSet) > 1):
            #recursively call if new set needs to be broken up
            recursiveRuleCalculation(itemSet, newSet, supportData, ruleList, minConfidence)
    
    

#apriori algorithm
def aprioriAlgorithm(data, minSupport = 0.10):
    initial_itemset = createItemset(data)
    itemsetList = map(set, data)
    #returns the 1-permutations of all the items above min support
    initial_itemlist, supportData = scanData(itemsetList, initial_itemset, minSupport)
    itemList = [initial_itemlist]
    size = 2
    #loop to get the support data for all item permutations
    while (len(itemList[size-2]) > 0):
        #generate the next itemset permutation
        itemset = aprioriGenerator(itemList[size-2],size)
        #calculate the acceptable items with this combination
        item, support = scanData(itemsetList, itemset, minSupport)
        
        #update the item and the support values
        supportData.update(support)
        itemList.append(item)
        size += 1
    
    #return the list of dates that are frequent, as well as their correlated support values
    return itemList, supportData

    
#association rules generating from the apriori algorithm taking a list of items, the support value, and the confidence threshhold
#returns rules with a confidence value
def generateRules(itemList, supportData, minConfidence = 0.10):
    ruleList = []
    for i in range(1, len(itemList)):
        for itemSet in itemList[i]:
            #creates single item sets
            individualSet1 = [frozenset([item]) for item in itemSet]
            if (i > 1):
                recursiveRuleCalculation(itemSet, individualSet1, supportData, ruleList, minConfidence)
            else:
                calculateConfidence(itemSet, individualSet1, supportData, ruleList, minConfidence)
    return ruleList
    
#output the support data and the associative rules formed in decreasing order
def outputData(supportData, rules, isDOTW):
    
    #sort the support and rules to be presented
    sorted_support = sorted(supportData.items(), key = operator.itemgetter(1), reverse=True)
    sorted_rules = sorted(rules, key = operator.itemgetter(2), reverse=True)

    #dotw analysis shows just the important days involved
    if(isDOTW):
        print "Support Data: "
        for n in xrange(len(sorted_support)):
            if any(x in (list(sorted_support[n][0])) for x in [0,1,2,3,4,5,6]):
                print '\n'.join(['%i: %s: support: %s' % (n, list(sorted_support[n][0]), sorted_support[n][1])])
        print "Rules: "
        for n in xrange(len(sorted_rules)):
            if any(x in (list(sorted_rules[n][0])) for x in [0,1,2,3,4,5,6]):
                print '\n'.join(['%i: %s -> %s: confidence: %s' % (n, list(sorted_rules[n][0]), list(sorted_rules[n][1]), sorted_rules[n][2])])
    #else just print the data
    else:
        print "Support Data: "
        print '\n'.join(['%i: %s: support: %s' % (n, list(sorted_support[n][0]), sorted_support[n][1]) for n in xrange(len(sorted_support))])

        print "Rules: "
        print '\n'.join(['%i: %s -> %s: confidence: %s' % (n, list(sorted_rules[n][0]), list(sorted_rules[n][1]), sorted_rules[n][2]) for n in xrange(len(sorted_rules))])
    
#trim data is just remove all that aren't in relation with the habit at hand
def trimData(keyValue, supportData, rules):
    newSupportData = {}
    
    for val in supportData:
        if keyValue in val:
            newSupportData[val] = supportData[val]
    
    newRules = []
    for val in rules:
        if keyValue in val[0] or keyValue in val[1]:
            newRules.append(val)
    
    #print newRules
    return newSupportData, newRules
            

# the main function
if __name__ == '__main__':
    removeCommonItems = False   #set only when you want to trim the common stuff, prob not needed anymore
    coach_me_organized_date, coach_me_organized_items, coach_me_organized_streak, coach_me_organized_dotw = doDataInput(removeCommonItems)
    
    print 'Data Analysis:'
    
    isDOTW = False          #set only when running dotw
    minSupport = 0.3        #good for date- 0.3 #overly info for dotw - 0.1   #tweak variable for allowing uncommon itemsets
    minConfidence = 0.7     #good for date- 0.7, 0.8            #0.2#0.05     #tweak variable for allowing less common rules
    
#    old version of just running one per
#    itemList, supportData = aprioriAlgorithm(coach_me_organized_items, minSupport)
#    rules = generateRules(itemList, supportData, minConfidence)
#    outputData(supportData, rules, isDOTW)
    
    #run the algorithm for each key item
    for key in coach_me_organized_date:
        itemList, supportData = aprioriAlgorithm(coach_me_organized_date[key], minSupport)
        rules = generateRules(itemList, supportData, minConfidence)
        print 'Habit: ' + key
        supportData_out, rules_out = trimData(key, supportData, rules)#only for date
        outputData(supportData_out, rules_out, isDOTW)
    
    print 'Finished'

    

#potential TODO for apriori.py
#TODO:limit the correlations to just two - four habits.
#TODO:remove noisy habits effectively by finding significant value/difference between one habit vs the rest
#TODO:rewrite main method to JUST take in a specific habit and to return all data for that habit. text input or select options in a menu
#TODO:restructure so it just runs for one habit, and that it goes deep for that one habit (as deep as it needs to go to find info)
#TODO:have just key = 'Run' or 'Go to gym' with a really low support and confidence
#TODO:learn about using input/output give and take-ness. Ask them what type of data (and show the different types), ask them for the input file, ask them for which habit. also ask them what confidence and support!
#TODO:allow for easy rerunning and recalculating in your given drill in. ask for an imported csv? then let them pick stuff?
#TODO:Try bidirectional apriori, FP trees, other association analysis methods
    
