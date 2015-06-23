import numpy as np

def initialize_rank_scores(head=None, tail_high=5, tail_low=2, tail_num=16, log_score=True):
    '''
    Initializes scores for the listing ranks; 
    
    Loosely inspired by the Long Tail & Google SERP CTRs

    INPUT: 
    - head (None or 1d numpy array):
      * score represents the "head" of the scores
      * if None (default), function uses data from moz.com to score the head
      * to avoid using the head, set head=np.array([])
    - tail_high, tail_low, tail_num (ints):
      * inputs to an np.linspace() function
      * to avoid using the tail, set tail_num=0
    - log_score (bool): if True, takes the natural log of the score

    OUTPUT: 
    - 1d numpy array: an array of length len(head) + tail_num.
    '''
    
    if head!=None:
        head_scores = head
    else:
        # source: https://moz.com/blog/google-organic-click-through-rates-in-2014
        MOZ_DATA = np.array([25, 15, 11, 8, 6.5])    
        head_scores = MOZ_DATA

    tail_scores = np.linspace(extended_high,extended_low,extended_num)
    
    scores = np.append(head_scores, tail_scores)
    if log_score:
        scores = np.log(scores)    # Take the ln of the score  

    return scores