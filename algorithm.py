import time

def algorithm(answerctx, words):
    possible_words = []

    for word in words:
        p = answerctx.check_word_possibility(word)
        if(p): possible_words.append(word)
    
    if(len(possible_words) == 1):
        return possible_words[0]
    
    print("possible words: {}".format(len(possible_words)))
    
    time_per_words = []
    time_per_perms = []
    avg_permutations = []
    scores = dict() 
    for _word in words:
        # print(_word)
        permutation_scores = {}
        tword = time.time()
        permutations = answerctx.generate_perms(_word)
        avg_permutations.append(len(permutations))
        
        
        for i, permutation in enumerate(permutations):
            tperm = time.time()

            _positions_have_to_be= {}
            _alpabets_somewhere = {}
            limits = {}
            
            # add checking steps
            for step_index, alphabet in enumerate(_word):
                step = permutation[step_index]
                if(step == 0):
                    if(alphabet in _alpabets_somewhere.keys()):
                        # _lim = _alpabets_somewhere.get(alphabet)
                        limits[alphabet] = True
                if(step == 1):

                    
                    if(_alpabets_somewhere.get(alphabet, None)):
                        _alpabets_somewhere[alphabet].append(step_index)
                    else:
                        _alpabets_somewhere[alphabet] = [step_index]
                if(step == 2):
                    if(_positions_have_to_be.get(alphabet, None)):
                        _positions_have_to_be[alphabet].append(step_index)
                    else:
                        _positions_have_to_be[alphabet] = [step_index]
                        
            lo = {}
            
            for alphabet, _o in _alpabets_somewhere.items():
                _oc = len(_o)
                lo[alphabet] = [_oc, limits.get(alphabet, False)]
                
            
            selected = []
            for word in possible_words:

                decision = answerctx.check_word_possibility(word, lo, [], _positions_have_to_be, _alpabets_somewhere, default=False)
                    
                if(decision): selected.append(word)

                        
                    
            if(len(selected) > 0): # has a possibility
                INFORMATION_GAINED = float((len(possible_words)/2)/len(selected))
                POSSIBILITY = float(len(selected)/len(possible_words))
                VALUE = float()
                VALUE = POSSIBILITY * INFORMATION_GAINED

                permutation_scores[''.join(str(x) for x in permutation)] = VALUE
                
            time_per_perms.append(time.time() - tperm )
        
        if(len(permutation_scores.values())): scores[_word] = permutation_scores
        time_per_words.append(time.time() - tword)
    
    # print("avg time taken to complete word: {}".format(sum(time_per_words)/len(time_per_words)))
    print("avg permutations: {}".format(sum(avg_permutations)/len(avg_permutations)))
    # print("avg time required to complete 1 permutation: {}".format(sum(time_per_perms)/len(time_per_perms)))
    return scores