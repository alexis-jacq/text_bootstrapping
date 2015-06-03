phrase = 'phrase test 1 , phrase test 2 . test 1 , phrase 2 , test 1 2'

import re
import operator

splited = re.split('[ \-]+',phrase )

TAU = 2
RANGE = 20

word_followings = {} # word : list of (word/concept, relative position) + weights

concept_followings = {} # concept : list of (word/concept, relative position) + weights
concept_keys = {} # concept : (word, relative position)
# for the moment : (pos, word, score)
concept_clock = {} # concept : clock value
concept_word = {}
global_layer = [] # global position : list of concepts or words

def treat(concept1,concept2,word_followings,j):
    if concept1 in word_followings:
        if concept2 in word_followings[concept1]:
            if j in word_followings[concept1][concept2]:
                word_followings[concept1][concept2][j] += 1
            else:
                word_followings[concept1][concept2].update({j:1})
        else:
            word_followings[concept1].update({concept2 : {j:1}})
    else:
        word_followings[concept1] = {concept2 : {j:1}}

    return word_followings[concept1][concept2][j]


i = 0
for word1 in splited:
    j=0
    global_layer.append([word1])
    limit = min(i+1+RANGE,len(splited))
    for word2 in splited[i+1:limit]:
        j+=1
        a = treat(word1,word2,word_followings,j)
        if a > TAU:
            concept = "(%s)_0_(%s)_%i"%(word1,word2,j)
            b = treat(word1,concept,concept_followings,j)
            #concept_keys[concept] = {0:word1,j:word2}
            concept_keys[concept] = (j,word2,b)
            concept_clock[concept] = 0
            global_layer[i].append(concept)
    i+=1

for deep in range(2):
    print "%i ... "%deep

    # concept ->
    for i in range(len(global_layer)-1):
            for concept1 in global_layer[i]:

                # concept -> concept
                limit = min(i+1+RANGE,len(global_layer))
                for j in range(len(global_layer[i+1:limit])-1):
                    for concept2 in global_layer[i+j+1]:
                        a = treat(concept1,concept2,concept_followings,j+1)
                        if a > TAU:
                            concept = "(%s)_0_(%s)_%i"%(concept1,concept2,j+1)
                            b = treat(concept1,concept,concept_followings,j+1)
                            #concept_keys[concept] = {0:concept1,j:concept2}
                            concept_keys[concept] = (j,concept2,b)
                            concept_clock[concept] = 0
                            global_layer[i].append(concept)
                            
                
                # concept -> word
                j = 0
                for word in splited[i+1:limit]:
                    j+=1
                    a = treat(concept1,word,concept_word,j)
                    if a > TAU:
                        concept = "(%s)_0_(%s)_%i"%(concept1,word,j)
                        b = treat(concept1,concept,concept_followings,j)
                        #concept_keys[concept] = {0:concept1,j:concept2}
                        concept_keys[concept] = (j,word,b)
                        concept_clock[concept] = 0
                        global_layer[i].append(concept)

        # word ->
        #i=0
        #for i in range(

            
print "       ################# TRAINING :"
print word_followings
print "____________"
print concept_followings
print "____________"
print splited
print '____________'
print concept_keys
print
print "       ################## SAMPLING :"

current_word = 'phrase'
current_pos = 0
result = [current_word]

length = 20

word_score = {} # position(global), word : score
concept_score = {} # position(global), concept : score
potential_concepts = {} # concept, position when score>0

#for i in range(length):
#    active_concepts.append({}) # concept, position when score>THETA


def score_update(concept, pos, score, score_dict):
    if pos in score_dict:
        if concept in score_dict:
            scor_dict[pos][concept] += score
        else:
            score_dict[pos].update({concept:score})
    else:
        score_dict[pos] = {concept:score}

for i in range(length):

    # word -> word :
    for word in word_followings[current_word]:
        for pos in word_followings[current_word][word]:
            score_update(word,i+pos,word_followings[current_word][word][pos],word_score)

    # word -> concept :
    if current_word in concept_followings:
        for concept in concept_followings[current_word]:
            if concept in concept_keys:
                pos,word,score = concept_keys[concept] # maybe we should also train the "word -> concept", but could be redondant
                score_update(word,i+pos,score,concept_score)
                #active_concepts[i].add(concept)

    # concept ->
    if i in concept_score:
        for concept1 in concept_score[i]:

            # concept -> concept :
            if concept1 in concept_followings:
                for concept2 in concept_followings[concept1]:
                    for pos in concept_followings[concept1][concept2]:
                        score_update(concept2,i+pos,concept_followings[concept1][concept2][pos],concept_score)

                # concept -> word :
                for word in concept_word[concept1]:
                    for pos in concept_word[concept1][word]:
                        score_update(word,i+pos,concept_word[concept1][word][pos],word_score)

    current_word = max(word_score[i+1].iteritems(), key=operator.itemgetter(1))[0]
    result.append(current_word)

print result
