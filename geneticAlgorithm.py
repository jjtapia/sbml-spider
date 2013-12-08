# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 14:17:57 2013

@author: proto
"""

from subprocess import call        
import cPickle as pickle
import shutil
import os
import random
from copy import copy
import sys
import numpy as np
def callScrapy(counter,keyTerms,numberOfPages):
    url = 'http://www.plosone.org/search/simple?from=globalSimpleSearch&filterJournals=PLoSONE'
    print url,keyTerms,numberOfPages
    url = '{0}&query={1}&x=-1243&y=-99&pageSize={2}'.format(url,'+'.join(keyTerms),numberOfPages)
    call(['mkdir','xml/output{0}'.format(counter)])
    call(['scrapy','crawl','sbml','-s','LOG_FILE=scrapy_{0}.log'.format(counter),'-a','start_urls={0}'.format(url)])
    print ' '.join(['scrapy','crawl','sbml','-s','LOG_FILE=scrapy_{0}.log'.format(counter),'-a','start_urls={0}'.format(url)])
    source = os.listdir(".")
    source = [x for x in source if '.xml' in x or '.dump' in x]
    print '0-----'
    keyWords = set([])
    if 'counterArray.dump' in source:
        with open('counterArray.dump','rb') as f:
            keyWords = pickle.load(f)
    for sourceFile in source:
        shutil.copy(sourceFile,'xml/xmlDump')
        shutil.move(sourceFile,'xml/output{0}'.format(counter))    
    return keyWords

def loadKeyWordDatabase():
    counter = set()
    with open('counterArray.stats','rb') as f:
        table = pickle.load(f)
        
        for element in table:
            for singleElement in element:
                counter.add(singleElement)
    return counter

def getRandomSample(keywords,number):
    randomSample = set()
    tmp = list(keywords)
    from random import randint
    while len(randomSample) < number:
        randomSample.add(tmp[randint(0,len(tmp)-1)])
    return randomSample

def createInitialPopulation(keywords,size):
    population = []
    for idx in range(0,size):
        c = Chromosome()
        c.content = getRandomSample(keywords,random.randint(1,3))
        c.counter = (idx+1)
        population.append(c)
    return population
    
class Chromosome():
    def __init__(self):
        self.content = []
        self.counter = 0
class GeneticAlgorithm():
    def __init__(self,initialPopulation,keywords):
        self.keywords = keywords
        self.initialPopulation = initialPopulation
        self.populationSize = len(self.initialPopulation)
        self.crossOverProbability = 0.5
        self.mutationProbability = 0.1
        self.counter = 100
        self.maxIterations= 50
        self.numberOfPages = 10
        
    def getCounter(self):
        self.counter +=1
        return self.counter
    def crossOver(self,chromosome1,chromosome2):
        newChromosome = copy(chromosome1)
        newChromosome.counter = self.getCounter()
        self.counter+=1
        fragments = []
        low = random.randint(0,len(chromosome2.content))
        tmpContent = list(chromosome2.content)
        while low < len(tmpContent):
            high = min(random.randint(low+ 1,len(tmpContent)),len(tmpContent))
            
            fragments.extend(tmpContent[low:high])
            low = high+1
        
        newChromosome.content = list(newChromosome.content)
        newChromosome.content.extend(tmpContent)
        newChromosome.content = set(newChromosome.content)
            
        return newChromosome
        
        
    def mutation(self,chromosome1):
        index = random.randint(0,len(chromosome1.content)-1)
        chromosome1.content = list(chromosome1.content)
        chromosome1.content[index] = list(getRandomSample(self.keywords,1))[0]
        chromosome1.content = set(chromosome1.content)


        chromosome1.counter = self.getCounter()
        return chromosome1
        
    def memoize(f):
        '''
        store already evaluated chromosomes in a cache
        '''
        cache = {}
        def helper(self,x):
            if x not in cache:            
                cache[x] = f(self,x)
            return cache[x]
        return helper

    @memoize
    def fitnessFunction(self,chromosome1):
        keyWords = callScrapy(chromosome1.counter,chromosome1.content,self.numberOfPages)
        for group in keyWords:
            for key in group:
                if key not in self.keywords:
                    self.keywords.add(key)
                    print key,
        print
        with open('xml/output{0}/stats.dump'.format(chromosome1.counter)) as f:
            totalCounter = pickle.load(f)
            
        source = os.listdir(".")
        counter = len([x for x in source if '.xml' in x])

        return counter*1.0/totalCounter*1.0
        
    def run(self):
        '''
        ending conditions: 10 iterations with the same best individual
        '''
        pol= self.initialPopulation
        score = 0
        counter=0
        idx=0
        averageHistory = []
        maxHistory = []
        while counter < 10 and idx < self.maxIterations:
            pol,evaluation = self.update(pol)
            self.numberOfPages = int(self.numberOfPages*1.2)
            averageHistory.append(np.average(evaluation))
            maxHistory.append(np.average(np.max(evaluation)))
            if score != max(evaluation):
                self.mutationProbability = 0.2
                score = max(evaluation)
                print score
                counter = 0
            else:
                self.mutationProbability *= 1.14
                print '.',
                sys.stdout.flush()
                counter +=1
            idx+=1
        return pol[evaluation.index(max(evaluation))],max(evaluation),averageHistory,maxHistory
        

    def update(self,population):
        def getRandom(cdf):
            return max(i for r in [random.random()] for i,c in cdf if c <= r)
        fitnessVector = []
        for chromosome in population:
            fitnessVector.append(self.fitnessFunction(chromosome))
        if sum(fitnessVector) == 0:
            pdf = [(idx,0) for idx,x in enumerate(fitnessVector)]
        else:
            pdf = [(idx,max(0,x/sum(fitnessVector))) for idx,x in enumerate(fitnessVector)]
        cdf = cdf = [(i, sum(p for j,p in pdf if j < i)) for i,_ in pdf]
        newPopulation = []
        tmp = []
        for iter in range(0,self.populationSize):
            tmp.append(population[getRandom(cdf)])
        #elitism
        newPopulation.append(population[fitnessVector.index(max(fitnessVector))]) 
        for iteri in range(0,len(tmp)):
            if random.random() < self.crossOverProbability:
                r = random.randint(0,len(newPopulation)-1)
                if r != iteri:
                    newPopulation.append(self.crossOver(copy(tmp[iteri]),copy(tmp[r])))
            elif random.random() < self.mutationProbability:
                newPopulation.append(self.mutation(copy(tmp[iteri])))
            else:
                newPopulation.append(tmp[iteri])
            
        return newPopulation,fitnessVector


if __name__ == "__main__":
    keywords = loadKeyWordDatabase()
    #randomSample =  getRandomSample(keywords,3)
    initialPol = createInitialPopulation(keywords,20)
    ga = GeneticAlgorithm(initialPol,keywords)
    results =  ga.run()
    with open('results.dump','wb') as f:
        for result in results:
            pickle.dump(result,f,2)
        pickle.dump(ga.keywords,f)
    #callScrapy(0,['sbml','xml'])    
    #callScrapy(2,randomSample)    