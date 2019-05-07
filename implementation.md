<div class="topnav">
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/">Home</a> 
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/overview">Overview</a>
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/evolution">Evolution</a>
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/results">Results</a>
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/implementation" class="active">Implementation</a>
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/ethics">Impact</a>
	<a href="https://18chowdhary.github.io/CandidatesWeekendGuide/about">About Us</a>
 </div>

# Implementation

### User Architecture
![User Architecture](/photos/user.png)

The above image shows the Flask routing for clients (Candidates and guests). It shows the user experience flow from login to schedule to candidate info card and back. Several pages edit or access the Database:
- The register page edits the database by:
	- [updating it with a hashed version of the user's password.](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L828-L845)
- The login page access the database to:
	- [check whether the entered password matches with the password stored in the database.](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L808-L817)
- The schedule page reads from the database to:
	- [retrieve all events in the user's Candidates' Weekend](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L147-L200)
	- display essential information like the event's name, location, start time, and end time.
- The candidate info page reads from the database to:
	- [retrieve and render essential information about the user](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L877-L888), like the user's name, their individual interview time and location, group interview location, the model class they're attending and the location of the model class, and their interviewers.
- The event info page reads from the database to:
	- [retrieve and render additional information about the selected event](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L989-L1001), like images and links associated with the event and the description for the event.

### Admin Architecture
![Admin Architecture](/photos/admin.png)
The above image shows the Flask routing for admins (the Admissions office). It shows the user experience flow from login to schedule to the manager page, etc. Several pages edit or access the database:
- The add event page edits the database by: 
	- [creating a new document  for the event in the collection of events](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L369-L396), where the document id is the event's name and the event's Candidates' Weekend number concatenated, and the fields within the document is all the information for the event.
- The add user(s) page edits the database by :
	- reading in an Excel file and adding users to the [authentication](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L497-L500) and to the database. It [creates a new document for each user in the collection of users](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L502-L513), with the document id being the user ID inputted in the Excel file, and filling the field with values from the Excel file.
- The select user page reads:
	- [the list of users](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/d2810cf77cece825b41cbdca17afd5be22e3819b/Web.py#L80-L102) from the database to create a list so that the admin can select the user they want to edit.
- The edit user page accesses from the database:
	- to [populate the edit user form with all current information for a user](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L708-L721). 
- The edit user page edits the database:
	- If the admin decides to [delete a user](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L545-L548), then the corresponding document for the user is deleted. 
	- If the admin [changes any information for a user](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L550-L573), the corresponding fields' values are updated in the database.
- The select event page"
	- [reads the list of events from the database](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L399-L410) to create a list so that the admin can select the user they want to edit.
- The edit event page:
	- reads from the database to [populate the edit event form with all current information for an event](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L661-L686). 
	- If the admin decides to [delete an event](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L420-L431), then the corresponding document for the event is deleted. 
	- If the admin [duplicates an event](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L433-L450), then a new document is created with the same information, its document id being the current event's document id with the word 'copy' added to the end (to avoid duplicate document ids). 
	- If the admin [changes any information for an event](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L452-L479), the corresponding fields' values are updated in the database.
- The update CW form:
	- reads from the database to [display the current Candidates' Weekend number](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L635-L641)
	- [changes the database](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L355-L363) if the current Candidates' Weekend is changed.
- The admin schedule page:
	- reads from the database to [pull all events for the current Candidates' Weekend number](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L588-L599) and displaying essential information for each event, like the name, location, start time, and end time.
- The admin event info page:
	- [pulls additional information for the each event from the database](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/dc2723d549e145f0c0ae3388beb0547eaddef49c/Web.py#L744-L753), like images and links associated with the event and the description for the event.

### Database Structure
#### Events Collection
![Events Collection](/photos/db_events.png)

Special notes:
- There is a dummy document in the events collection that stores general information for all events. At the moment, the only information in the document is the current Candidates' Weekend, but there could be additional information added (like default locations or a list of speakers, for example).
- In order to avoid multiple documents having the same ID, but still allowing for multiple events across multiple Candidates' Weekends (and allowing for slight differences in events across Candidates' Weekends), the document ID for an event has the event's name and hyphenated additions if the event is a copy of another event and the Candidates' Weekend number. When displaying the event, two methods are used. 
	- [get_raw_name](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/f215d7c5e1d1959f931df7944ba7cbacc889357f/events.py#L98-L106) takes in an event name and strips the Candidates' Weekend number; this is used in the edit event form. 
	- [get_display_name](https://github.com/18chowdhary/CandidatesWeekendGuide/blob/f215d7c5e1d1959f931df7944ba7cbacc889357f/events.py#L108-L114) takes in an event name and strips all additions (including the word "copy"); this is used in the schedule and in the additional event information pages.

#### Users Collection
![Users Collection](/photos/db_users.png)
