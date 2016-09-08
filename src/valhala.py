#six degrees of precision in valhalla
inv = 1.0 / 1e6;

def getShape(leg):
    decoded = []
    previous = [0,0]
    i = 0
    #for each byte
    while i < len(leg['shape']):
        #for each coord (lat, lon)
        ll = [0,0]
        for j in [0, 1]:
            shift = 0
            byte = 0x20
            #keep decoding bytes until you have this coord
            while byte >= 0x20:
                byte = ord(leg['shape'][i]) - 63
                i += 1
                ll[j] |= (byte & 0x1f) << shift
                shift += 5
            #get the final value adding the previous offset and remember it for the next
            ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
            previous[j] = ll[j]
        #scale by the precision and chop off long coords also flip the positions so
        #its the far more standard lon,lat instead of lat,lon
        decoded.append([float('%.6f' % (ll[1] * inv)), float('%.6f' % (ll[0] * inv))])
    #hand back the list of coordinates
    return decoded

def getStops(leg):
    shape = getShape(leg)
    stops = []

    for step in leg['maneuvers']:
        stops.append(shape[step['begin_shape_index']])

    return stops

def getInstructions(leg):
    instructions = []

    for step in leg['maneuvers']:
        instructions.append(step['verbal_pre_transition_instruction'])

    return instructions
