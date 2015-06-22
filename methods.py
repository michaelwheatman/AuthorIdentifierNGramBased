import re
from collections import defaultdict
import string
import nltk
import cProfile
import random
def buildDictionary(filename):
	f = open(filename, 'r')
	dictionary = []
	for line in f:
		l = line.strip()
		l = l.split(' ', 1)
		l[1] = l[1].strip()
		dictionary.append(l)
	return dictionary

def getPronounciation(word, dictionary):
	for reference in dictionary:
		if reference[0].lower() == word:
			return reference[1]
	return ''

def doesRhyme(wordOne, wordTwo, dictionary):
	pronounciationOne = getPronounciation(wordOne, dictionary)
	pronounciationTwo = getPronounciation(wordTwo, dictionary)
	if getLastSyllable(pronounciationOne) == getLastSyllable(pronounciationTwo):
		return True
	return False

def getLastSyllable(pronounciation):
	for i in range(len(pronounciation)-1,-1, -1):
		if isVowel(pronounciation[i]):
			if i != 0 and isVowel(pronounciation[i-1]) == False:
				return pronounciation[i-1:]
			return pronounciation[i:]
	return ''

def isVowel(phoneme):
	vowels = ['AA','AE','AH','AO','AW','AY','EH','ER','EY','IH','IY','OW','OY','UH','UW','Y']
	if phoneme in vowels:
		return True
	return False

def getNumSyllables(pronounciation):
	numSyllables = 0
	for phone in pronounciation:
		if isVowel(phone):
			numSyllables+=1
	return numSyllables


def loop(word1, dictionary):
	rhymes = []
	for item in dictionary:
		if doesRhyme(word1, item[0].lower(), dictionary):
			rhymes.append(item[0])
			print item[0]
	return rhymes

def clean(filename):
	f = open(filename, 'r')
	d = open("n.txt", 'w')
	for line in f:
		line = line.lower()
		#line = re.sub(r'([^\s?[a-z]]|_)+', '', line)
		line = re.sub(r'[-_.?!,":\';()|0-9]*', r'', line)

		#print line
		if line != "\n":
			d.write(line)
	d.close()
	f.close()

def buildBiGramCounts(filename):
	unigrams = {}
	source = open(filename, 'r')
	source = source.read()
	for i in range(len(source)):
		if source[i] not in unigrams:
			unigrams.append([source[i], 0])
		else:
			unigrams[unigrams.index(source[i])][1]+=1
		if i%5000 == 0:
			print i, len(source)
	print unigrams 

# returns a dictionary with a default value of another instance of this kind of
# dictionary and the initial value of the dictionary at key 0 is 0.
def get_count_dict():
    d = defaultdict(get_count_dict)
    d[0] = 0
    return d


# Creates a dictionary that will contain a dictionary for each unigram,
# which then contains a dictionary holding the second element of a bigram,
# each bi-gram consists of a dictionary that contains the third element of the
# trigram started by the word "t".
def get_counts(token_list):
    counts = get_count_dict()
    for i, t in enumerate(token_list):
        counts[0] += 1
        counts[t][0] += 1
        if i + 1 < len(token_list):
            counts[t][token_list[i+1]][0] += 1
        if i + 2 < len(token_list):
            counts[t][token_list[i+1]][token_list[i+2]][0] += 1
    return counts


def main():
	#dictionary = buildDictionary('cmudict.txt')
	#word1 = 'establishment'
	#print getPronounciation(word2, dictionary)
	#print doesRhyme(word1, word2, dictionary)
	#pronounciation = getPronounciation(word1, dictionary)
	#pronounciation = pronounciation.split(' ')
	source = open('4.txt', 'r')
	words = source.readlines()
	randIndex = random.randint(0, 500)
	subset = words[randIndex:]
	print "len(subset) = ",len(subset)
	#print "randIndex = ",randIndex,"firstWord = ",firstWord
	t = nltk.NgramModel(3, source)
	s = t.generate(10, subset)
	string = ' '.join(s)
	string = re.sub(r'\n', r'', string)
	print string

	#counts = get_counts(tokens)
	#print counts['a']
	#print getNumSyllables(pronounciation)
	#print loop('orange', dictionary)
	#print getLastSyllable(getPronounciation(word1, dictionary))
#clean('dickens.txt')
main()
#if __name__ == '__main__':
    #cProfile.run('main()')