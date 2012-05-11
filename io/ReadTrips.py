'''
Created on Feb 20, 2012

@author: Sol
'''
import time, glob, csv, os, random
import os.path as path
import util.Geo as geo, main.Constants as Constants


def is_valid_trip(trip_file_name, debug=False):
    """this function determines whether an extracted trip is valid based on some heuristics"""
    #filename=Constants.PROCESSED_DIR+dirname+'/trip_trajectory/'+str(trip_id)+'.txt'
    #gps_point=[]
    trip_file=open(trip_file_name, 'r')
    lines=trip_file.readlines()
    count=0
    for idx in range(len(lines)):
        _, lon, lat, _, _, time=lines[idx].split(',')
        lon=float(lon)
        lat=float(lat)
        time=int(time)
        if count==5: #if the max distance from the start point does not increase in 5 consecutive steps, then disregard the trip 
            return False 
        if idx==0:
            start_time=time
            start_point=(lat, lon)
            max_dist=0
            #gps_point.append((0, lat, lon))
        else:
            dist=geo.distBetween(lat, lon, start_point[0], start_point[1])
            if debug:
                print dist
            if dist<max_dist:
                count+=1
            else:
                max_dist=dist
            #gps_point.append((dist, lat, lon))
    if time-start_time<30:  #if travel time < half minute, disregard the trip
        return False
    return True

def extract_trip_from_one_file(file_name, trip_dir, trip_meta):
    #print file_name
    f = open(file_name)
    # Using a DictReader instead
    r = csv.DictReader(f, ['taxi_id', 'timestamp', 'lng', 'lat', 'unknown1', 'unknown2', 'occupied'])
    trips = []
    max_lat = 0.0
    min_lat = 180
    max_lng = 0.0
    min_lng = 180
    
    lat = []
    lng = []
    timestamp = []
    trip = []
    travelDistance = 0.0
    
    trip_meta_file = open(trip_meta, 'a+')
    trip_id = extract_trip_from_one_file.count

    for line in r:
        if "{occupied}".format(**line) == '1':
            day_of_week = int(time.strftime("%w", time.strptime("{timestamp}".format(**line), "%Y-%m-%d %H:%M:%S")))
            hour_of_day = int(time.strftime("%H", time.strptime("{timestamp}".format(**line), "%Y-%m-%d %H:%M:%S")))
            minute = int(time.strftime("%M", time.strptime("{timestamp}".format(**line), "%Y-%m-%d %H:%M:%S")))
            sec = int(time.strftime("%S", time.strptime("{timestamp}".format(**line), "%Y-%m-%d %H:%M:%S")))
            sec_of_day = hour_of_day * 3600 + minute * 60 + sec
            trip.append(("{taxi_id}".format(**line), float("{lng}".format(**line)), float("{lat}".format(**line)), day_of_week, hour_of_day, sec_of_day))
            lat.append(float("{lat}".format(**line)))
            lng.append(float("{lng}".format(**line)))
            timestamp.append(sec_of_day)
            if len(lat) > 1:
                travelDistance += geo.distBetween(lat[-1], lng[-1], lat[-2], lng[-2])
        else: 
            if trip: 
                if timestamp[-1] >= timestamp[0]:
                    travelTime = timestamp[-1] - timestamp[0]
                else: # a trip crossed a day
                    travelTime = timestamp[-1] - timestamp[0] + 60 * 60 * 24
                if travelTime > 0 and travelDistance > 0: #filter trips with zero travel time/distance
                    trips.append((trip, lat, lng, timestamp, travelDistance, travelTime))
                    #generate a trip file
                    trip_file = open(trip_dir + str(trip_id) + '.txt', 'w')
                    for line in trip:
                        print >> trip_file, ','.join([str(field) for field in line])
                    trip_file.close()
                    #update trip meta
                    trip_meta_file.write(','.join([str(trip_id), str(trip[0][0]), str(lat[0]), str(lng[0]), str(timestamp[0]), str(lat[-1]), str(lng[-1]), str(timestamp[-1]), str(travelTime), str(travelDistance)])+'\n')
                    trip_id += 1
                    
                max_lat = max(max(lat), max_lat)
                min_lat = min(min(lat), min_lat)
                max_lng = max(max(lng), max_lng)
                min_lng = min(min(lng), min_lng)
                lat = []
                lng = []
                timestamp = []
                trip = []
                travelDistance = 0.0
    trip_meta_file.close()
    extract_trip_from_one_file.count = trip_id
    return trips, max_lat, min_lat, max_lng, min_lng

def generate_trip_meta(all_trip_meta_file_name, trip_meta_file_name, non_valid_trip_file_name, trip_dir):
    """Given the all_trip_meta_file, generate the trip meta file by using the filter algorithm"""
    start=time.time()
    
    trip_meta_file=open(trip_meta_file_name, 'w+')
    non_valid_trip_file=open(non_valid_trip_file_name, 'w+')
    
    with open(all_trip_meta_file_name) as all_trip_meta_file:
        for line in all_trip_meta_file:
            trip_id=line.split(',')[0]
            trip_file_name=trip_dir+'/'+trip_id+'.txt'
            if is_valid_trip(trip_file_name):
                trip_meta_file.write(line)
            else:
                non_valid_trip_file.write(trip_id+'\n')
    trip_meta_file.close()
    non_valid_trip_file.close()
    
    elapsed = int((time.time() - start)/60)
    print "%d minutes elapsed\n"%elapsed 


def build_file_names(dir_name):
    raw = Constants.RAW_DIR + dir_name
    trip_dir = Constants.PROCESSED_DIR + dir_name + '/trip_trajectory/'
    if not os.path.exists(trip_dir):
        os.makedirs(trip_dir)
    
    names = ['all_trip_meta','trip_meta','non_valid_trip']
    files = []
    for name in names:
        files.append(Constants.PROCESSED_DIR + dir_name + '/' + name + '.txt')
    return trip_dir, files

def processRawData(dir_name, trip_dir, all_trip_meta_file_name):
    """load raw data, analyze trips and write them to processed data"""
    start=time.time()

    trips = []
    _max_lat = 0.0
    _min_lat = 180
    _max_lng = 0.0
    _min_lng = 180

    extract_trip_from_one_file.count = 1
    
    for f in glob.glob(Constants.RAW_DIR +dir_name+ '/*'):
        ts, max_lat, min_lat, max_lng, min_lng = extract_trip_from_one_file(f, trip_dir, all_trip_meta_file_name)
        _max_lat = max(max_lat, _max_lat)
        _min_lat = min(min_lat, _min_lat)
        _max_lng = max(max_lng, _max_lng)
        _min_lng = min(min_lng, _min_lng)
        trips.extend(ts)  
    
    elapsed = int((time.time() - start)/60)
    print "%d minutes elapsed\n"%elapsed 
    return trips, _max_lat, _min_lat, _max_lng, _min_lng


dir_name="Taxi_Shanghai"
trip_dir, files=build_file_names(dir_name)

#generate the all_trip_meta_file
#processRawData(dir_name,trip_dir,files[0])

#generate trip_meta_file, i.e. filtering out invalid trips
generate_trip_meta(files[0], files[1], files[2], trip_dir)
#is_valid_trip("C:/Program Files/Weka-3-6/data/Taxi_Trajectory/processed/Taxi_Shanghai/trip_trajectory/499.txt", True)

'''
def readFromSynthesizedData(dir_name):
    """create N trips (length range from (2km,8km)) with 3N pair OD-Merged trips"""
    N = 1000
    trip_meta = ['none']
    for _ in range(1, N + 1):
        trip_meta.append({'td':random.randint(2000, 8000)})

    names = ['trip_meta', 'od_merge_trips']
    files = []
    for name in names:
        files.append(Constants.PROCESSED_DIR + dir_name + '/' + name + '.txt')
    
    my_file = open(files[1], 'w+')
    lines = []
    for _ in range(1, 3 * N + 1):
        child = random.randint(1, N)
        while True:
            father = random.randint(1, N)
            if father != child:
                break
        line = str(child) + ',' + str(father) + '\n'
        if line not in lines:
            my_file.write(line)
            lines.append(line)
    my_file.close()
'''
   