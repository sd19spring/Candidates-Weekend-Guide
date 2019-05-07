'''
This module contains all functions and classes related to events.

This includes:
    Functions involved in creating/updating events:
        - allowed_file - a function that checks to see if an uploaded file is
          a valid file type (used to validate files associated with events)
        - the Event class - the object representation of an event
        - get_links_dict - a function that takes in a string of text defining links
          and converts them into a dictionary, so that they can be stored in the
          database
    Functions involved in displaying events:
        - get_raw_name - a function that gets the raw name of an event (without
          the Candidates' Weekend number)
        - get_display_name - a function that gets the display name of an event
          (without any additions at all)
        - split_description_lines - a function that takes a string with the
          description for text and converts it into a list, so that line breaks
          can be preserved
'''
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    '''
    Checks to see if filename is an accepted type.
    filename: filename

    >>> allowed_file('cat.jpg')
    True
    >>> allowed_file('cat.abc')
    False

    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Event():
    '''
    Events that occur during Candidates' Weekend.
    '''
    def __init__(self, name, start_time, end_time, day, location,
                 description, cw_number, access, img_files=None,
                 links_dict=None):
        '''
        Creates an event.

        Attributes:
        name: name of the event
        start_time: starting time
        end_time: ending time
        day: which day the event will take place on (friday or saturday)
        location: place where event occurs
        description: string describing the event
                    /more information about the event
        img_files: any related files (must be PDFs)
        cw_number: string denoting which candidates' weekend the
                   schedule is displaying
        access: string denoting who can attend the event (candidates only,
                guests only, or all)
        links: the dictionary of links, with the key being the link itself
               and the value being the text to e displayed for each link
        '''
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.day = day
        self.location = location
        self.description = description
        self.img_files = img_files
        self.cw_number = cw_number
        self.links = links_dict
        self.access = access

    def to_dict(self):
        '''
        Stores object data in a dictionary so
        that it can be stored in database.
        '''
        event_dict = {
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'day': self.day,
            'location': self.location,
            'description': self.description,
            'img_files': self.img_files,
            'cw_number': self.cw_number,
            'links': self.links,
            'access': self.access
        }

        return event_dict

def get_links_dict(links_text):
    '''
    Processes the user-input links text to a dictionary of links,
    where the key is the link itself and the value is the text to be displayed
    for that link.
    '''
    links_dict = dict()
    links = links_text.split("\n")
    for link in links:
        link_parts = link.split(",")
        if len(link_parts) > 2:
            links_dict[link_parts[0]] = link_parts[1].strip()

    return links_dict

def get_raw_name(name):
    '''
    Gets raw event name, without copy or dashes or the CW number.
    Preserves 'copy', for document ID purposes.
    '''
    if name.find("-") > 0:
        dash_index = name.rfind('-')
        return name[0:dash_index]
    return name

def get_display_name(name):
    '''
    Gets name to be displayed, without dashes of any sort.
    Removes 'copy' out of the event name.
    '''
    index = name.find('-')
    return name[0:index]

def split_description_lines(raw_description):
    '''
    Splits a string of text that is the raw description of an event into
    lines so that the description can be displayed on a page with line
    breaks.
    '''
    description_lines = raw_description.split("\n")
    for i in range(0, len(description_lines)):
        line = description_lines[i].strip("\r").strip()
        description_lines[i] = line

    return description_lines
