def to_min(time):
    '''
    converts time to units of minutes.

    time: string in hh:mm:ss format
    '''
    time_list = time.split(':')
    time_list = [int(t) for t in time_list]
    return time_list[0]*60 + time_list[1]

def to_hours(minutes):
    '''
    Reverses the to_min function and applies it to the original object.

    minutes: integer

    '''
    h = str(minutes//60)
    time_marker = "AM"
    if int(h) > 12:
        hour = int(h)
        hour -= 12
        h = str(hour)
        time_marker = "PM"
    if int(h) == 12:
        time_marker = "PM"
    m = str(minutes%60)
    if int(m) < 10:
        m += '0' #compensates for missing '0'
    return h + ':' + m + " " + time_marker

def convert_conventional(time_string):
    '''
    Converts time string appearance
    time_string: string

    returns time string
    '''
    time_mins = to_min(time_string)
    time = to_hours(time_mins)
    return time

def sort_events(event_list):
    '''
    Sorts events chronologically based on the start time.
    event_list: list of event objects

    returns list of events
    '''

    time_list = []
    for event in event_list:
        #convert time to minutes to make sorting easier
        event['start_time'] = to_min(event['start_time'])
        event['end_time'] = to_min(event['end_time'])
    event_list = sorted(event_list, key = lambda i: (i['day'], i['start_time'], i['name']))

    for event in event_list:
        #add events in chronolgical order
        event['start_time'] = to_hours(event['start_time'])
        event['end_time'] = to_hours(event['end_time'])
    return event_list

if __name__ == '__main__':
    #Test with sample data
    event_list = [{'description': 'Check-In before grabbing some snacks before our Welcome', 'pdfs': [], 'name': 'Check-In', 'cw_number': 1, 'end_time': '15:30', 'start_time': '14:00', 'location': 'Milas Hall Lobby', 'day': 'Saturday', 'image': 'None'}, {'description': 'fun', 'name': 'Design Challenge', 'pdfs': [], 'cw_number': 2, 'end_time': '13:00', 'start_time': '12:00', 'location': 'Academic Center', 'day': 'Saturday', 'image': 'None'}, {'end_time': '21:00', 'start_time': '19:00', 'location': 'Norden Auditorium', 'day': 'Saturday', 'image': 'None', 'description': 'lights camera action', 'pdfs': [], 'name': 'FWOP Play', 'cw_number': 3}]

    sort_events(event_list)
    print(event_list)
