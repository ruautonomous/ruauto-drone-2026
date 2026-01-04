

def read_config_file(file = 'info_files/config.txt'):
    config = {}
    with open(file) as f:
        while True:
            read = f.readline()
            if(read == ''):
                break
            if(read.__contains__('#')):
                continue
            read = read.removesuffix('\n').split('=')
            config[read[0]] = read[1]
        return config
    
def read_waypoints(file = 'info_files/waypoints.txt'):
    waypoints = []
    with open(file) as f:
        while True:
            read = f.readline()
            if(read == ''):
                break
            if(read.__contains__('#')):
                continue
            read = read.removesuffix('\n').split(',')
            waypoints.append([float(read[0]), float(read[1])])

    return waypoints

def read_geofence(file = 'info_files/fence.txt'):
    geofence = []
    with open(file) as f:
        while True:
            read = f.readline()
            if(read == ''):
                break
            if(read.__contains__('#')):
                continue
            read = read.removesuffix('\n').split(',')
            geofence.append([float(read[0]),float(read[1])])

    return geofence
