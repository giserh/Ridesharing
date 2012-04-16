'''
Created on Feb 2, 2012

@author: Sol
'''
import matplotlib.pyplot as plt
import pylab
from matplotlib.ticker import EngFormatter


SAVEDIR='E:\\Research\\MobileComputing\\RideSharing\\experiment_result\\'

def draw_trips(trips):
    '''draw all GPS points in trips'''
    COLOR=['b','r','g']
 
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    idx=0
    for t in trips:
        ax.plot(t[1],t[2], t[3], 'o-', c=COLOR[idx%3])
        idx+=1
        
    pad=0.005
    #ax.set_xlim3d(min_lat-pad, max_lat+pad)
    #ax.set_ylim3d(min_lng-pad, max_lng+pad)
    #ax.set_zlim3d(0, 1)
    plt.show()


def draw_result(res, heuristics, capacity, criteria, criteria_unit):
    COLORS=['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    MARKERS=['o','s','^','p', 'D', '+', 'h', 'H']
    
    x_tick_names=[str(capa) for capa in capacity[:-1]]+['Unbounded']
    x_axis=range(1,len(x_tick_names)+1)
    for heur in heuristics:
        res['benefit'][heur]=[int(v/1000) for v in res['benefit'][heur]]
    
    for idx in range(len(criteria)): 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        
        ax.set_title(criteria[idx])
        ax.set_xlabel('Ridesharing capacity')
        y_label=criteria[idx]
        if criteria_unit[idx]:
            y_label+='('+criteria_unit[idx]+')'
        ax.set_ylabel(y_label)
        
        max_value=max([max(res[criteria[idx]][heur]) for heur in heuristics])
        min_value=min([min(res[criteria[idx]][heur]) for heur in heuristics])
        if criteria[idx]=='avg_merge':
            upper_offset=lower_offset=0.02
        elif criteria[idx]=='benefit':
            upper_offset=lower_offset=int((max_value-min_value)*0.05)+1
        else:
            upper_offset=lower_offset=int((max_value-min_value)*0.05)+1
            if criteria[idx]=='avg_delay':
                upper_offset+=100
            
        ax.axis([0,len(x_axis)+1,max(min_value-lower_offset,0),max_value+upper_offset])
        
        ###################################
        #pylab.xticks(x_axis, x_tick_names)
        ###################################
        ax.set_xticks(x_axis)  
        ax.set_xticklabels(x_tick_names)
        #formatter = EngFormatter(unit=criteria_unit[idx], places=1)
        #ax.yaxis.set_major_formatter(formatter)

        for j in range(len(heuristics)):
            ax.plot(x_axis, res[criteria[idx]][heuristics[j]], color=COLORS[j],  marker=MARKERS[j], markersize=10, markeredgecolor=COLORS[j], linestyle='-', linewidth=2, label=heuristics[j])
        
        if  criteria[idx]=='avg_delay' or criteria[idx]=='avg_merge':
            position='upper left'
        else:
            position='lower right'
        ax.legend(heuristics, loc=position,numpoints=1, markerscale=1.3)
        plt.savefig(SAVEDIR+criteria[idx])
    #plt.show()


    
    

