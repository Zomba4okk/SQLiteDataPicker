# SQLiteDataPicker

## Instructions

We would like you to write a Python program which queries an SQLite database and writes data to a JSON file. You would need to download the database from [here](https://github.com/lerocha/chinook-database/blob/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite). 
You can find the SQL script used to populate the database [here](https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql).

The program should query customer invoice payments, with the option to filter for specific time periods, and write the output to a JSON file in this format:

```json
[
    {
        "customer_id": 57,
        "first_name": "Luis",
        "last_name": "Rojas",
        "total_paid": 46.62,
        "individual_payments": [
            {
                "date": "2009-04-04 00:00:00",
                "amount": 1.98
            },
            {
                "date": "2009-05-15 00:00:00",
                "amount": 13.86
            },
            {
                "date": "2010-01-13 00:00:00",
                "amount": 17.91
            },
            {
                "date": "2011-08-20 00:00:00",
                "amount": 1.98
            },
            {
                "date": "2011-11-22 00:00:00",
                "amount": 3.96
            },
            {
                "date": "2012-02-24 00:00:00",
                "amount": 5.94
            },
            {
                "date": "2012-10-14 00:00:00",
                "amount": 0.99
            }
        ]
    },
    ...
]
```
In the output the customers should be sorted by `total_paid` amount in descending order. The JSON filename should include the timestamp of when the script was executed. Last, we would also like to see some tests for your program (you can decide what functionalities are the most important to test).

We have provided the command line interface for the program (but you may wish to validate user input). You may use any 3rd party packages you wish. If you choose to do so, please add instructions on how to install them.



## Dependencies

- Python 3


## How to run
```bash
python main.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]
```