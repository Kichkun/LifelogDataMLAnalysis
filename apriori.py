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
    
    
    #trim the keys of the dictionary because associative analysis is solely relational in the group
    coach_me_organized_date = [coach_me_organized_date[key] for key in coach_me_organized_date.keys()]
    coach_me_organized_items = [coach_me_organized_items[key] for key in coach_me_organized_items.keys()]
    coach_me_organized_streak = [coach_me_organized_streak[key] for key in coach_me_organized_streak.keys()]
    coach_me_organized_dotw = [coach_me_organized_dotw[key] for key in coach_me_organized_dotw.keys()]
        
    if(removedCommons):
        #remove common data sometimes works best
        coach_me_organized_date = [[x for x in y if x not in ['Pray','NoP!','Laugh','Set priorities for your day']] for y in coach_me_organized_date]
        coach_me_organized_items = [[x for x in y if x not in ['Pray','NoP!','Laugh','Set priorities for your day']] for y in coach_me_organized_items]
        coach_me_organized_streak = [[x for x in y if x not in ['Pray','NoP!','Laugh','Set priorities for your day']] for y in coach_me_organized_streak]
        coach_me_organized_dotw = [[x for x in y if x not in ['Pray','NoP!','Laugh','Set priorities for your day']] for y in coach_me_organized_dotw]

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
        confidence = supportData[itemSet] / supportData[itemSet-item]
        if confidence >= minConfidence:
            ruleList.append((itemSet-item, item, confidence))
            prunedSet.append(item)
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
    
    

#apriori algorithm for 5922 days/~50 items
#run time estimate = instant for minSupport = 0.6 
#rt = instant for minSupport 0.3
#rt = 2s for minSupport 0.1
#rt = 5s for minSupport 0.08 lowest I can go, overly crowded data though
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
            individualSet = [frozenset([item]) for item in itemSet]
            if (i > 1):
                recursiveRuleCalculation(itemSet, individualSet, supportData, ruleList, minConfidence)
            else:
                calculateConfidence(itemSet, individualSet, supportData, ruleList, minConfidence)
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
                print '\n'.join(['%i: %s support: %s' % (n, list(sorted_support[n][0]), sorted_support[n][1])])
        print "Rules: "
        for n in xrange(len(sorted_rules)):
            if any(x in (list(sorted_rules[n][0])) for x in [0,1,2,3,4,5,6]):
                print '\n'.join(['%i: %s -> %s confidence: %s' % (n, list(sorted_rules[n][0]), list(sorted_rules[n][1]), sorted_rules[n][2])])
    #else just print the data
    else:
        print "Support Data: "
        print '\n'.join(['%i: %s support: %s' % (n, list(sorted_support[n][0]), sorted_support[n][1]) for n in xrange(len(sorted_support))])

        print "Rules: "
        print '\n'.join(['%i: %s -> %s confidence: %s' % (n, list(sorted_rules[n][0]), list(sorted_rules[n][1]), sorted_rules[n][2]) for n in xrange(len(sorted_rules))])
    

# the main function
if __name__ == '__main__':
    removeCommonItems = True   #set only when you want to trim the common stuff
    coach_me_organized_date, coach_me_organized_items, coach_me_organized_streak, coach_me_organized_dotw = doDataInput(removeCommonItems)
    
    print 'Data Analysis:'
    
    isDOTW = True           #set only when running dotw
    minSupport = 0.1        #tweak variable for allowing uncommon itemsets
    minConfidence = 0.08    #tweak variable for allowing less common rules
    
    #run the algorithm
    itemList, supportData = aprioriAlgorithm(coach_me_organized_dotw, minSupport)
    rules = generateRules(itemList, supportData, minConfidence)
    outputData(supportData, rules, isDOTW)
    print 'Finished'

    


