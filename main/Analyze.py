'''
Created on Apr 7, 2012

@author: Sol
'''
def upper_bound(trip_meta, child_trips):
    benefit=0.0
    for c_id, _ in child_trips.iteritems():
        benefit+=trip_meta[c_id]['td']
    print 'benefit=%f'%benefit
    '''
    max_delay=0.0
    sum_delay=0.0
    fathers={}
    for c_id, (f_id, delay) in od_child_trips.iteritems():
        sum_delay+=delay
        max_delay=max(max_delay, delay)
        if f_id not in fathers.keys():
            fathers[f_id]=c_id
        else:
            fathers[f_id].append(c_id)
    avg_delay=sum_delay/len(od_child_trips)

    max_merge=0
    sum_merge=0
    for f_id, v in fathers.iteritems():
        sum_merge+=len(v)
        max_merge=max(max_merge, len(v))
    avg_merge=max_merge/len(fathers)
    
    print 'max_merge=%d, avg_merge=%f, max_delay=%f, avg_delay=%f'%(max_merge, avg_merge, max_delay, avg_delay)
    '''

def avg_tt_td(trip_meta):
    tt_sum=0.0
    td_sum=0.0
    for trip in trip_meta[1:]:
        tt_sum+=trip['tt']
        td_sum+=trip['td']
    print 'avg_tt=%f, avg_td=%f' %(tt_sum/len(trip_meta), td_sum/len(trip_meta))

def maximal_trip_analysis(child_trips, father_trips, mergeable_relation):
    maximal_trips=[]
    for f_id, _ in father_trips.iteritems():
        if f_id not in child_trips.keys():
            maximal_trips.append(f_id)
    child_trips_without_maximal_father_trips=[]
    
    for c_id, v in child_trips.iteritems():
        if not (set(maximal_trips) & set(v)):
            child_trips_without_maximal_father_trips.append(c_id)
    print 'no_of_maximal_father=%d, no_of_non_maximal_father=%d, no_of_father=%d, no_of_child=%d, no_of_child_without_maximal_father=%d'%(len(maximal_trips), len(father_trips)-len(maximal_trips), len(father_trips),len(child_trips), len(child_trips_without_maximal_father_trips))
    
    rp={}
    for id in maximal_trips:
        rp[id]=[]
    for c_id, v in child_trips.iteritems():
        intersec=set(v) & set(maximal_trips)
        if intersec:
            min_delay=999999
            sink_id=-1
            for f_id in intersec:
                if mergeable_relation[str(c_id)+'_'+str(f_id)]<min_delay:
                    sink_id=f_id
                    min_delay=mergeable_relation[str(c_id)+'_'+str(f_id)]
            rp[sink_id].append(c_id)
    return rp

def profiel_ridesharing_plan(rp, mergeable_relation, trip_meta):
    items = rp.items()
    #items.sort(key=lambda merged_trips:merged_trips[1], reverse=True )
    items.sort(key=lambda merged_trips:merged_trips[0])
    
    benefit=0.0
    max_merge = 0
    sum_merge = 0
    max_delay=0.0
    sum_delay=0.0
    no_of_merged_trips=0
    for sink_id ,v in rp.iteritems():
        for c_id in v:
            benefit+=trip_meta[c_id]['td']
        no_of_merged_trips += len(v)
        max_merge = max(max_merge, len(v))
        sum_merge+=len(v)
        for t_id in v:
            delay=mergeable_relation[str(t_id)+'_'+str(sink_id)]
            sum_delay+=delay
            max_delay=max(max_delay, delay)
    avg_merge=float(sum_merge)/len(rp)
    avg_delay=sum_delay/no_of_merged_trips
    return benefit, max_merge, avg_merge, no_of_merged_trips, max_delay, avg_delay
                            
    
    