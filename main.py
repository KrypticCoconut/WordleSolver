import random

import time



from emulator import Wordle
from algorithm import algorithm
from contextholder import AnswerContext

words = []


with open("words.txt", "r") as file:
	for line in file.readlines():
		words.append(line.strip())      
        

def start_game(answer):
    game = Wordle()
    ctx = AnswerContext()
    game.answer = answer
    
    print("answer: {}".format(answer))
    
    for guess_no in range(6):
        _start_time = time.time()
        print("-"*60)
        print("attempt number {}".format(guess_no+1))
        start_time = time.time()
        
        
        if(guess_no == 0):
            guess = "tears"
            print("guess: {}".format(guess))
            
        else:
            uncaclulated_scores = algorithm(ctx, words)
            
            if(isinstance(uncaclulated_scores, str)):
                print("-"*60)
                print("answer is {}\ntries needed: {}".format(uncaclulated_scores, guess_no))
                print(ctx.least_occurances)
                break
            
            caclulated_scores = {}
            for word, permutations in uncaclulated_scores.items(): caclulated_scores[word] = sum(permutations.values())
            
            guess = max(caclulated_scores, key=caclulated_scores.get)
            
            
            print("guess: {}".format(guess))
            print("guess score: {}".format(caclulated_scores[guess]))
            print("answer score: {}".format(caclulated_scores[answer]))
    
        
        if(guess == answer):
            print("-"*60)
            print("answer is {}\ntries needed: {}".format(guess, guess_no))
            print(ctx.least_occurances)
            break
        
        res = game.guess(guess)
        print("result: {}".format(res))
        ctx.enter_results(res, guess)
        

        print(time.time() - _start_time)
        
        
        if(guess == answer):
            break
        


    
    
    

start_game(random.choice(words))
