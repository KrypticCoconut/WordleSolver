import random
import string

class Wordle:
    def __init__(self) -> None:
        self.answer = None
        
    def generate_answer(self, words):
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

