# Source data

This directory contains CSV files of the URI-Rs of the departments at a select set of HBCUs as collected by @deazarrillo and @chrisojackso. They have been converted to CSV using the shell commands:

```bash
 for x in $(ls *.xlsx); do x1=${x%".xlsx"}; in2csv $x > $x1.csv; echo "$x1.csv done."; done'''
 ```
