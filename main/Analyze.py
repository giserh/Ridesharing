'''
Created on Apr 7, 2012

@author: Sol
'''
from operator import itemgetter
import copy


import main.Constants as Constants


def upper_bound(trip_meta, child_trips, father_trips, capacity):
    upper_bound_by_child=0.0
    for c_id, _ in child_trips.iteritems():
        upper_bound_by_child+=trip_meta[c_id]['td']
    
    upper_bound_by_father=0.0
    for f_id, _ in father_trips.iteritems():
        for c_id in father_trips[f_id]['children'][:capacity]:
            upper_bound_by_father+=trip_meta[c_id]['td']
    print upper_bound_by_child, upper_bound_by_father
    
    return min(upper_bound_by_child, upper_bound_by_father)

def avg_tt_td(trip_meta):
    tt_sum=0.0
    td_sum=0.0
    for trip in trip_meta[1:]:
        tt_sum+=trip['tt']
        td_sum+=trip['td']
    print 'avg_tt=%f, avg_td=%f' %(tt_sum/len(trip_meta), td_sum/len(trip_meta))

def optimal_heuristics(child_trips, father_trips, mergeable_relation, trip_meta, capacity):
    rp={}
    
    while father_trips:    
		sink_trips=[]
		for f_id, _ in father_trips.iteritems():
			if f_id not in child_trips.keys():
				sink_trips.append(f_id)
		
		'''
		child_trips_without_maximal_father_trips=[]
		for c_id, v in child_trips.iteritems():
			if not (set(maximal_trips) & set(v)):
				child_trips_without_maximal_father_trips.append(c_id)
		print 'no_of_maximal_father=%d, no_of_non_maximal_father=%d, no_of_father=%d, no_of_child=%d, no_of_child_without_maximal_father=%d'%(len(maximal_trips), len(father_trips)-len(maximal_trips), len(father_trips),len(child_trips), len(child_trips_without_maximal_father_trips))
		
		print maximal_trips
		for c_id in child_trips_without_maximal_father_trips[:5]:
			print c_id,  child_trips[c_id]
		'''
		
		sink_ids=[]    
		for c_id, v in child_trips.iteritems():
			intersec=set(v) & set(sink_trips)
			if intersec:
				min_delay=Constants.INF
				sink_id=-1
				for f_id in intersec:
					if mergeable_relation[str(c_id)+'_'+str(f_id)]<min_delay:
						sink_id=f_id
						min_delay=mergeable_relation[str(c_id)+'_'+str(f_id)]
				sink_ids.append(sink_id)
				if sink_id in rp:
					rp[sink_id].append(c_id)
				else:
					rp[sink_id]=[c_id]
		sink_ids=list(set(sink_ids))

		if(capacity<Constants.INF):
			#sort by benefit
			for sink_id in sink_ids:
				if len(rp[sink_id])>capacity:
					children=[]
					for c in rp[sink_id]:
						children.append((trip_meta[c]['td'], c))
					children=sorted(children, reverse=True)
					rp[sink_id]=map(itemgetter(1), children[:capacity])
		
	
		'''update father_trips and child_trips'''
		for sink_id in sink_ids:
			selected=sink_id
			li = [selected]
			if rp[selected]:
				li.extend(copy.deepcopy(rp[selected]))
				for t_id in li:
					if t_id in child_trips: #update outgoing edges of selected nodes
						for fid in child_trips[t_id]:
							father_trips[fid]['benefit'] -= trip_meta[t_id]['td']
							father_trips[fid]['children'].remove(t_id)
							del father_trips[fid][t_id]
							if not father_trips[fid]['children']:
								del father_trips[fid]
						del child_trips[t_id]
					if t_id in father_trips: #update incoming edges of selected nodes
						for cid in father_trips[t_id]['children']:
							child_trips[cid].remove(t_id)
							if not child_trips[cid]:
								del child_trips[cid]
						del father_trips[t_id]

    return rp

def profile_ridesharing_plan(rp, mergeable_relation, trip_meta):
    items = rp.items()
    #items.sort(key=lambda merged_trips:merged_trips[1], reverse=True )
    items.sort(key=lambda merged_trips:merged_trips[0])
    
    benefit=0.0
    max_merge = 0
    max_delay=0.0
    sum_delay=0.0
    no_of_merged_trips=0
    for sink_id ,v in rp.iteritems():
        for c_id in v:
            benefit+=trip_meta[c_id]['td']
			delay=mergeable_relation[str(t_id)+'_'+str(sink_id)]
            sum_delay+=delay
            max_delay=max(max_delay, delay)
        no_of_merged_trips += len(v)
        max_merge = max(max_merge, len(v))
           
    avg_merge=float(no_of_merged_trips)/len(rp)
    avg_delay=sum_delay/no_of_merged_trips
    #print benefit, max_merge, avg_merge, no_of_merged_trips, max_delay, avg_delay
    return (benefit, no_of_merged_trips, avg_delay,int(max_merge), int(avg_merge),  max_delay )
                            
    
    