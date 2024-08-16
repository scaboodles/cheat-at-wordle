import random
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time

# 0 -> letter absent
# 1 -> wrong place
# 2 -> correct

def sortWordlistByLetterFreq(words):
    alphabet = ''.join(words)
    freqs = Counter(alphabet)

    def score(word):
        unique = set(word)
        return sum(freqs[letter] for letter in unique)
    sortedWords = sorted(words, key=score, reverse=True)

    return sortedWords

def clickElemByTestID(driver, id):
    driver.find_element(By.CSS_SELECTOR, '[data-testid="{}"]'.format(id)).click()

def clickLetter(driver, letter):
    driver.find_element(By.CSS_SELECTOR, '[data-key="{}"]'.format(letter)).click()

def inputGuess(driver, guess):
    guess = guess.lower()
    for letter in guess:
        clickLetter(driver, letter)
        time.sleep(.1)
    driver.find_element(By.CSS_SELECTOR, "[aria-label='enter']").click()
    time.sleep(2)

def getTileFeedback(tile):
    full = tile.get_attribute('aria-label')
    if("absent" in full):
        return 0
    elif("present" in full):
        return 1
    else:
        return 2

def getTiles(driver, guessNumber, guess): #guess number starts counting at 0
    tiles = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tile"]')
    guessIndex = guessNumber * 5
    tiles = tiles[guessIndex:guessIndex+5]
    tileData = []
    for i in range(len(tiles)):
        tileData.append({'letter': guess[i], 'data' : getTileFeedback(tiles[i]), 'position' : i})

    return tileData
            
def pruneWords(words, data):
    newWords = []
    for curr in words:
        keepWord = True
        confirmed = {letter: 0 for letter in set(curr)}

        for letterData in data:
            currLetter = letterData['letter']
            currData = letterData['data']
            currPos = letterData['position']

            if(currData == 2):
                if(not curr[currPos] == currLetter):
                    keepWord = False
                else:
                    confirmed[currLetter] += 1

        for letterData in data:
            currLetter = letterData['letter']
            currData = letterData['data']
            currPos = letterData['position']

            if(currData == 1):
                if(curr[currPos] == currLetter or currLetter not in curr):
                    keepWord = False
                else:
                    confirmed[currLetter] += 1
            elif(currData == 0):
                if(currLetter in curr and confirmed[currLetter] < curr.count(currLetter)):
                    keepWord = False

        if keepWord:
            newWords.append(curr)
    return newWords
            
def init ():
    with open('fiveLetterWords.txt', 'r') as file:
        read = file.read()
    possibleWords = sortWordlistByLetterFreq(read.splitlines())

    driver = webdriver.Chrome()
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    time.sleep(2)

    print('init driver')

    clickElemByTestID(driver, "Play")
    time.sleep(.25)

    clickElemByTestID(driver, "icon-close")
    time.sleep(.25)
    guessNumber = 0
    while(True):
        currGuess = random.choice(possibleWords[:max(1, len(possibleWords) // 4)]).lower()
        print("|{}|".format(currGuess))
        inputGuess(driver, currGuess)

        data = getTiles(driver, guessNumber, currGuess)

        guessNumber += 1
        print("guess {} got feedback {}".format(currGuess,data))
        possibleWords = pruneWords(possibleWords, data)

        time.sleep(1)

init()