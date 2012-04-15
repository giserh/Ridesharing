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
    capacity=[1,2,3,'INF']
    
    COLORS=['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    MARKERS=['o','s','^','p', 'D', '+', 'h', 'H']
    
    x_tick_names=[str(capa) for capa in capacity[:-1]]+['Unbounded']
    x_axis=range(1,len(x_tick_names)+1)
    
    
    for idx in range(len(criteria)): 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        ax.set_title(criteria[idx])
        ax.set_xlabel('Ridesharing capacity')
        ax.set_ylabel(criteria[idx])
        max_value=max([max(res[criteria[idx]][heur]) for heur in heuristics])
        min_value=min([min(res[criteria[idx]][heur]) for heur in heuristics])
        offset=int((max_value-min_value)*0.05)+1
        ax.axis([0,len(x_axis)+1,min_value-offset,max_value+offset])
        
        ###################################
        #pylab.xticks(x_axis, x_tick_names)
        ###################################
        ax.set_xticks(x_axis)  
        ax.set_xticklabels(x_tick_names)
        formatter = EngFormatter(unit=criteria_unit[idx], places=1)
        ax.yaxis.set_major_formatter(formatter)

        for j in range(len(heuristics)):
            ax.plot(x_axis, res[criteria[idx]][heuristics[j]], color=COLORS[j],  marker=MARKERS[j], markersize=10, markeredgecolor=COLORS[j], linestyle='-', linewidth=2, label=heuristics[j])
        ax.legend(heuristics, loc='lower right',numpoints=1, markerscale=1.3)
        plt.savefig(SAVEDIR+criteria[idx])


    
    

