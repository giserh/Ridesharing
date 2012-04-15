'''
Created on Mar 29, 2012

@author: Sol
'''
import doctest
def algorithmX(reversed_sets, sets, solution=[]):
    if not reversed_sets:
        yield list(solution)
    else:
        c = min(reversed_sets, key=lambda c: len(reversed_sets[c]))
        for r in reversed_sets[c]:
            solution.append(sets[r])
            cols = select(reversed_sets, sets, r)
            for s in algorithmX(reversed_sets, sets, solution):
                yield s
            deselect(reversed_sets, sets, r, cols)
            solution.pop()

def select(reversed_sets, sets, r):
    cols = []
    for j in sets[r]:
        for i in reversed_sets[j]:
            for k in sets[i]:
                if k != j:
                    reversed_sets[k].remove(i)
        cols.append(reversed_sets.pop(j))
    return cols

def deselect(reversed_sets, sets, r, cols):
    for j in reversed(sets[r]):
        reversed_sets[j] = cols.pop()
        for i in reversed_sets[j]:
            for k in sets[i]:
                if k != j:
                    reversed_sets[k].add(i)

def inverted_sets(sets):
    inverted_sets = {}
    for set_name, items  in sets.items():
        for item in items:
            if item not in inverted_sets:
                inverted_sets[item]=set()
            inverted_sets[item].add(set_name)
    return inverted_sets

all_subsets= lambda x: [[y for j, y in enumerate(set(x)) if (i >> j) & 1] for i in range(2**len(set(x)))]

def expand(sets):
    mergable_items=[]
    univ=[]
    new_sets=set()
    
    for set_name, items in sets.items():
        mergable_items+=items[1:]
        univ+=items
        for s in all_subsets(items[1:])[:-1]:
            new_sets.add(frozenset(s+[items[0]]))
    mergable_items=set(mergable_items)
    univ=set(univ)
    maximal_items=univ.difference(mergable_items)
    
    i=len(sets)+1
    for s in new_sets:
        sets[str(i)]=list(s)
        i+=1
    return sets, maximal_items, mergable_items, univ
                    
if __name__=="__main__":
    sets = {
    '1': [4, 1, 2],
    '2': [5, 1, 3],
    '3': [6, 2, 3],
    '4': [7, 4],
    '5': [8, 5],
    '6': [9, 6],
    '7': [1],
    '8': [2],
    '9': [3],
    }
    sets, maximal_items, mergable_items,univ=expand(sets)
    #print sets
    #print inverted_sets(sets)
    min_len=len(univ)
    solu=[]
    for sol in algorithmX(inverted_sets(sets),sets):
        solu.append(sol)
        min_len=min(min_len, len(sol))

    #print solu
    for sol in solu:
        if len(sol)==min_len:
            print [s for s in sol if len(s)>1]
    