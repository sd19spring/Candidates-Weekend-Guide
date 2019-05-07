'''
This module contains the User class.
'''

class User():
    '''
    Defines a user of the app.
    '''
    def __init__(self, username, email, group_letter,
                 interview_time, interview_location,
                 dinner_group, group_interview_location, cw_number,
                 name, model_class, model_class_location, interviewers):
        '''
        Creates a user.

        Attributes:
        username - the user's name/user id
        email - user's email address
        group_letter - the letter for the user's interview group
        interview_time - the user's individual interview time
        interview_location - the location of the user's individual interview
        dinner_group - the number of the user's dinner group
        group_interview_location - the location of the user's group interview
        cw_number - the user's candidates' weekend number, represented
                    as a string
        name - the user's fullname
        model_class - the model class the user will be attending
        model_class_location - the location of the model class (represented
                               as a string)
        interviewers - the names of the interviewers for this user, represented
                       as a string
        '''
        self.username = username
        self.email = email
        self.group_letter = group_letter
        self.interview_time = interview_time
        self.interview_location = interview_location
        self.dinner_group = dinner_group
        self.group_interview_location = group_interview_location
        self.cw_number = cw_number
        self.name = name
        self.model_class = model_class
        self.model_class_location = model_class_location
        self.interviewers = interviewers

    def to_dict(self):
        '''
        Stores user information in a diciontary.
        '''
        user_dict = {
            'email': self.email,
            'group_letter': self.group_letter,
            'interview_time': self.interview_time,
            'interview_location': self.interview_location,
            'dinner_group': self.dinner_group,
            'group_interview_location': self.group_interview_location,
            'cw_number': self.cw_number,
            'name': self.name,
            'model_class': self.model_class,
            'model_class_location': self.model_class_location,
            'interviewers': self.interviewers
        }

        return user_dict
