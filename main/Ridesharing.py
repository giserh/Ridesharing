'''
Created on Feb 20, 2012

@author: Sol
'''
import heapq, copy, random, time
import util.Geo as geo
import io.ReadTrips as read
import main.Analyze as ana, main.Constants as Constants
import plot.scatter as scatter
import plot.Graph as networkx
from operator import itemgetter


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
    t_walkLeg1 = geo.distBetween(child_trip['start_point']['lat'], child_trip['start_point']['lng'], father_trip['start_point']['lat'], father_trip['start_point']['lng']) / Constants.PACE
    if child_trip['start_point']['time'] + t_walkLeg1 > father_trip['start_point']['time']:
        return False, False, -1
    t_walkLeg2 = geo.distBetween(child_trip['end_point']['lat'], child_trip['end_point']['lng'], father_trip['end_point']['lat'], father_trip['end_point']['lng']) / Constants.PACE
    delay = father_trip['end_point']['time'] + t_walkLeg2 - child_trip['end_point']['time']-child_trip['tt']
    '''
    if delay<0:
        print delay, 'f=(%d~%d), c=(%d~%d)'%(father_trip['start_point']['time'], father_trip['end_point']['time'], child_trip['start_point']['time'],child_trip['end_point']['time'])
        delay+=864000
    '''
    #if father_trip['end_point']['time']- child_trip['start_point']['time']+ t_walkLeg2 / PACE  > child_trip['tt'] * (1 + DELTA):
    if delay > Constants.DELTA:
        return True, False, delay
        #print father_trip['tt'], t_walkLeg1, t_walkLeg2, child_trip['start_point']['time'], father_trip['start_point']['time'], child_trip['tt'], father_trip['tt']+(t_walkLeg1+t_walkLeg2)/PACE+(father_trip['start_point']['time']-child_trip['start_point']['time']-t_walkLeg1/PACE), child_trip['tt']*(1+DELTA/100)
    return True, True, delay

def produceMergableRelation(dir_name, delay_array=[], output=False):
    '''update od-merged trip file'''
    start = time.time()   
    names = ['trip_meta', 'od_merge']
    
    insert_idx = 1
    for delay in delay_array[:-1]:
        names.insert(insert_idx, 'od_merge_' + str(delay))
        insert_idx += 1
    file_names = []
    for name in names:
        file_names.append(Constants.PROCESSED_DIR + dir_name + '/' + name + '.txt')
    
    trip_meta = loadTripMetaFile(file_names[0])
   
    if delay_array:
        child_sets = {}
        upper_bound = []
        for i in range(len(delay_array)):
            child_sets[i] = []
            upper_bound.append(0)
    
    if output:
        pair_files = []
        for file_name in file_names[1:]:
            pair_files.append(open(file_name, 'w+'))
    
    for i in range(1, len(trip_meta)):
        for j in range(i + 1, len(trip_meta)):
            mergeable = False
            d, a_d, delay = od_merge_mergeable(trip_meta[i], trip_meta[j])
            if d:
                c_id = i
                f_id = j
                mergeable = True
            else: #i is not a child trip of j, test reverse
                d, a_d, delay = od_merge_mergeable(trip_meta[j], trip_meta[i])
                if d:
                    c_id = j
                    f_id = i
                    mergeable = True
            if mergeable:
                if delay_array:
                        for idx in range(len(child_sets)):
                            if delay <= delay_array[idx]:
                                if c_id not in child_sets[idx]:
                                    child_sets[idx].append(c_id)

                if output:
                        for idx in range(len(delay_array)):
                            if delay <= delay_array[idx]:
                                pair_files[idx].write(','.join([str(c_id), str(f_id), str(delay)]) + '\n')

    if delay_array:
        for i in range(len(child_sets)):
            benefit = 0.0
            for child in child_sets[i]:
                benefit += trip_meta[child]['td']
            upper_bound[i] = benefit
    if output:
        for pair_file in pair_files:
            pair_file.close()
    
    elapsed = int((time.time() - start) / 60)
    print "%d minutes elapsed" % elapsed
    #print upper_bound, '\n'
    
    return upper_bound  

def loadMergableRelation(dir_name, file_name, maximum_delay, graphViz=False):
    '''build data structures needed for the heuristics:
    e.g. given (1,3), (2,3)
    father_trips={3:{1:5, 2:5, 'benefit':10, 'children':[1,2]}, }
    child_trips={1:[3], 2:[3], } 
    '''
    start = time.time()
    
    names = ['trip_meta', file_name]
    files = []
    for name in names:
        files.append(Constants.PROCESSED_DIR + dir_name + '/' + name + '.txt')
    trip_meta = loadTripMetaFile(files[0])
    
    if graphViz:
        graph_relation = open(Constants.PROCESSED_DIR + dir_name + '/graph_relation.gv', 'w+')
        graph_relation.write('digraph graphname {\n')
    
    father_trips = {}
    child_trips = {}
    mergeable_relation = {}
   
    line_count = 0
    MAXIMUM_NO_OF_FATHER = Constants.INF
    with open(files[1]) as fileobject:
        for line in fileobject:
            c_id, f_id, delay = line[:-1].split(',')
            delay = float(delay)
            if delay <= maximum_delay:
                if graphViz:
                    graph_relation.write(c_id + " -> " + f_id + ";\n")
                pair_id = c_id + '_' + f_id
                line_count += 1
                c_id = int(c_id)
                f_id = int(f_id)
                
                mergeable_relation[pair_id] = delay
                if c_id not in child_trips.keys():
                    child_trips[c_id] = [f_id]
                else:#
                    if not (file_name == 'od_merge' and len(child_trips[c_id]) > MAXIMUM_NO_OF_FATHER):
                        child_trips[c_id].append(f_id)
                    #only save MAXIMUM_NO_OF_FATHER top fathers with minimum delay  
                    elif delay < mergeable_relation[str(c_id) + '_' + str(child_trips[c_id][-1])]:
                        purge_f_id = child_trips[c_id][-1]
                        del mergeable_relation[str(c_id) + '_' + str(purge_f_id)]
                        
                        #update father_trips accordingly
                        father_trips[purge_f_id]['children'].remove(c_id)
                        del father_trips[purge_f_id][c_id]
                        father_trips[purge_f_id]['benefit'] -= trip_meta[c_id]['td']
                        if not father_trips[purge_f_id]['children']:
                            del father_trips[purge_f_id]
    
                        child_trips[c_id][-1] = f_id             
                        # re-sort fathers based on delay
                        fathers = []
                        for f in child_trips[c_id]:
                            fathers.append((mergeable_relation[str(c_id) + '_' + str(f)], f))
                        fathers = sorted(fathers)
                        child_trips[c_id] = map(itemgetter(1), fathers)
                    else:
                        del mergeable_relation[pair_id]
                if pair_id in mergeable_relation.keys():
                    if f_id not in father_trips.keys():
                        father_trips[f_id] = {c_id:trip_meta[c_id]['td'], 'benefit':trip_meta[c_id]['td'], 'children':[c_id]}
                    else:
                        father_trips[f_id][c_id] = trip_meta[c_id]['td']
                        father_trips[f_id]['benefit'] += trip_meta[c_id]['td']
                        father_trips[f_id]['children'].append(c_id)
       
    if graphViz:
        graph_relation.write('}')
        graph_relation.close()
    
    #sort children list in descending order of their distance 
    for f_id in father_trips.keys():
        children = []
        for c_id in father_trips[f_id]['children']:
            children.append((trip_meta[c_id]['td'], c_id))
        children = sorted(children, reverse=True)
        father_trips[f_id]['children'] = map(itemgetter(1), children)
                        
    print "%s has %d lines" % (file_name , line_count)
    elapsed = int((time.time() - start) / 60)
    print "%d minutes elapsed\n" % elapsed
    
    return father_trips, child_trips, mergeable_relation, trip_meta

"""
def greedyMaxFather(father_trips, child_trips, option, capacity):
    '''    e.g. given (1,3), (2,3)
    father_trips={3:{1:5, 2:5, 'benefit':10, 'children':[1,2]}, }
    child_trips={1:[3], 2:[3], } 
    '''
    print option, capacity
    
    benefit = 0
    merged_trips = {}
       
    while father_trips:      
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
        
        selected_child_trips = []
        for child in copy.deepcopy(father_trips[selected]['children']):
            if len(selected_child_trips) == capacity:
                break
            #the edge is selected only if its benefit no smaller than that of the child
            if 'edge' in option and child in father_trips.keys() and father_trips[selected][child] < father_trips[child]['benefit']:
                continue
            selected_child_trips.append(child)
            benefit += father_trips[selected][child]
        
        '''update father_trips and child_trips'''
        li = [selected]
        if selected_child_trips:
            merged_trips[selected] = copy.deepcopy(selected_child_trips)
            li.extend(selected_child_trips)
            for t_id in li:
                if t_id in child_trips: #update outgoing edges of selected nodes
                    for fid in child_trips[t_id]:
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
"""

"""
def bounded_capacity(dir_name, capacity_array=[1, 2, 3, 4, 5, Constants.INF], delay=Constants.INF):
    heuristics = ['upper_bound', 'optimal_filter', 'benefit', 'avg_benefit', 'children_no', 'random', ]#, 'edge_benefit']
    criteria = ['saved_driving_distance']#,'no_of_saved_trips','avg_delay','max_merge', 'avg_merge', 'max_delay']
    criteria_unit = ['km']#,'','sec','','','sec']
    
    capacity_array = [1, 2, 3, 4, 5, Constants.INF]

    filename = 'od_merge'
    if delay < Constants.INF:
        filename += '_' + str(delay)
    father_trips, child_trips, mergeable_relation , trip_meta = loadMergableRelation(dir_name, filename, delay)
    '''
    res = {}
    for cri in criteria:
        res[cri]={}
        for heur in heuristics:
            res[cri][heur]=[]
    '''    
    data = []
    for heur in heuristics:
        data.append([])
    
    for i in range(len(heuristics)):
        for capa in capacity_array:
            print heuristics[i], capa
            if i == 0:
                data[i].append(ana.upper_bound(trip_meta, child_trips, father_trips, capa))
            else:
                if i == 1:
                    rp = ana.optimal_heuristics(copy.deepcopy(child_trips), copy.deepcopy(father_trips), mergeable_relation, trip_meta, capa)
                else:
                    _, rp = greedyMaxFather(copy.deepcopy(father_trips), copy.deepcopy(child_trips), heur, capa)
                    #benefit, max_merge, avg_merge, no_of_merged_trips, max_delay, avg_delay=ana.profile_ridesharing_plan(rp, mergeable_relation, trip_meta)
                results = ana.profile_ridesharing_plan(rp, mergeable_relation, trip_meta)
                data[i].append(results[0])
    scatter.draw_variant_capacity(data, heuristics, capacity_array, criteria, criteria_unit, dir_name)
    
    '''
    '''format results'''        
    print '%-s%s' % ('\t', '\t\t'.join(criteria))
    for heur in heuristics:
        print '%-s\t' % heur, '\t\t'.join([','.join([ str(item) for item in res[crit][heur] ]) for crit in criteria])
    print
    '''
"""

"""
def bounded_delay(dir_name, upper_bound, DELAY=[900, 1800, 2700, 3600, Constants.INF]):
    #'''
    criteria = ['saved_driving_distance', 'no_of_saved_trips', 'avg_delay', 'max_merge', 'avg_merge', 'max_delay']
    criteria_unit = ['km', '', 'sec', '', '', 'sec']
    
    heuristics = ['upper_bound', 'optimal_filter', 'benefit', 'avg_benefit', 'children_no', 'random']
    
    #data=[upper_bound[:len(DELAY)]]
    data = []
    for heur in heuristics[:]:
        data.append([])

    for i in range(len(DELAY)):
        pair_file = 'od_merge'
        if DELAY[i] < Constants.INF or len(heuristics) > 2:
            if DELAY[i] < Constants.INF:
                pair_file += '_' + str(DELAY[i])
            father_trips, child_trips, mergeable_relation , trip_meta = loadMergableRelation(dir_name, pair_file, DELAY[i])
        for j in range(len(heuristics)):
            if j == 0:
                if DELAY[i] < Constants.INF:
                    data[j].append(ana.upper_bound(trip_meta, child_trips, father_trips, Constants.INF))
                else:
                    data[j].append(upper_bound[i])
            else:
                if j == 1 and DELAY[i] < Constants.INF:
                        rp = ana.optimal_heuristics(copy.deepcopy(child_trips), copy.deepcopy(father_trips), mergeable_relation, trip_meta, Constants.INF)
                elif j > 1:
                    _, rp = greedyMaxFather(copy.deepcopy(father_trips), copy.deepcopy(child_trips), heuristics[j], Constants.INF)
                if not (j == 1 and DELAY[i] == Constants.INF):
                    results = ana.profile_ridesharing_plan(rp, mergeable_relation, trip_meta)
                    data[j].append(results[0])
                else:
                    data[j].append(upper_bound[i])
    scatter.draw_variant_delay(data, heuristics, DELAY, criteria, criteria_unit, dir_name)
    #'''
"""

def ridesharing(dir_name):
    read.processRawData(dir_name)
    #DELAY = [900, 1800, 2700, 3600, Constants.INF]
    #upper_bound=produceMergableRelation(dir_name, DELAY, True)
    # unbounded capacity, bounded delay
    #bounded_delay(dir_name, upper_bound, DELAY[:-1])
    
    # bounded capacity, unbounded delay
    #bounded_capacity(dir_name, delay=900)
    
    """
    heur= 'optimal_filter'
    capacity = [2, 4, 8, 16, 32, INF]
    criteria=['saved_driving_distance','no_of_saved_trips','avg_delay','max_merge', 'avg_merge', 'max_delay']
    criteria_unit=['km','','sec','','','sec']
    res = {}
    for cri in criteria:
        res[cri]={heur:[]}
        
    father_trips, child_trips, mergeable_relation , trip_meta=loadMergableRelation(dir_name, 'od_merge', INF)
    ana.upper_bound(trip_meta, child_trips)
    '''
    '''
    for capa in capacity[:]:
        rp=ana.optimal_heuristics(copy.deepcopy(child_trips), copy.deepcopy(father_trips), mergeable_relation, trip_meta, capa)
        results=ana.profile_ridesharing_plan(rp, mergeable_relation, trip_meta)
        for i in range(len(criteria)):
            res[criteria[i]][heur].append(results[i])
    scatter.draw_result(res, [heur], capacity, criteria, criteria_unit)
        
    """

if __name__ == "__main__":
    ridesharing('Taxi_Shanghai')
