# Meta - QEP translation + Comparison of QEPs

Meta is a system that assists students and engineers working with database to understand how an improved query can reduce the total cost through proper indexing and sorting on commonly queried attributes.

## Getting Started

Clone or download all files from folder, and run from Main.py

### Prerequisites

The program is written in python 3 evironment, package versions used for development are just below.
```
gtts==2.0.4
psycopg2==2.8.4
pygame==1.9.6
```
Install all dependencies that are required for the project by running:
```
pip3 install -r requirements.txt
```
Ensure the DBMS used is PostgreSQL and create a database

*Database is not provided in our files, please source for your open dataset

To simplify login process fill can be set by default, by changing 'Enter_Attribute' in each of the row below. This line can be find in login.py
```
def __init__(self):
  self.database = 'Enter_database'
  self.username = 'Enter_username'
  self.password = 'Enter_password'
  self.host = 'Enter_host'
  self.portnum = 'Enter_portnumber'
 ```


### Installing

Run from Main.py

Login using your postgreSQL credentials

## Deployment

To start using the system, prepare at least 2 pairs of sql queries that is compatible with PostgreSQL and make sure that Q2 is an improvised version of Q1 which will produce a better QEP than Q1.

Input your first query in the Query 1 textbox, and click on QEP 1 button below the textbox
Input your second query in the Query 2 textbox, and click on QEP 2 button below the text box
The QEP description should be displayed immediately on the textbox below

Once both Natural Language description of the QEPs are displayed,
click on compare to see the explanation on why QEP2 is better and faster than QEP1

You can also view the QEP graph tree to compare the the Natural Language description to assist in your understanding of the QEP

## Authors

* **Wayne Lim** - Algorithm
* **Tan Jia Jun** - GUI
* **Yue Ying** - Parsing and Translation
* **Sean Yap** - Foundation and Design

## Acknowledgments

* thank you to Prof. Sourav for providing with Vocalizer.py for easier generation of QEP to text
* Friends whom share and contribute ideas to improve our system
