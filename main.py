import random
import re
import string
import itertools
import time




words = []

with open("words.txt", "r") as file:
	for line in file.readlines():
		words.append(line.strip())      
        
class Wordle:
    def __init__(self) -> None:
        self.answer = None
        
    def generate_answer(self):
        selected_index = random.randint(0, len(words)-1)
        self.answer = words[selected_index]
    
    def guess(self, word):
        # 0 for no match
        # 1 for somewhere in word
        # 2 for exact match
        ret = []
        _s = dict()
        for index in range(5):
            alphabet = word[index]
            if alphabet == self.answer[index]:
                ret.append(2)
                    
            elif (alphabet in self.answer):
                if(alphabet in _s.keys()):
                    _same_indexes = [i for i, x in enumerate(self.answer) if x == word[index]]
                    same_indexes = []
                    for index in _same_indexes:
                        if(word[index] != self.answer[index]): same_indexes.append(index)
                    if(len(same_indexes) > _s[alphabet]):
                        ret.append(1)
                        _s[alphabet] += 1
                    else:
                        ret.append(0)
                else:
                    _same_indexes = [i for i, x in enumerate(self.answer) if x == word[index]]
                    same_indexes = []
                    for index in _same_indexes:
                        if(word[index] != self.answer[index]): same_indexes.append(index)
                    # print(same_indexes, _same_indexes, index, alphabet)
                    if(same_indexes):
                        ret.append(1)
                        _s[alphabet] = 1
                    else:
                        ret.append(0)
                            

            else:
                ret.append(0)
        
        return ret


def generate_freq_ratio(words):
    freq_dict = dict(zip(list(string.ascii_lowercase), [0]*len(list(string.ascii_lowercase)))) 
    for word in words:
        for letter in word:
            freq_dict[letter] += 1
    
    return freq_dict

def generate_perc_dict(freq_dict):
    sum = 0 
    for i in freq_dict.values():
        sum += i
    
    perc_dict = {}
    for i, letter in enumerate(freq_dict):
        occurance = list(freq_dict.values())[i]
        perc_dict[letter] = occurance/sum
        
    return perc_dict



# ============================================================================================
# ANSWER GENERATION
# ============================================================================================

class AlphabetCtx:
    def __init__(self, ctx, alphabet):
        self.alphabet = alphabet
        self.parent_ctx = ctx

        self.least_occurances = 0
        self.checked = False
        self._positions = set()
        self._positions_not_in = set()
        
        self.not_in_word = False

    def set_occurance(self, occurance, checked=False):
        alphabet = self.alphabet
        

        if(occurance == None):
            checked = True
            self.not_in_word = True
            self.parent_ctx.not_in_word.add(alphabet)
            self._positions_not_in = set()
            if(alphabet in list(self.parent_ctx.positions_not_in)):
                del self.parent_ctx.positions_not_in[alphabet]
            self.checked = checked
            return
            
        if(self.least_occurances > occurance):
            return
        
        
        self.least_occurances = occurance
        self.parent_ctx.least_occurances[alphabet] = [self.least_occurances, checked]
        self.checked = checked
        
    @property
    def positions(self):
        return self._positions


    @positions.setter
    def positions(self, add_pos):
        alphabet = self.alphabet
        self._positions.add(add_pos)
        if(alphabet in list(self.parent_ctx.positions)):
            self.parent_ctx.positions[alphabet].add(add_pos)
        else:
            self.parent_ctx.positions[alphabet] = set([add_pos])

    @property
    def positions_not_in(self):
        return self._positions_not_in


    @positions_not_in.setter
    def positions_not_in(self, not_pos):
        alphabet = self.alphabet
        self._positions_not_in.add(not_pos)
        if(alphabet in list(self.parent_ctx.positions_not_in)):
            self.parent_ctx.positions_not_in[alphabet].add(not_pos)
        else:
            self.parent_ctx.positions_not_in[alphabet] = set([not_pos])

    @property
    def no_position_not_known(self):
        return self.least_occurances - len(self.positions)



class AnswerContext:
    def __init__(self):
        self.positions = {} # green letters
        self.positions_not_in = {} # orange letters that are not in correct spot
        self.not_in_word = set() # grey letters that are just not in word
        self.least_occurances = {} # least amount of occurances calculated for orange letter
        
        self.alphabets = dict()
        for alphabet in list(string.ascii_lowercase):
            self.alphabets[alphabet] = AlphabetCtx(self, alphabet)
        
    def enter_results(self, result, guess):
        track = dict()
        grey = {}
        orange = {}
        green = {}
        all = {}
        for index, step in enumerate(result):
            alphabet = guess[index]
            
            if(not alphabet in all.keys()):
                all[alphabet] = {0:False, 1:False, 2:False}
            
            if(step == 0):
                if(alphabet in grey.keys()):
                    grey[alphabet].append(index)
                else:
                    grey[alphabet] = [index]
        
            
            if(step == 1):
                if(alphabet in orange.keys()):
                    orange[alphabet].append(index)
                else:
                    orange[alphabet] = [index]
            if(step == 2):
                if(alphabet in green.keys()):
                    green[alphabet].append(index)
                else:
                    green[alphabet] = [index]
                    
            all[alphabet][step] = True

        for alphabet, pack in all.items():
            obj = self.alphabets[alphabet]
            in_grey, in_orange, in_green = list(pack.values())
            
            not_positions = []
            positions = []
            occurances = 0
            checked = False
            not_in_word = False
            
            _in_other_than_grey = False
            if(in_green):
                _in_other_than_grey = True
                positions = green[alphabet]
                occurances += len(positions)
            if(in_orange):
                _in_other_than_grey = True
                not_positions = orange[alphabet]
                occurances += len(not_positions)
            if(in_grey):
                if(_in_other_than_grey):
                    checked = True
                    for position in grey[alphabet]:
                        not_positions.append(position)
                else:
                    not_in_word = True
                
            if(not_in_word):
                obj.set_occurance(None, True)
            else:
                obj.set_occurance(occurances, checked)
                
            for position in positions:
                obj.positions = position
                
            for position in not_positions:
                obj.positions_not_in = position
    
    def check_word_possibility(self, word, least_occurances = {}, not_in_word = [], positions = {}, positions_not_in = {}, default=True):
        if(default):
            
            least_occurances = {}
            for _a, obj in self.alphabets.items():
                least_occurances[_a] = [obj.no_position_not_known, obj.checked]

            positions = self.positions
            positions_not_in = self.positions_not_in
            not_in_word = self.not_in_word
        
            
        for _a in not_in_word: # not in word cleared
            if(_a in word):
                # if(word == "trees"): print("1 eliminated {}".format(word))
                return False
            

        
        
        for alphabet, _positions in positions.items():
            for position in _positions:
                if(word[position] != alphabet): 
                    # if(word == "trees"): print("2 eliminated {}".format(word))
                    return False
        
        for alphabet, avoid_positions in positions_not_in.items():
            least_occurance, limit = least_occurances[alphabet]
            avoid_positions2 = positions.get(alphabet, [])
            
            occurances_i = [pos for pos, _a in enumerate(word) if (_a == alphabet)]
            occurances_f = [pos for pos in occurances_i if ( pos not in avoid_positions) and (pos not in avoid_positions2) ]
            # occurances_i = [occ for occ in occurances_i if occ not in avoid_positions2]
            # occurances_i = [occ for occ in occurances_i if occ not in avoid_positions]
            
            if(len(occurances_f) < least_occurance):
                # if(word == "trees"): print("3 eliminated {} {} {} {} {} {}".format(word, alphabet, occurances_i, avoid_positions, avoid_positions2, least_occurance))
                return False
                
            
            if((len(occurances_f) > least_occurance) and limit):
                # if(word == "trees"): print("4 eliminated {}".format(word))
                return False
                
            
            
                
        return True
    
    def generate_perms(self, word):
        permutations = []
        for combo in itertools.product([0,1,2], repeat=5):
            permutations.append(combo)
        
        # for each position, alphabet in word
        # if alphabet is green in position, remove all orange and grey possibilites for that position
        # if alphabet is not green, remove all green possibilities for that position
        # calculate least po
        for position, alphabet in enumerate(word):
            # print(alphabet in self.not_in_word, alphabet)
            if(alphabet in self.not_in_word):
                permutations = list(filter(
                    lambda perm: (perm[position] == 0),
                    permutations
                ))
                
        
        orange_letters = dict(zip(list(range(5)), list(word)))
        for alphabet, positions in self.positions.items(): # iterate over greens
            
            for position in positions:
                if(word[position] != alphabet): #if alphabet is not green
                    orange_letters[position] = word[position]
                    permutations = list(filter(
                        lambda perm: (perm[position] == 1) or (perm[position] == 0),
                        permutations
                    ))
                else: #if alphabet is green
                    # print("deleted position {} alphabet {}".format(position, word[position]))
                    del orange_letters[position]
                    permutations = list(filter(
                        lambda perm: (perm[position] == 2),
                        permutations
                    ))
        
        _t = {}        
        for position in range(5):
            alphabet = orange_letters.get(position, None)
            if(alphabet == None):
                continue
            
            obj = self.alphabets[alphabet]
            
            if(alphabet not in _t.keys()):
                _t[alphabet] = [obj.no_position_not_known, obj.checked, []]

            iter, neg, positions = _t[alphabet]
            neg = not neg

            
            if((iter == 0) and (not neg)): # if # occurances in word exceeded of occurances checked 
                permutations = list(filter(
                    lambda perm: (perm[position] == 0),
                    permutations
                ))
            else:
                iter = iter -1
                def _f(perm):
                    for _p in positions:
                        if(perm[position] == 1 and perm[_p] == 0):
                            return False
                    return True
                
                permutations = list(filter(
                    _f,
                    permutations
                ))
                
                positions.append(position)
                # print("deleted 2 positon {} alphabet {}".format(position, alphabet))
            _t[alphabet] = [iter, not neg, positions]
            
        individuality_letters = list(set(list(word)))
        # print(individuality_letters, word)
        
        def _f2(perm): #ensures true oranges
            positions_to_jump = dict(zip(individuality_letters, [0]* len(individuality_letters)))
            positions_from_jump = dict(zip(individuality_letters, [0]* len(individuality_letters)))
            for index, _p in enumerate(perm):
                alphabet = word[index]
                if(_p == 0 or _p == 1): positions_to_jump[alphabet] += 1
                if(_p == 1): positions_from_jump[alphabet] += 1
            # print(positions_to_jump, positions_from_jump)
            for alphabet, required_pos in positions_from_jump.items():
                if(required_pos == 0): continue
                
                totallity = 0
                for _a, has_pos in positions_to_jump.items():
                    if(_a == alphabet): continue
                    totallity += has_pos
                
                if(not totallity >= required_pos):
                    # print(totallity, required_pos, alphabet, perm)
                    return False
                
            return True
        
        permutations = list(filter(
            _f2,
            permutations
        ))
        
        return permutations

              

def algorithm(answerctx: AnswerContext, guess_no):
    possible_words = []

    for word in words:
        p = answerctx.check_word_possibility(word)
        if(p): possible_words.append(word)
    
    if(len(possible_words) == 1):
        return possible_words[0]
    
    print("possible words: {}".format(len(possible_words)))
    # print(possible_words, answerctx.positions)
    
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

            
            
    # print(scores)
            
        

def main(answer):
    game = Wordle()
    game.answer = answer
    
    ctx = AnswerContext()
    print("answer: {}".format(answer))
    
    for guess_no in range(6):
        _start_time = time.time()
        print("-"*60)
        print("attempt number {}".format(guess_no + 1))
        start_time = time.time()
        
        
        if(guess_no == 0):
            guess = "tears"
            print("guess: {}".format(guess))
            
        else:

            
            uncaclulated_scores = algorithm(ctx, guess_no)
            
            if(isinstance(uncaclulated_scores, str)):
                print("answer is {}".format(uncaclulated_scores))
                break
            caclulated_scores = {}
            for word, permutations in uncaclulated_scores.items():
                permutations = permutations.values()
                caclulated_scores[word] = sum(permutations)
            
            guess = max(caclulated_scores, key=caclulated_scores.get)
            print("guess: {}".format(guess))
            print("guess score: {}".format(caclulated_scores[guess]))
            print("answer score: {}".format(caclulated_scores[answer]))
    
        
        if(guess == answer):
            break
        
        res = game.guess(guess)
        print("result: {}".format(res))
        ctx.enter_results(res, guess)
        

        print(time.time() - _start_time)
        if(guess == answer):
            break
        
    return guess_no, (time.time() - _start_time)

    
    
    
    
main(random.choice(words))
