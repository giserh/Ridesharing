'''
Created on Feb 27, 2012

@author: Sol
'''

    


import math as m



def distBetween(lat1, lng1, lat2, lng2):
    '''return distance between two geo points in meters'''
    EARTHRADIUS=3958.75;
    MILETOKM=1.609344;
    dLat=m.radians(lat2-lat1)
    dLng=m.radians(lng2-lng1)
    a=m.sin(dLat/2)**2+m.cos(m.radians(lat1))*m.cos(m.radians(lat2))*m.sin(dLng/2)**2
    c=2*m.atan2(m.sqrt(a), m.sqrt(1-a))
    return EARTHRADIUS*MILETOKM*1000*c;


