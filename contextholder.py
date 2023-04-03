
import string
import itertools

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
            
            occurances_f = [pos for pos, _a in enumerate(word) if (_a == alphabet) and ( pos not in avoid_positions) and (pos not in avoid_positions2)]
            # occurances_f = [pos for pos in occurances_i if ( pos not in avoid_positions) and (pos not in avoid_positions2) ]
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