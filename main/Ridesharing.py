'''
Created on Feb 20, 2012

@author: Sol
'''
import heapq, copy, random
import util.Geo as geo
import main.Analyze as ana
import plot.scatter as scatter
from operator import itemgetter


BASE_DIR = 'C:/Program Files/Weka-3-6/data/Taxi_Trajectory/'
RAW_DIR = BASE_DIR + 'raw/'
PROCESSED_DIR = BASE_DIR + 'processed/'
INF = 9999999
DELTA = 15*60
PACE = 1.3

def loadTripMetaFile(file_name):
    '''build data structure which stores trip meta information'''
    my_file = open(file_name, 'r')
    trip_meta = ['none']
    for line in my_file.readlines():
        fields = line[:-1].split(',')
        trip_meta.append({'taxi_id':int(fields[1]), 'start_point':{'lat':float(fields[2]), 'lng':float(fields[3]), 'time':int(fields[4])}, 'end_point':{'lat':float(fields[5]), 'lng':float(fields[6]), 'time':int(fields[7])}, 'tt':int(fields[8]), 'td':float(fields[9])})
    return trip_meta

def od_merge_mergeable(child_trip, father_trip):
    '''check if this pair of pairs is od-merge mergable and admissible-od-merge mergable'''
    if child_trip['start_point']['time'] >= father_trip['start_point']['time']:
        return False, False, -1
    t_walkLeg1 = geo.distBetween(child_trip['start_point']['lat'], child_trip['start_point']['lng'], father_trip['start_point']['lat'], father_trip['start_point']['lng']) / PACE
    if child_trip['start_point']['time'] + t_walkLeg1 / PACE > father_trip['start_point']['time']:
        return False, False, -1
    t_walkLeg2 = geo.distBetween(child_trip['end_point']['lat'], child_trip['end_point']['lng'], father_trip['end_point']['lat'], father_trip['end_point']['lng']) / PACE
    delay=father_trip['end_point']['time']+t_walkLeg2/PACE-child_trip['end_point']['time']
    '''
    if delay<0:
        print delay, 'f=(%d~%d), c=(%d~%d)'%(father_trip['start_point']['time'], father_trip['end_point']['time'], child_trip['start_point']['time'],child_trip['end_point']['time'])
        delay+=864000
    '''
    #if father_trip['end_point']['time']- child_trip['start_point']['time']+ t_walkLeg2 / PACE  > child_trip['tt'] * (1 + DELTA):
    if delay > DELTA:
        return True, False, delay
        #print father_trip['tt'], t_walkLeg1, t_walkLeg2, child_trip['start_point']['time'], father_trip['start_point']['time'], child_trip['tt'], father_trip['tt']+(t_walkLeg1+t_walkLeg2)/PACE+(father_trip['start_point']['time']-child_trip['start_point']['time']-t_walkLeg1/PACE), child_trip['tt']*(1+DELTA/100)
    return True, True, delay

def produceMergableRelation(dir_name):
    '''update od-merged trip file'''
    names = ['trip_meta', 'admissible_od_merge', 'od_merge']
    files = []
    for name in names:
        files.append(PROCESSED_DIR + dir_name + '/' + name + '.txt')
    trip_meta = loadTripMetaFile(files[0])
    admissible_od_merge=open(files[1], 'w+')
    od_merge = open(files[2], 'w+')
    
    for i in range(1, len(trip_meta)):
        for j in range(i + 1, len(trip_meta)):
            d, a_d, delay=od_merge_mergeable(trip_meta[i], trip_meta[j])
            if d:
                od_merge.write(','.join([str(i), str(j), str(delay)]))
                od_merge.write('\n')
                if a_d:
                    admissible_od_merge.write(','.join([str(i), str(j), str(delay)]))
                    admissible_od_merge.write('\n')
            else: #i is not a child trip of j, test reverse
                d, a_d, delay=od_merge_mergeable(trip_meta[j], trip_meta[i]) 
                if d:
                    od_merge.write(','.join([str(j), str(i), str(delay)]))
                    od_merge.write('\n')
                    if a_d:
                        admissible_od_merge.write(','.join([str(j), str(i), str(delay)]))
                        admissible_od_merge.write('\n')
    admissible_od_merge.close()
    od_merge.close()
    '''
                    if (i not in od_child_trips.keys() or od_child_trips[i][1]>delay) and j:
                    od_child_trips[i]=(j, delay)
                    if j not in od_child_trips.keys() or od_child_trips[j][1]>delay:
                    od_child_trips[j]=(i, delay)
    '''             
  

def loadMergableRelation(dir_name, file_name):
    '''build data structures needed for the heuristics:
    e.g. given (1,3), (2,3)
    father_trips={3:{1:5, 2:5, 'benefit':10, 'children':[1,2]}, }
    child_trips={1:[3], 2:[3], } 
    '''
    names = ['trip_meta', file_name]
    files = []
    for name in names:
        files.append(PROCESSED_DIR + dir_name + '/' + name + '.txt')
    trip_meta = loadTripMetaFile(files[0])
        
    father_trips = {}
    child_trips = {}
    mergable_relation = {}
    
    i=0
    with open(files[1]) as fileobject:
        for line in fileobject:
            i+=1
            c_id, f_id, delay = line[:-1].split(',')
            mergable_relation[c_id+'_'+f_id]=float(delay)
            c_id=int(c_id)
            f_id=int(f_id)
            if f_id not in father_trips:
                father_trips[f_id] = {c_id:trip_meta[c_id]['td'], 'benefit':trip_meta[c_id]['td'], 'children':[c_id]}
            else:
                father_trips[f_id][c_id] = trip_meta[c_id]['td']
                father_trips[f_id]['benefit'] += trip_meta[c_id]['td']
                idx = 0
                while idx < len(father_trips[f_id]['children']) and trip_meta[c_id]['td'] < trip_meta[father_trips[f_id]['children'][idx]]['td']:
                    idx += 1
                    father_trips[f_id]['children'].insert(idx, c_id) 
            if c_id not in child_trips:
                child_trips[c_id] = [f_id]
            else:
                child_trips[c_id].append(f_id)
    
    #sort children list in descending order of their distance 
    '''
    for f_id in father_trips.keys():
        children=[]
        for c_id in father_trips[f_id]['children']:
            children.append(trip_meta[c_id]['td'], c_id)
        children=sorted(children, reverse=True)
        father_trips[f_id]['children']=map(itemgetter(1), children)
    '''
                    
    print "line=%d"%i
    return father_trips, child_trips, mergable_relation, trip_meta

def greedyMaxFather(father_trips, child_trips, option, capacity):
    '''    e.g. given (1,3), (2,3)
    father_trips={3:{1:5, 2:5, 'benefit':10, 'children':[1,2]}, }
    child_trips={1:[3], 2:[3], } 
    '''
    benefit = 0
    merged_trips = {}
       
    while True:
        if father_trips:
            heap = []
            if option == 'random':
                selected = father_trips.keys()[random.randint(0, len(father_trips.keys()) - 1)]
                #selected=father_trips.keys()[-1]
            else:
                if option == 'benefit' or option == 'edge_benefit':
                    for k, v in father_trips.iteritems():
                        benefit_sum = 0
                        for i in range(0, min(capacity, len(v['children']))):
                            benefit_sum += v[v['children'][i]]
                        heap.append((-benefit_sum, k))
                elif option == 'children_no':
                    for k, v in father_trips.iteritems():
                        heap.append((-len(v['children']), k))
                elif option == 'avg_benefit':
                    for k, v in father_trips.iteritems():
                        heap.append((-float(v['benefit']) / len(v['children']), k))
                heapq.heapify(heap)
                _, selected = heapq.heappop(heap)
        else:
            break

        selected_child_trips = []
        for child in copy.deepcopy(father_trips[selected]['children']):
            if len(selected_child_trips) == capacity:
                break
            #the edge is selected only if its benefit no smaller than that of the child
            if 'edge' in option and child in father_trips.keys() and father_trips[selected][child] < father_trips[child]['benefit']:
                continue
            selected_child_trips.append(child)
            benefit += father_trips[selected][child]
        '''update heap'''
        li = [selected]
        if selected_child_trips:
            merged_trips[selected] = copy.deepcopy(selected_child_trips)
            li.extend(selected_child_trips)
            for t_id in li:
                if t_id in child_trips: #update outgoing edges of selected nodes
                    for fid in child_trips[t_id]:
                        #print fid, id
                        father_trips[fid]['benefit'] -= father_trips[fid][t_id]
                        father_trips[fid]['children'].remove(t_id)
                        del father_trips[fid][t_id]
                        if not father_trips[fid]['children']:
                            del father_trips[fid]
                    del child_trips[t_id]
                if t_id in father_trips: #update incoming edges of selected nodes
                    for cid in father_trips[t_id]['children']:
                        child_trips[cid].remove(t_id)
                    del father_trips[t_id] 

    return benefit, merged_trips

def runHeuristics(father_trips, child_trips, mergeable_relation, trip_meta):
    heuristics = ['benefit', 'avg_benefit', 'children_no', 'random']#, 'edge_benefit']
    capacity = [1, 2, 3, INF]
    criteria=['benefit','no_of_merged_trips','max_merge', 'avg_merge', 'max_delay','avg_delay']
    criteria_unit=['km','','','','sec','sec']

    
    res = {}
    for cri in criteria:
        res[cri]={}
        for heur in heuristics:
            res[cri][heur]=[]

    for heur in heuristics:
        for capa in capacity:
            print heur, capa
            _, rp = greedyMaxFather(copy.deepcopy(father_trips), copy.deepcopy(child_trips), heur, capa)
            benefit, max_merge, avg_merge, no_of_merged_trips, max_delay, avg_delay=ana.profiel_ridesharing_plan(rp, mergeable_relation, trip_meta)
            res['benefit'][heur].append(benefit)
            res['no_of_merged_trips'][heur].append(int(no_of_merged_trips))
            res['max_merge'][heur].append(int(max_merge))
            res['avg_merge'][heur].append(avg_merge)
            res['max_delay'][heur].append(max_delay)
            res['avg_delay'][heur].append(avg_delay)

    #scatter.draw_result(res, heuristics, capacity, criteria, criteria_unit)
    
    """format results"""        
    print '%-s%s' % ('\t', '\t\t'.join(criteria))
    for heur in heuristics:
        print '%-s\t' % heur, '\t\t'.join([','.join([ str(item) for item in res[crit][heur] ]) for crit in criteria])
    print
  
def ridesharing(dir_name):
    #read.processRawData(dir_name)
    
    #produceMergableRelation(dir_name)
    #'''
    file_prefixes=['','admissible_']
    for prefix in file_prefixes[1:]:
        father_trips, child_trips, mergeable_relation , trip_meta=loadMergableRelation(dir_name, prefix+'od_merge')
        #'''
        ana.upper_bound(trip_meta, child_trips)
        ana.avg_tt_td(trip_meta)
        if prefix=='':
            rp=ana.maximal_trip_analysis(child_trips, father_trips, mergeable_relation)
            print ana.profiel_ridesharing_plan(rp, mergeable_relation, trip_meta)         
        else:
            runHeuristics(father_trips, child_trips, mergeable_relation, trip_meta)
        #'''
        print
    #'''
if __name__ == "__main__":
    #ridesharing('Taxi_Shanghai')
    ridesharing('test')
    #readFromSynthesizedData('synthesized')
    #readFromProcessedData('Taxi_Shanghai')
