# -*- coding: utf-8 -*-

import sys
import pickle
import re
import operator
import random

def cmp(c1, c2):
    a,b = c1
    c,d = c2
    s = b+d
    r = random.uniform(0,s)
    return 1 if r>b else -1


def random_pull(distribution): # dist. is a list of coulpes
    if distribution :
        sorted_couples = sorted(distribution,cmp)
        return sorted_couples[0][0]
    else:
        return None


arg = (int)(sys.argv[1])
print arg
if arg==1:

    print "       ################# TRAINING :"

    with open('text2', 'r') as f:
        phrase = f.readline()

    phrase = phrase.replace(',',' ,')
    phrase = phrase.replace('.',' .')
    phrase = phrase.strip('\n')

    splited = re.split('[ \-]+',phrase )

    TAU = [7,7,7,1]
    RANGE = 10

    word_followings = {} # word : list of (word/concept, relative position) + weights

    concept_followings = {} # concept : list of (word/concept, relative position) + weights
    concept_keys = {} # concept : (word, relative position)
    # for the moment : (pos, word, score)
    concept_clock = {} # concept : clock value
    concept_word = {}
    global_layer = [] # global position : list of concepts or words

    def treat(concept1,concept2,word_followings,j):
        if concept1 in word_followings:
            if j in word_followings[concept1]:
                if concept2 in word_followings[concept1][j]:
                    word_followings[concept1][j][concept2] += 1
                else:
                    word_followings[concept1][j].update({concept2:1})
            else:
                word_followings[concept1].update({j : {concept2:1}})
        else:
            word_followings[concept1] = {j : {concept2:1}}

        return word_followings[concept1][j][concept2]


    i = 0
    for word1 in splited:
        j=0
        global_layer.append([word1])
        limit = min(i+1+RANGE,len(splited))
        for word2 in splited[i+1:limit]:
            j+=1
            a = treat(word1,word2,word_followings,j)
            if a > 1:
                concept = random.random()#"(%s)_0_(%s)_%i"%(word1,word2,j)
                b = treat(word1,concept,concept_followings,j)
                #concept_keys[concept] = {0:word1,j:word2}
                concept_keys[concept] = (j,word2,b)
                concept_clock[concept] = 0
                global_layer[i].append(concept)
        i+=1

    for deep in range(4):
        print "%i ... "%deep

        # concept ->
        for i in range(len(global_layer)-1):
                for concept1 in frozenset(global_layer[i]):

                    # concept -> concept
                    limit = min(i+1+RANGE,len(global_layer))
                    for j in range(len(global_layer[i+1:limit])-1):
                        for concept2 in global_layer[i+j+1]:
                            a = treat(concept1,concept2,concept_followings,j+1)
                            if a > TAU[deep]:
                                concept = random.random#"(%s)_0_(%s)_%i"%(concept1,concept2,j+1)
                                b = treat(concept1,concept,concept_followings,j+1)
                                #concept_keys[concept] = {0:concept1,j:concept2}
                                concept_keys[concept] = (j,concept2,b)
                                concept_clock[concept] = 0
                                global_layer[i].append(concept)
                                
    # concept ->
    for i in range(len(global_layer)-1):
            for concept1 in global_layer[i]:

                
                # concept -> word
                j = 0
                limit = min(i+1+RANGE,len(global_layer))
                for word in splited[i+1:limit]:
                    j+=1
                    a = treat(concept1,word,concept_word,j)
                    """if a > 3:
                        concept = "(%s)_0_(%s)_%i"%(concept1,word,j)
                        b = treat(concept1,concept,concept_followings,j)
                        #concept_keys[concept] = {0:concept1,j:concept2}
                        concept_keys[concept] = (j,word,b)
                        concept_clock[concept] = 0
                        global_layer[i].append(concept)"""

            # word ->
            #i=0
            #for i in range(

    pickle.dump( word_followings, open( "word_followings.p", "wb" ) )
    pickle.dump( concept_followings, open( "concept_followings.p", "wb" ) )
    pickle.dump( concept_word, open( "concept_word.p", "wb" ) )
    pickle.dump( concept_keys, open( "concept_keys.p", "wb" ) )

else:
    word_followings = pickle.load( open( "word_followings.p", "rb" ) )
    concept_followings = pickle.load( open( "concept_followings.p", "rb" ) )
    concept_word = pickle.load( open( "concept_word.p", "rb" ) )
    concept_keys = pickle.load( open( "concept_keys.p", "rb" ) )


print
print "       ################## SAMPLING :"



current_word = '.'
current_pos = 0
result = []

length = 30

word_score = {} # position(global), word : score
concept_score = {} # position(global), concept : score
potential_concepts = {} # concept, position when score>0

#for i in range(length):
#    active_concepts.append({}) # concept, position when score>THETA


def score_update(concept, pos, score, score_dict):
    if pos in score_dict:
        if concept in score_dict:
            score_dict[pos][concept] += score
        else:
            score_dict[pos].update({concept:score})
    else:
        score_dict[pos] = {concept:score}

dot = False
i = 0
while (not dot and i<20) :

    i+=1

    # word -> word :
    try:
        for pos in word_followings[current_word]:
            for word in word_followings[current_word][pos]:
                score_update(word,i+pos,word_followings[current_word][pos][word],word_score)
    except KeyError:
        current_word = '.'
        for pos in word_followings[current_word]:
            for word in word_followings[current_word][pos]:
                score_update(word,i+pos,word_followings[current_word][pos][word],word_score)


    # word -> concept :
    if current_word in concept_followings:
        for pos in concept_followings[current_word]:
            for concept in concept_followings[current_word][pos]:
                if concept in concept_keys:
                    pos,word,score = concept_keys[concept] # maybe we should also train the "word -> concept", but could be redondant
                    score_update(word,i+pos,score,concept_score)
                    #active_concepts[i].add(concept)

    # concept ->
    if i in concept_score:
        for concept1 in concept_score[i]:

            # concept -> concept :
            if concept1 in concept_followings:
                for pos in concept_followings[concept1]:
                    for concept2 in concept_followings[concept1][pos]:
                        score_update(concept2,i+pos,concept_followings[concept1][pos][concept2],concept_score)

                # concept -> word :
                for pos in concept_word[concept1]:
                    for word in concept_word[concept1][pos]:
                        score_update(word,i+pos,concept_word[concept1][pos][word],word_score)

    for word in frozenset(word_score[i+1]):
        #               word_following[current_word][position][:]
        if word not in word_followings[current_word][1]:
            del word_score[i+1][word]

    distribution = word_score[i+1].items()
    current_word = random_pull(distribution)
    #current_word = max(word_score[i+1].iteritems(), key=operator.itemgetter(1))[0]
    result.append(current_word)
    dot = (current_word=='.' or current_word=='?')

print ' '.join(result)
