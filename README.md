# ms-uk-payslip-parser

Simple parser for payslips issued by MS UK.

Converts a series of your PDF payslips into a neat CSV table. 

## Installation

- Install Python3 3.7+ and Virtualenv
- Install dependencies
```
# create a virtualenv
mkvirtualenv payslip-parser
# switch to virtualenv
workon payslip-parser
# install dependencies
pip3 install -r requirements.txt
```
- Or if you have `pipenv` installed:
```bash
pipenv install
```

## Usage

1. Download your payslips PDF files from the portal and put them in a directory
   e.g. `~/payslips`

2. Get into your virtualenv:
    
    ```bash
    workon payslip-parser
    ```
    
    or if you have `pipenv`
    
    ```bash
    pipenv shell
    ```

3. First, convert PDF files to text:
    
    ```bash
    python3 to_text.py ~/payslips ./text_payslips
    ``` 
    
    Now you should see text files with your payslips content in `text_payslips` directory.

4. Now you can parse the text files and produce CSV tables:

    ```bash
    python3 parser.py ./text_payslips
    ``` 

   After this you will see two CSV files in this directory:
   - `payslips-month-columns.csv` - each month's data is in a separate column
   - `payslips-month-rows.csv` - each month's data is in a separate row
   
   Every payslip item label has a short prefix identifying its payslip section:
   - `.m` - metadata item
   - `.d.p` - payments data item
   - `.d.d` - deductions data item
   - `.d.t` - totals data item
   - `.d.et` - employer totals data item
   - `.d.ytd` - year-to-date data item
   
5. Open the CSV file in your spreadsheet editor of choice or Pandas.


## Feedback

Create an issue if you encounter a problem or have a suggestion.
Or ping me on Teams.

