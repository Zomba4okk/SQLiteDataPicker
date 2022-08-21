# SQLiteDataPicker

## Description

This is a Python program which queries an SQLite database and writes data to a JSON file. 

You can download the database from [here](https://github.com/lerocha/chinook-database/blob/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite).<br>
Or you can find the SQL script used to populate the database [here](https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql).

The program queries customer invoice payments, with the option to filter for specific time periods, and write the output to a JSON file in format presented below.<br>
The output customers sorted by `total_paid` amount in descending order.<br>
The JSON filename include the timestamp of when the script was executed.

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

## Dependencies

The program works stable with **Python 3.8** or higher.<br>
All third-party dependencies listed in `requirements.txt` file in core directory.

## How to work with program
### Install dependencies:
```bash
make install
```
### Run tests:
```bash
make test
```
You can set up the test database more advanced using `.test.env` file.<br>
See the end of the section for more information about the available settings. 

### Run script:
```bash
python main.py [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--path path/for/output/file]
```
You can set up the database more advanced using `.local.env` file.<br>
See the end of the section for more information about the available settings. 

### DB advanced setup:
- DB_URL: string; database address
- DB_DRIVER: string; Python DB driver, which will be used by SQLAlchemy to interact with the DB
- DB_ECHO: bool; if set to `true` each executed query will be logged in console.

## Comments regarding implementation
### Tech stack
SQLAlchemy ORM is used in the program for interacting with the database.

It is one of the most used Python ORMs with big open-source community.<br>
It is distributed under an open free MIT license and available both private and commercial use.<br>
We also can be sure that the library will be kept up to date, including timely security updates, bugs and technical issues, compatibility with related packages and Python versions.

From technical perspective it provides well readable and easy-to-use interface for building queries, managing transaction/sessions, etc.<br>
We will be able to quickly deliver updates or fixes, introduce custom metrics or logs, set up hooks for specific actions.<br>
Interacting with DB through the SQLAlchemy interfaces also allows us to set up program to work with different DBMS with no need to take care of SQL dialects.
Important to mention that rarely used SQLAlchemy feature - `automap_base` - gives us lot of flexibility in this specific case: 
instead of building appropriate models manually we are just generating them by analyzing provided database.
### Optimization
While implementing a data-collecting or data-analyzing program we have to make sure that it will be able to work with big and very big amounts of data without significant issues.

To keep it there were introduced a few mechanisms in the `CustomerPaymentsDataService`.

#### Batched load:
We are not loading whole data at once. Instead, program querying configurable number of records, process them and repeat the process until nothing will be left.<br>
Use `batch_size` parameter of `CustomerPaymentsDataService._get_data_generator` method to configure number of records. Default value is 10000.

#### Data as a generator:
The program also does not store whole data in its memory. It uses Python generator to return data rows one by one from queried batch. 
When the batch ends, the generator requests a new one seamlessly and continues to return data.

Unfortunately, internal Python `json` package does not support dumping data from a generator. 
Therefore, we are using `simplejson` package instead.<br>
If `iterable_as_array=True` parameter is provided to the `simplejson.dump` method it retrieves rows one by one and immediately write them directly to target file without clogging RAM.