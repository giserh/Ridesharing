'''
Created on Feb 2, 2012

@author: Sol
'''
import matplotlib.pyplot as plt
import pylab
from matplotlib.ticker import EngFormatter
import main.Constants as Constants

COLORS=['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
MARKERS=['o','s','^','p', 'D',  'h', 'H', '+']

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


def draw_variant_capacity(data, heuristics, capacity, criteria, criteria_unit, dirname):  
    for l in range(len(data)):
        data[l]=[int(dis/1000) for dis in data[l]]
    
    x_tick_names=[str(capa) for capa in capacity[:-1]]+['Unbounded']
    x_axis=range(1,len(x_tick_names)+1)
    
    '''
    for heur in heuristics:
        res[criteria[0]][heur]=[int(v/1000) for v in res[criteria[0]][heur]]
    '''
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
        
        max_value=max([max(series) for series in data])
        min_value=min([min(series) for series in data])
        if idx==2:
            upper_offset=0.13
            lower_offset=0.02
        elif idx==0:
            upper_offset=lower_offset=int((max_value-min_value)*0.05)+1
        else:
            upper_offset=lower_offset=int((max_value-min_value)*0.05)+1
            if idx==5:
                upper_offset+=350
            
        ax.axis([0,len(x_axis)+1,min_value-lower_offset,max_value+upper_offset])
        
        ###################################
        #pylab.xticks(x_axis, x_tick_names)
        ###################################
        ax.set_xticks(x_axis)  
        ax.set_xticklabels(x_tick_names)
        #formatter = EngFormatter(unit=criteria_unit[idx], places=1)
        #ax.yaxis.set_major_formatter(formatter)

        for j in range(len(heuristics)):
            ax.plot(x_axis, data[j], color=COLORS[j],  marker=MARKERS[j], markersize=10, markeredgecolor=COLORS[j], linestyle='-', linewidth=2, label=heuristics[j])
        
        ax.legend(heuristics, loc='best',numpoints=1, markerscale=1.3)
        plt.savefig(Constants.SAVEDIR+str(idx)+'_'+dirname)
    #plt.show()

def draw_variant_delay(data, heuristics, delay, criteria, criteria_unit, dirname): 
    for l in range(len(data)):
        data[l]=[int(dis/1000) for dis in data[l]]
    
    x_tick_names=[]
    for d in delay:
        if d<Constants.INF:
            x_tick_names.append(str(int(d/60))) 
        else:
            x_tick_names.append('Unbounded')
                                
    x_axis=range(1,len(x_tick_names)+1)
 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(True)
    
    ax.set_title(criteria[0])
    ax.set_xlabel('Delay Threshold (minutes)')
    idx=0
    y_label=criteria[idx]
    if criteria_unit[idx]:
        y_label+='('+criteria_unit[idx]+')'
    ax.set_ylabel(y_label)
    
    max_value=max(max(line) for line in data)
    min_value=min(min(line) for line in data)
    upper_offset=lower_offset=int((max_value-min_value)*0.05)+1
       
    ax.axis([0,len(x_axis)+1,min_value-lower_offset,max_value+upper_offset])
    
    ###################################
    #pylab.xticks(x_axis, x_tick_names)
    ###################################
    ax.set_xticks(x_axis)  
    ax.set_xticklabels(x_tick_names)
    #formatter = EngFormatter(unit=criteria_unit[idx], places=1)
    #ax.yaxis.set_major_formatter(formatter)

    for j in range(len(heuristics)):
        ax.plot(x_axis, data[j], color=COLORS[j],  marker=MARKERS[j], markersize=10, markeredgecolor=COLORS[j], linestyle='-', linewidth=2, label=heuristics[j])
    
    ax.legend(heuristics, loc='best',numpoints=1, markerscale=1.3)
    plt.savefig(Constants.SAVEDIR+str(idx)+'_delay_'+dirname)
    #plt.show()

  
    

