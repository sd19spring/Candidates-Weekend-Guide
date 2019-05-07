'''
This program controls the main Flask routing for the web app and hosts several
other supporting functions. It is separated into a few main sections:

    1. General database functions, like retrieving all users, all events, or just
    a subset of the events.

    2. General image retrieval functions, which interact with Firebase Storage.
    This includes retrieving uploaded images associated with an event, and getting
    major images like the header images.

    3. Admin routing for the Flask web-app, and all related functions
    (like editing/adding events and users and changing the candidates'
    weekend number).

    4. Client routing for the Flask web-app, and all related functions (like
    retrieving candidate information and displaying the Candidates' Weekend
    schedule).
'''

import os
from flask import Flask, render_template, redirect, url_for, request
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sortbytime import sort_events, convert_conventional
from users import *
from events import *

app = Flask(__name__)

OLIN_LOGO = "oval.png"
OLIN_HEADER = "olinheader.jpg"

EVENTS_COLLECTION = 'events'
GENERAL_INFO_EVENT = "General Event Info"
CW_NUMBER = 'cw_number'
ALL_WEEKENDS = "All"
NAME = 'name'
LINKS = 'links'
FILES = 'files'
START_TIME = 'start_time'
END_TIME = 'end_time'
DAY = 'day'
LOCATION = 'location'
DESCRIPTION = 'description'
ACCESS = 'access'
SELECTED_EVENT = 'event'
DELETE_EVENT = 'Delete Event'
DUPLICATE_EVENT = 'Duplicate Event'
COPY = '-copy'
SUBMIT = 'Submit'
CHECKED_FILES = 'check'
FRIDAY = 'Friday'
SATURDAY = 'Saturday'
IMG_FILES = 'img_files'

USERS_COLLECTION = 'users'
ADMISSIONS_USERNAME = 'olinadmissions'
ADMISSIONS_PASSWORD = 'cwadmin'
USERNAME = 'username'
PASSWORD = 'password'
SELECTED_USER = 'users'
DELETE_USER = "Delete User"
EMAIL = 'email'
GROUP_LETTER = 'group_letter'
INTERVIEW_TIME = 'interview_time'
INTERVIEW_LOCATION = 'interview_location'
DINNER_GROUP = 'dinner_group'
GROUP_INTERVIEW_LOCATION = 'group_interview_location'
NAME = 'name'
MODEL_CLASS = 'model_class'
MODEL_CLASS_LOCATION = 'model_class_location'
INTERVIEWERS = 'interviewers'
VERIFY_PASSWORD = 'password2'

# ------- GENERAL DATABASE FUNCTIONS ---------
def get_users():
    '''
    Gets list of users from the database, and
    all the corresponding information associated
    with each user.

    Returns:
    user_names - list of names of users (user ids/document ids)
    user_infos - list of dictionaries, where each dictionary
                 contains more information about the corresponding user
    '''
    user_names = []
    user_infos = []

    # Get reference to all users
    users_ref = DB.collection(USERS_COLLECTION).get()

    # Get each user's name/id and information
    for user in users_ref:
        user_names.append(user.id)
        user_infos.append(user.to_dict())

    return user_names, user_infos

def valid_admin_login(username, password):
    '''
    Checks for valid admin login.

    Returns true if the correct admin username and password are entered,
    and false otherwise.
    '''

    return username == ADMISSIONS_USERNAME and password == ADMISSIONS_PASSWORD

def get_curr_cw():
    '''
    Gets the current Candidates' Weekend number from the database.

    Returns: the current weekend number as a string
    '''
    return DB.collection(EVENTS_COLLECTION).document(
        GENERAL_INFO_EVENT).get().to_dict()[CW_NUMBER]

def get_all_events():
    '''
    Retrieves all events from the database for all Candidates' Weekends

    Returns:
    - event_names - a list of all the events' names, represented as strings
    - event_infos - a corresponding list of event information, represented
    as dictionaries
    '''

    # Access the events collection
    events_ref = DB.collection(EVENTS_COLLECTION).get()

    # Gets names of all events and dictionaries of information for all events
    event_names = []
    event_infos = []
    for event in events_ref:
        # Makes sure to avoid the event document that
        # contains general information, like the candidates' weekend number
        if event.id != GENERAL_INFO_EVENT:
            event_names.append(event.id)
            event_infos.append(event.to_dict())

    return event_names, event_infos

def get_events(user_id=None):
    '''
    Retrieves the events from the database to be displayed in the schedule.
    If there is a user id supplied, then this function retrieves the events
    for the user's Candidates' Weekend. Otherwise, it retrieves the events
    for the current Candidates' Weekend.

    Returns:
    - event_names: a list of the event names
    - event_infos: a parallel list of event information dictionaries
    '''

    # Gets reference to the collection of events
    events_ref = DB.collection(EVENTS_COLLECTION).get()

    # Gets the current Candidates' Weekend Number
    curr_cw_number = get_curr_cw()

    # If a user id is supplied, retrieves the user's
    # Candidates' Weekend number, or sets the user's Candidats'
    # Weekend number to None
    if user_id is not None:
        user_cw_number = DB.collection(USERS_COLLECTION).document(
            user_id).get().to_dict()[CW_NUMBER]
    else:
        user_cw_number = None

    # Gets all events and adds each event's document ID to one list
    # and the event info dictionary to one list
    event_names = []
    event_infos = []

    for event in events_ref:
        # Makes sure the event is not the document intended to store the
        # general information, like the current Candidates' Weekend number
        if event.id != GENERAL_INFO_EVENT:
            # Gets the event's Candidates' Weekend number
            event_cw_number = event.to_dict()[CW_NUMBER]

            # If there is a user id supplied, then adds all events that
            # are in that user's Candidates' Weekend (or present in all
            # Candidates' Weekends)
            if user_cw_number is None:
                if event_cw_number in (curr_cw_number, ALL_WEEKENDS):
                    event_names.append(event.id)
                    event_infos.append(event.to_dict())
            # Otherwise, only gets events in the
            # current Candidates Weekend
            else:
                if event_cw_number in (user_cw_number, ALL_WEEKENDS):
                    event_names.append(event.id)
                    event_infos.append(event.to_dict())

    return event_names, event_infos

def separate_and_sort_events(event_names, event_infos):
    '''
    Separates events based on day and sorts events based on time.
    '''
    friday_events = []
    saturday_events = []

    for i in range(0, len(event_names)):
        # Adds display name to event info dictionaries, to make rendering easier
        event_infos[i][NAME] = get_display_name(event_names[i])

        # Separates events into separate days
        if event_infos[i][DAY] == FRIDAY:
            friday_events.append(event_infos[i])
        elif event_infos[i][DAY] == SATURDAY:
            saturday_events.append(event_infos[i])

    # Sorts events
    friday_events = sort_events(friday_events)
    saturday_events = sort_events(saturday_events)

    return friday_events, saturday_events

# ------- IMAGE RETRIEVAL FUNCTIONS -------
def get_media_link(img_filename):
    '''
    Gets the link for an image stored in Firebase Storage
    so that it can be displayed.

    Params: img_filename - the name of the file as a string,
    file extension included.
    Returns: image_url - the URL of the image so that it can be displayed
    '''
    # Gets blob from Firebase Storage so that image can be accessed
    image_blob = BUCKET.get_blob(img_filename)

    # Retrieves the media link for the image so that it can be displayed
    image_blob.make_public()

    return image_blob.media_link

def get_logo():
    '''
    Gets the link for the Olin logo to be displayed in the tab header.

    Returns: the URL for the logo so that the logo can be displayed
    '''
    return get_media_link(OLIN_LOGO)

def get_header():
    '''
    Gets the link for the Olin header to be displayed in the header of
    each page.

    Returns: the URL for the header so that the header can be displayed
    '''
    return get_media_link(OLIN_HEADER)

def get_uploaded_images(images):

    '''
    Retrieves the uploaded images for a specific event.

    Inputs:
    images - an array of files downloaded from
    the database (references to the uploaded files)

    Returns:
    uploaded_images - either an empty list if there
    are no files associated with the event, or the
    list of the URLs for files associated with each event
    '''
    uploaded_images = []

    # Checks if there were any uploaded images
    for image in images:

        # Adds link to file to the list of uploaded images
        uploaded_images.append(get_image(image))

    return uploaded_images

def get_image(image):
    '''
    Retrieves the link for an image associated with the event,
        if there is an image.

    Returns "None" if there is no image associated with the event,
        or returns the image filename.
    '''

    # Check if there is an image associated with the event
    if image:
        # Checks to make sure the image is a valid image
        if image.filename != "" and allowed_file(image.filename):
            # Saves the image to the uploads folder
            image_filepath = os.path.join(app.config['UPLOAD_FOLDER'],
                                          image.filename)
            image.save(image_filepath)

            # Saves image to Firebase Storage
            img_filename = secure_filename(image.filename)
            blob = BUCKET.blob(img_filename)
            blob.upload_from_filename(image_filepath)

            # Deletes image from local directory after it was uploaded
            os.remove(image_filepath)

            return get_media_link(img_filename)

    return None

# ------ ADMIN ROUTING --------
@app.route('/login/admin', methods=['POST', 'GET'])
def admin_login():
    '''
    Allows admin to log in so that they can edit the website.
    '''
    # Retrieve information from submitted form
    if request.method == 'POST':
        # Checks admin credentials; if valid credentials, directs user to
        # admin manager page
        if valid_admin_login(request.form[USERNAME], request.form[PASSWORD]):
            return redirect(url_for('admin_manager'))

        # Redirects user to error page if invalid credentials
        return redirect(url_for('admin_login_error'))

    # Shows the admin login page
    return show_admin_login()

@app.route('/admin/manager')
def admin_manager():
    '''
    Displays admin manager page, where admins
    can edit/add users or edit/add events.
    '''
    return show_admin_manager()

@app.route('/login/error/admin')
def admin_login_error():
    '''
    Displays admin login error page.
    '''
    return show_admin_login_error()

@app.route('/admin/update-cw', methods=['POST', 'GET'])
def change_gen_info():
    '''
    Allows admin to change general information, like the current Candidates'
    Weekend number.
    '''
    if request.method == 'POST':

        # Updates current candidates' weekend number in the database
        DB.collection(EVENTS_COLLECTION).document(GENERAL_INFO_EVENT).set({
            "cw_number": request.form[CW_NUMBER]})

        # Redirects user to the admin manager page
        return redirect(url_for('admin_manager'))

    # Show page to allow admin to change general information
    return show_gen_info()

@app.route('/admin/add-event', methods=['POST', 'GET'])
def create_event():
    '''
    Adds event to the database.
    '''
    # Retrieves information from form to create an event
    if request.method == 'POST':

        # Creates Event object for this event and adds it to the database
        event = Event(request.form[NAME] + "-" + request.form[CW_NUMBER],
                      request.form[START_TIME], request.form[END_TIME],
                      request.form[DAY], request.form[LOCATION],
                      request.form[DESCRIPTION], request.form[CW_NUMBER],
                      request.form[ACCESS],
                      get_uploaded_images(request.files.getlist(FILES)),
                      get_links_dict(request.form[LINKS]))

        DB.collection(EVENTS_COLLECTION).document(event.name).set(event.to_dict())

        # Redirect to admin manager page
        return redirect(url_for('admin_manager'))

    # Show page with form to add event
    return show_add_event()

@app.route('/admin/select-event', methods=['POST', 'GET'])
def view_events():
    '''
    Shows page with list of events so that admin can select the event to edit.
    '''
    # Retrieves selected event
    if request.method == "POST":

        # Redirects to page to edit event for the selected event
        return redirect(url_for("edit_event", event_name=request.form[SELECTED_EVENT]))

    return show_events()

@app.route('/admin/edit-event/<event_name>', methods=['POST', 'GET'])
def edit_event(event_name=None):
    '''
    Edits an event and syncs changes to the event in the database.
    '''
    # Retrieves updated event information and updates database.
    if request.method == "POST":

        # Deletes event
        if request.form['button'] == DELETE_EVENT:

            # Deletes document
            DB.collection(EVENTS_COLLECTION).document(event_name + "-" +
                                                      request.form[
                                                          CW_NUMBER]).delete()

            # Redirects user to the admin manager page
            return redirect(url_for('admin_manager'))

        # Duplicates event

        elif request.form['button'] == DUPLICATE_EVENT:

            # Gets the event's information
            full_name = event_name + "-" + request.form[CW_NUMBER]
            event_info = DB.collection(EVENTS_COLLECTION).document(
                full_name).get().to_dict()

            # Creates new document with the same information, with the name
            # as the event's name + "copy"
            DB.collection(EVENTS_COLLECTION).document(full_name).set(event_info)

            # Redirects user to the admin manager page
            return redirect(url_for('admin_manager'))

        # Updates event information
        elif request.form['button'] == SUBMIT:

            # Gets full name for the event, with the Candidates' Weekend
            # number included
            name = request.form[NAME] + "-" + request.form[CW_NUMBER]

            # Gets links to all files for this event, including the
            # selected files from the already uploaded files
            # and newly uploaded files
            img_files = get_uploaded_images(request.files.getlist(
                FILES)) + request.files.getlist(CHECKED_FILES)

            # Gets links from the form and composes a dictionary with the links
            links = get_links_dict(request.form[LINKS])

            # Updates the document in the collection of events with
            # the new information
            updated_event = Event(name, request.form[START_TIME],
                                  request.form[END_TIME], request.form[DAY],
                                  request.form[LOCATION],
                                  request.form[DESCRIPTION],
                                  request.form[CW_NUMBER],
                                  request.form[ACCESS],
                                  img_files, links)
            DB.collection(EVENTS_COLLECTION).document(name).set(updated_event.to_dict())

            return redirect(url_for('admin_manager'))

    return show_edit_event(event_name)

@app.route('/admin/add-users', methods=['POST', 'GET'])
def add_users():
    '''
    Allows admin to create users by uploading an Excel file.
    '''
    # Add users from uploaded file
    if request.method == 'POST':
        # Retrieve uploaded Excel file
        file = request.files['file']
        file_df = pd.read_excel(file)

        users_ref = DB.collection(USERS_COLLECTION)
        for index, row in file_df.iterrows():
            # Create user in Firebase Authentication
            user = auth.create_user(uid=row['User ID'],
                                    email=row['Email Address'],
                                    display_name=row['Name'])

            # Add user to the database + user information
            users_ref.document(user.uid).set({"email": user.email,
                                              "dinner_group": row[
                                                  'Dinner Group'],
                                              "group_letter": row[
                                                  'Group Letter'],
                                              "interview_location": row[
                                                  'Interview Location'],
                                              "interview_time": row[
                                                  'Individual Interview Time'],
                                              "group_interview_location": row[
                                                  'Group Interview Location'],
                                              "password": "",
                                              "cw_number": row[
                                                  "Candidates' Weekend Number"],
                                              'name': row['Name'],
                                              'model_class': row['Model Class'],
                                              'model_class_location': row[
                                                  'Model Class Location'],
                                              'interviewers': row[
                                                  'Interviewers']})

        # Redirects to admin manager page
        return redirect(url_for('admin_manager'))

    return show_add_users()

@app.route('/admin/select-user', methods=['POST', 'GET'])
def view_users():
    '''
    Shows page where admin can select a user to edit
    '''
    # Retrieves the selected user
    if request.method == 'POST':

        # Gets the selected user from the form
        user = request.form[SELECTED_USER]

        # Redirects to a page to edit this user's information
        return redirect(url_for("edit_user", user_name=user))

    return show_users()

@app.route('/admin/edit-user/<user_name>', methods=['POST', 'GET'])
def edit_user(user_name=None):
    '''
    Allows admin to make edit a user's information and update the database.
    '''
    # Retrieves the updated information from
    # the edit user form and updates the database
    if request.method == 'POST':

        # User deleted
        if request.form['button'] == DELETE_USER:
            DB.collection(USERS_COLLECTION).document(user_name).delete()
            return redirect(url_for('admin_manager'))
        # User changed
        elif request.form['button'] == SUBMIT:
            user_ref = DB.collection(USERS_COLLECTION).document(user_name)

            # Gets new information for user
            # Updates email address in authentication and database
            auth.update_user(user_name, email=request.form[EMAIL])

            # Creates updated user object to use to update the database
            updated_user = User(user_name, request.form[EMAIL],
                                request.form[GROUP_LETTER],
                                request.form[INTERVIEW_TIME],
                                request.form[INTERVIEW_LOCATION],
                                request.form[DINNER_GROUP],
                                request.form[GROUP_INTERVIEW_LOCATION],
                                request.form[CW_NUMBER], request.form[NAME],
                                request.form[MODEL_CLASS],
                                request.form[MODEL_CLASS_LOCATION],
                                request.form[INTERVIEWERS])

            user_ref.set(updated_user.to_dict(), merge=True)

            # Redirects to the admin manager page
            return redirect(url_for('admin_manager'))

    # Shows the edit user form with the current information
    # filled in so that the user can be updated
    return show_edit_user(user_name)

@app.route('/welcome/admin')
def admin_welcome():
    '''
    Shows the welcome page for the admin
    (with all the navigation tabs for the admin).
    '''
    return show_admin_welcome()

@app.route('/schedule/admin')
def admin_schedule():
    '''
    Shows the schedule for the current Candidates' Weekend for the admin.
    '''
    # Gets all event names and information for the events for the current
    # Candidates' Weekend
    event_names, event_infos = get_events()

    # Separates and sorts events based on day and time
    friday_events, saturday_events = separate_and_sort_events(event_names, event_infos)

    return show_admin_schedule(friday_events, saturday_events)

@app.route('/event-info/<name>/admin')
def admin_event_info(name):
    '''
    Shows the specific information for a selected event.
    '''
    # Gets information for the event, represented as a dictionary
    event = DB.collection(EVENTS_COLLECTION).document(name).get().to_dict()

    # Show page with more event information
    return show_admin_event_info(name, event)

# ---- ADMIN RENDERING OF PAGES -----
def show_admin_login():
    '''
    Displays the admin login page.
    '''
    return render_template('adminlogin.html', img_url=get_header(),
                           img_url1=get_logo())

def show_admin_manager():
    '''
    Shows the admin manager page.
    '''
    return render_template('admin_manager.html', img_url=get_header(),
                           img_url1=get_logo())

def show_admin_login_error():
    '''
    Shows admin login error page.
    '''
    return render_template('adminloginerror.html',
                           img_url=get_header(),
                           img_url1=get_logo())

def show_gen_info():
    '''
    Displays page that admin can use to change the Candidates' Weekend number.
    '''
    return render_template('change_gen_info.html', img_url1=get_logo(),
                           img_url=get_header(),
                           current_cw_number=get_curr_cw())

def show_add_event():
    '''
    Shows the add event form.
    '''
    return render_template('add_event.html', img_url=get_header(),
                           img_url1=get_logo())

def show_events():
    '''
    Retrieves all events and renders page with list of events for all
    Candidates' Weekends (so admin can select an event to edit.)
    '''
    # Shows page with list of events for all Candidates' Weekends
    event_names = get_all_events()
    return render_template('view_events.html', img_url=get_header(),
                           events_list=event_names,
                           img_url1=get_logo())

def show_edit_event(event_name):
    '''
    Gets the current information for an event and populates the edit event
    form with this information, and displays the edit event form.
    '''

    # Retrieves current information for an event and fills form
    event_ref = DB.collection(EVENTS_COLLECTION).document(event_name).get()

    # Gets event information as a dictionary
    event_dict = event_ref.to_dict()

    # Recomposes the links as a string of text that can be displayed
    links_text = ""
    links_dict = event_dict[LINKS]
    for key in links_dict.keys():
        links_text += key + ", " + links_dict[key] + "\n"

    event_dict['links_text'] = links_text

    # Shows edit event form with current information filled in
    return render_template("edit_event.html",
                           old_name=get_raw_name(event_ref.id),
                           event=event_dict,
                           img_url=get_header(),
                           img_url1=get_logo())

def show_add_users():
    ''' Shows add user form. '''

    # Shows upload page
    return render_template('add_users.html', img_url=get_header(),
                           img_url1=get_logo())

def show_users():
    '''
    Retrieves list of users from the database and renders page so that
    admin can select a user to edit/delete.
    '''

    # Shows page with list of users to allow admin to select a user
    user_names = get_users()
    return render_template('view_users.html',
                           img_url=get_header(),
                           users_list=user_names,
                           img_url1=get_logo())

def show_edit_user(user_name):
    '''
    Populates the edit user form with the user's current information and
    shows the edit user form to the admin.
    '''
    # Get current user information
    user_ref = DB.collection(USERS_COLLECTION).document(user_name).get()

    # Show edit user form with current information filled in
    return render_template('edit_user.html',
                           img_url=get_header(),
                           old_username=user_ref.id,
                           user_info=user_ref.to_dict(),
                           img_url1=get_logo())

def show_admin_welcome():
    '''
    Shows the admin welcome page.
    '''

    return render_template('adminwelcome.html', img_url=get_header(),
                           img_url1=get_media_link('campusmap.jpg'),
                           img_url2=get_logo(),
                           img_url3=get_media_link('welcomepage.jpg'))

def show_admin_schedule(friday_events, saturday_events):
    '''
    Shows the admin schedule for Friday and Saturday.
    '''

    # Displays schedule
    return render_template('adminschedule.html', friday_events=friday_events,
                           saturday_events=saturday_events,
                           img_url=get_header(),
                           img_url1=get_logo())

def show_admin_event_info(name, event):
    '''
    Renders a page with the information for the given event.
    '''
    return render_template('adminevents.html', name=get_display_name(name),
                           description=split_description_lines(event[DESCRIPTION]),
                           img_files=event[IMG_FILES],
                           links=event[LINKS],
                           img_url=get_header(),
                           img_url1=get_logo())

# ------- CLIENT SIDE ROUTING ---------
@app.route('/')
def homepage():
    '''
    Redirects user automatically to welcome page.
    '''
    return redirect(url_for("welcome"))

@app.route('/welcome')
def welcome():
    '''
    Renders generic welcome page for non-logged in users.
    '''
    return show_welcome()

@app.route('/welcome/<user_id>')
def client_welcome(user_id):
    '''
    Launches home page.
    '''
    # Retrieves and shows campus map.
    return show_client_welcome(user_id)

@app.route('/login', methods=['POST', 'GET'])
def client_login():
    '''
    Checks user credentials to determine if user can log in.
    '''
    # If email has been sent to log in, check to see if email is in database.
    if request.method == 'POST':
        email = request.form[EMAIL].lower()

        users = DB.collection('users').where(EMAIL, '==', email).get()
        user = None
        for u in users:
            user = u

        # return error page is user isn't in database
        if user is None:
            return show_client_email_error()

        # If user exists, check to see if password matches
        if user.to_dict()[PASSWORD] != '':
            # If password exists, redirect to password input
            return redirect(url_for('client_password', user_id=user.id))

        # If password doesn't exist, redirect student to create password
        return redirect(url_for('client_register', user_id=user.id))

    # Show client login page
    return show_client_login()

@app.route('/auth/<user_id>', methods=['POST', 'GET'])
def client_password(user_id=None):
    '''
    Checks to see if client password matches input.
    user_id: Identifies user

    '''

    # If password has been attempted, check to see if it matches password
    # in database.
    if request.method == 'POST':
        password_attempt = request.form[PASSWORD]
        user_password = DB.collection(USERS_COLLECTION).document(user_id).get().to_dict()[PASSWORD]

        # If they match, log user in.
        if check_password_hash(user_password, password_attempt):
            return redirect(url_for('client_schedule', user_id=user_id))

        # Otherwise, show error message
        return show_client_login_error(user_id)

    return show_client_password(user_id)

@app.route('/register/<user_id>', methods=['POST', 'GET'])
def client_register(user_id=None):
    '''
    Client is redirected here if they do not have a password in the database.
    Sets the client's password.
    '''
    # Makes sure passwords are matching and are more than eight characters long
    if request.method == 'POST':

        if request.form[PASSWORD] != '' and request.form[VERIFY_PASSWORD] != '':
            if request.form[PASSWORD] == request.form[VERIFY_PASSWORD]:
                if len(request.form[PASSWORD]) >= 8:
                    # Get hashed password
                    hashed_password = generate_password_hash(request.form[PASSWORD])

                    # Update user's hashed password in authentication
                    auth.update_user(user_id, password=hashed_password)

                    # Update user's hashed password in the database
                    user_ref = DB.collection(USERS_COLLECTION).document(user_id)
                    user_ref.set({"password": hashed_password}, merge=True)

                    # Redirect user to the schedule
                    return redirect(url_for('client_schedule',
                                    user_id=user_id))

                # Invalid password, show error in registration page
                return show_client_register_error(user_id)

        # Passwords don't match, show error in registration
        return show_client_register_error(user_id)

    # Show registration page
    return show_client_register(user_id)

@app.route('/schedule', defaults={'user_id': None})
@app.route('/schedule/<user_id>')
def client_schedule(user_id=None):
    '''
    Shows the current schedule.
    '''

    # Get event names and information
    event_names, event_infos = get_events(user_id)
    # Add name to event information dictionary
    for i in range(0, len(event_names)):
        event_name = event_names[i]
        event_infos[i][NAME] = get_display_name(event_name)

    # Separates events between occurring on Friday
    # and on Saturday and sorts by time
    friday_events, saturday_events = separate_and_sort_events(event_names, event_infos)

    return show_client_schedule(user_id, friday_events, saturday_events)

@app.route('/candidate-info/<user_id>')
def candidate_info(user_id=None):
    '''
    Show the candidate info card for a given candidate.
    '''
    # Gets the user's information as a dictionary
    user_dict = DB.collection('users').document(user_id).get().to_dict()

    # Converts the interview time to conventional time)
    user_dict[INTERVIEW_TIME] = convert_conventional(user_dict[INTERVIEW_TIME])

    # Renders candidate info page with the user's information
    return show_candidate_info(user_id, user_dict)

@app.route('/event-info/<name>/', defaults={'user_id': None})
@app.route('/event-info/<name>/<user_id>')
def event_info(name, user_id=None):
    '''
    Shows additional information for a given event.

    Inputs:
    name - the name of the event to show more information for
    '''

    # Show page with more event information
    return show_event_info(name, user_id, DB.collection(EVENTS_COLLECTION).document(name).get().to_dict())

# ----- CLIENT RENDERING -------
def show_welcome():
    '''
    Shows the generic welcome page for non-logged in users.
    '''

    return render_template('welcome.html', img_url=get_header(),
                           img_url1=get_media_link('campusmap.jpg'),
                           img_url2=get_logo(),
                           img_url3=get_media_link('welcomepage.jpg'))

def show_client_welcome(user_id):
    '''
    Shows the welcome page for a logged-in user.
    '''

    return render_template('clientwelcome.html', img_url=get_header(),
                            img_url1=get_media_link('campusmap.jpg'),
                            img_url2=get_logo(),
                            img_url3=get_media_link('welcomepage.jpg'),
                            user_id=user_id)

def show_client_login():
    ''' Shows the client login page so that the
    user can enter their email address and login. '''

    return render_template('clientlogin.html', img_url=get_header(),
                           img_url1=get_logo())

def show_client_email_error():
    '''
    Shows error message if invalid email address in client login.
    '''
    return render_template('clientemailerror.html',
                           img_url=get_header(),
                           img_url1=get_logo())

def show_client_login_error(user_id):
    '''
    Shows an error message due to invalid login attempt.
    '''
    return render_template('clientloginerror.html', img_url=get_header(),
                           user_id=user_id, img_url1=get_logo())

def show_client_password(user_id):
    '''
    Shows page that prompts user to enter their password (to validate their
    login attempt).
    '''
    # Prompt user to enter password
    return render_template('clientloginpassword.html', img_url=get_header(),
                           user_id=user_id,
                           img_url1=get_logo())

def show_client_register_error(user_id):
    '''
    Renders error page for registration errors.
    '''

    return render_template('clientregistererror.html',
                           img_url=get_header(),
                           user_id=user_id,
                           img_url1=get_logo())

def show_client_register(user_id):
    '''
    Shows registration page for a user, that allows them to set their password
    for the first time.
    '''

    return render_template('clientregister.html', img_url=get_header(),
                           img_url1=get_logo(),
                           user_id=user_id)

def show_client_schedule(user_id, friday_events, saturday_events):
    '''
    Shows the schedule for a specific user. Shows only the events for that
    user's Candidates' Weekend.
    '''

    return render_template('clientschedule.html', friday_events=friday_events,
                           saturday_events=saturday_events,
                           img_url=get_header(),
                           img_url1=get_logo(), user_id=user_id)

def show_candidate_info(user_id, user_dict):
    '''
    Shows the information for the given candidate.
    '''

    return render_template('clientinfo.html', user_id=user_id,
                           user=user_dict, img_url1=get_logo(),
                           img_url=get_header())

def show_event_info(name, user_id, event):
    '''
    Shows the event information for a user, with the appropriate tabs in
    the navigation bar.
    '''

    return render_template('events.html', name=get_raw_name(name),
                           description=split_description_lines(event[DESCRIPTION]),
                           img_files=event[IMG_FILES],
                           links=event[LINKS],
                           img_url=get_header(),
                           img_url1=get_logo(),
                           user_id=user_id)

if __name__ == '__main__':
    # Configures app and uploads folder for the app
    UPLOAD_FOLDER = os.getcwd()
    # Defines allowed extensions to limit acceptable files to upload
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Configures database and gets access to the database
    PROJECT_ID = "klgsglksgjs"
    CRED = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(CRED, {
        'projectId': PROJECT_ID,
        'storageBucket': PROJECT_ID + ".appspot.com"})

    # Initialize the client for interfacing with the database
    DB = firestore.client()

    # Initializes Firebase Storage bucket for file uploads/retrieval
    BUCKET = storage.bucket()

    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.01'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT, debug=True)
