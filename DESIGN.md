To check the website for funtionality search these flights:

Destination: LEJ     Date: 27 May 2022

Destination: NRT     Date: 16 March 2022

Destination: MUC     Date: 18 February 2022

Destination: MIA     Date: 25 December 2021

Destination: SIN     Date: 27 December 2021

Destination: MAD     Date: 25 March 2022

Destination: ATL     Date: 7 January 2022




Or you can just execute this line of code in the terminal, and you will see a dictionary of all flights. Just check any flight you want! Codes of cities are inside the destinations dictionary and the scheduleDate defines the date of the flight. 

curl -X GET --header "Accept: application/json" --header "app_id: adf587a8" --header "app_key: e4fe059f048765a5a7527fa3f68910ff" --header "ResourceVersion: v4" "https://api.schiphol.nl/public-flights/flights?includedelays=false&page=0&sort=%2BscheduleTime"



So, first of all, I connected the API KEY provided by Schiphol airport about public flights to my web application. So, in order to run the website, the API KEY should be entered. I find this way of accessing the data very interesting since I can access the real relevant data instead of creating an artificial database. Regarding the code, I created two different functions(lookup and search) that execute queries to the server of the airport in Amsterdam based on the code of the city and flight date. The lookup function searches for the city based on the IATA code, while the search function returns a dictionary of lists that contain data about all flights in the database. According to the requirements of Schiphol Airport, I included the APP_ID and API_KEY in the headers dictionary and used it during requests. Also, there is a function for formatting cash as USD. All of these are assistant functions in helper.py that will be called in app.py.


I have a database called the airport. It contains two tables: users and tickets. 

In app.py as a first step, I imported all required modules such as Flask, SQL, etc. Then I configure the Flask app and a mail function. I decided to connect to the Gmail server since it is the most popular mail system. Apart from that, I decided to use session in order to save the user's id when he registers into the system. It is very comfortable because a user does not need to enter his username and password each time he/she logs in to the website. Also, with sessions, I can reuse the user's id any time I need instead of requesting it from the login page. 

As I said, I connected the SQL database to my program since it helps to store data, change and request when I need to use it. I exploited such queries like SELECT, INSERT INTO, DELETE, and UPDATE since these are the most important for my web application. There are two tables: users and tickets. In the first one, the primary key is the id of each user, while in the latter one the rpimary key is the id of the booked ticket. 

Moreover, I alternated two different methods like GET and POST when functions are called. So, every time users submit data I check if it was submitted via POST, so that it can be processed further, or with GET, which means that I have to just redirect users to a particular page. POST is a better option for data submission as it does not depict them in the URL bar, so it is more secure. 

When the website searches for the flight for the destination and date entered by the user, I decided to get the data about all flights from the Schiphol airport's database. This data consists of several levels of lists and dictionaries, hence I needed to keep indexing in order to get the data I want. Afterward, I used a nested for loop that helps me to keep track of whether there is any match between the user's inputs and the airport's database. Two lists for flight time and flight number are automatically updated if there is a match. I check whether there are available flights by checking if the flight time list is empty, so if it is empty, then there are no flights that satisfy the user's requirements. 

In connecting python to my HTML pages, I implemented the Jinja template engine so that I can depict responses in python on HTML pages. 

I have one layout standard page, and only the main block is changed when the user goes to other pages. The layout page contains links to CSS stylesheets and defines the general structure of all pages. 

Besides, I decided to use the flask_mail module, so that users receive an email confirmation when they book a ticket. For this function, I installed flask_mail and configured it by creating a new imaginative Gmail account for my website. 

Furthermore, I used the publically available stylesheets from Bootstrap and W3School for my website. I cited these links on the layout page. 
