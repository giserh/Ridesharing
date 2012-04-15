'''
Created on Feb 20, 2012

@author: Sol
'''
import time, glob, csv, os, random
import util.Geo as geo


BASE_DIR = 'C:/Program Files/Weka-3-6/data/Taxi_Trajectory/'
RAW_DIR = BASE_DIR + 'raw/'
PROCESSED_DIR = BASE_DIR + 'processed/'

def set_directory(base_dir):
    global BASE_DIR, RAW_DIR, PROCESSED_DIR
    BASE_DIR=base_dir
    RAW_DIR = BASE_DIR + 'raw/'
    PROCESSED_DIR = BASE_DIR + 'processed/'

def readTaxiFile(file_name, trip_dir, trip_meta):
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
    trip_id = readTaxiFile.count
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
                    trip_meta_file.write(','.join([str(trip_id), str(trip[0][0]), str(lat[0]), str(lng[0]), str(timestamp[0]), str(lat[-1]), str(lng[-1]), str(timestamp[-1]), str(travelTime), str(travelDistance)]))
                    trip_meta_file.write('\n')
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
    readTaxiFile.count = trip_id
    return trips, max_lat, min_lat, max_lng, min_lng

def processRawData(dir_name):
    '''load raw data, analyze trips and write them to processed data'''
    raw = RAW_DIR + dir_name
    trip_dir = PROCESSED_DIR + dir_name + '/trip_trajectory/'
    if not os.path.exists(trip_dir):
        os.makedirs(trip_dir)
    
    names = ['trip_meta', 'od_merge_trips']
    files = []
    for name in names:
        files.append(PROCESSED_DIR + dir_name + '/' + name + '.txt')
        my_file = open(files[-1], 'w+')
        my_file.close()    

    trips = []
    _max_lat = 0.0
    _min_lat = 180
    _max_lng = 0.0
    _min_lng = 180

    readTaxiFile.count = 1
    for f in glob.glob(raw + '/*'):
        ts, max_lat, min_lat, max_lng, min_lng = readTaxiFile(f, trip_dir, files[0])
        _max_lat = max(max_lat, _max_lat)
        _min_lat = min(min_lat, _min_lat)
        _max_lng = max(max_lng, _max_lng)
        _min_lng = min(min_lng, _min_lng)
        trips.extend(ts)
        
    #trip_meta = loadTripMetaFile(files[0])
    #updateODMergeTrips(trip_meta, files[1])
    return trips, _max_lat, _min_lat, _max_lng, _min_lng

def readFromSynthesizedData(dir_name):
    '''create N trips (length range from (2km,8km)) with 3N pair OD-Merged trips '''
    N = 1000
    trip_meta = ['none']
    for _ in range(1, N + 1):
        trip_meta.append({'td':random.randint(2000, 8000)})

    names = ['trip_meta', 'od_merge_trips']
    files = []
    for name in names:
        files.append(PROCESSED_DIR + dir_name + '/' + name + '.txt')
    
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
    
    #father_trips, child_trips = loadODMergeTrips(files[1], trip_meta)
    #runHeuristics(father_trips, child_trips)


