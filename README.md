# datacollection

This repository is for storing the in-progress development of the process of collecting data for the [NSF Award #2122525](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2122525&HistoricalAwards=false), "Examining the effects of academic mobility on individual professors' research activity and institutional human capital at HBCUs".

## The primary code

`fetch_timemaps.py` is currently the primary file to execute. This file takses a set of CSV files as input. These are currently converted from the Excel files provided by [@deazarrillo](https://github.com/deazarrillo) and [@chrisojackso](https://github.com/chrisojackso) via the command `for x in $(ls *.xlsx); do x1=${x%".xlsx"}; in2csv $x > $x1.csv; echo "$x1.csv done."; done`. Both the source XLSX file and the converted CSV files are stored in `src_data`, as expected from `fetch_timemap.py`.

## Memento and Aggregation

The Python script expects a Memento Aggregator to be running. [Memento (RFC7089)](https://datatracker.ietf.org/doc/html/rfc7089) is a standardized framework for negotiating with resources in time with the primary use case being exhibited. An aggregator acts as a central endpoint to send a request that will then be relayed to multiple archives. Few aggregators exist -- one hosted by Los Alamos National Laboratory at mementoweb.org and the free and open-source [MemGator](https://github.com/oduwsdl/MemGator) software. We will be using MemGator, as it is user-configurable. [Another instance of MemGator](https://aggregator.matkelly.com) is run by [@machawk1](https://github.com/machawk1) but ultimately it is best to run your own. See the [MemGator GitHub repository](https://github.com/oduwsdl/MemGator) for more information and to obtain a binary.

The purpose of the Pythonm script, at least initially, is to take the CSVs for input and for each URL, fetch the TimeMap. These TimeMaps (defined in the [Memento specification](https://datatracker.ietf.org/doc/html/rfc7089)) contain a list of URIs that represent historical captures of a web page in time along with inline metadata and additional context. Each of these is called a URI-M (see [RFC7089](https://datatracker.ietf.org/doc/html/rfc7089)).

## Next Steps

Once we have TimeMaps for all of the URIs in the CSVs, we can use the list of URI-Ms contained within each as the basis of the archived data that needs to be collected. [@machawk1](https://github.com/machawk1) anticipates using [warcio](https://github.com/webrecorder/warcio) for this, as it will retain context of the historical captures unlike simply iterating through each URI manually and using "save as" from the browser. Using a library like this also allows the process to be executed programmatically and helps with our ultimate need for reprocibility of the data source.
