# Statistical Reporting Module — Technical Design

## Goal
Read an Apache web server access log (~10K lines) and produce a statistical
report showing the percentage breakdown of requests by **Country**, **OS**, and
**Browser**. Each dimension is reported separately, sorted by frequency
(descending), with two decimal places.


## High-Level Components

### 1. Database Reader
Once the script starts, it loads the IP-to-Country mapping from a database (e.g. SQLite, Redis) into memory. 
This allows for fast lookups during log parsing without hitting the database repeatedly. The mapping is stored in a dictionary for O(1) access.

Optimization:
Since the network address in the "DB" are in CIDR format (a.b.c.d/x) on the one hand and the IP addresses in the log file are exact IP addresses on the other hand,
we cannot use O(1) lookup. 
However, most network addresses in the "DB" has prefix length of at least 16, it means that the first two octets must be identical
to the first two octets of the IP address in the log file. 
Therefore, we can first filter the "DB" entries by the first two octets of the IP address in the log file, and then perform O(n) lookup on the filtered entries,
where n is the number of entries that match the first two octets. This optimization significantly reduces the number of entries we need to check for each IP address in the log file, 
improving performance while still ensuring accurate country mapping.

### 2. CLIParser
The entry point and the only component that talks to the outside world's
arguments. Command line arguments should include:
- path to log file we want to parse
- log type (e.g. "Apache")
In order to execute the script run:
$ python main.py <path to log file> apache


### 3. ProcessSpawner - unfortunately, I did not have enough time to implement it
Orchestrates parallel processing. It can use ProcessPoolExecutor.
Environment variables should set:
- number of lines that each processor should handle (e.g. 1000)
- maximum number of worker processes to spawn (e.g. 4)


### 4. LogParser
Streams raw log lines from its assigned byte range. Responsibilities:
- Open the file and seek to the chunk's start offset, reading until the end
  offset, yielding one line at a time (a generator) so memory stays flat
  regardless of file size.
- Stay format-agnostic: it knows nothing about Apache syntax — it only produces
  strings.
- In order to make it easy to maintain and extend, it receive two inputs:
  - a list of extractor - every extractor receives a log line and extracts a specific value for each dimension.
    More than one dimensions can be calculated in each extractor.
  - log line separator - we currently support only Apache logs. We treat the log file as a sort of table, where each line is a row that contains multiple fields separated by a specific separator (e.g. space, comma).
    The log line separator is used to split each log line into its constituent fields, allowing the extractors to access the relevant data for each dimension.
    By injecting a Separator class we can easily support different log formats in the future without changing the LogParser's core logic.

### 5. Extractors  
A list of classes that implements the Extractor protocol. 
Each extractor is responsible for extracting specific values from a log line for a particular dimension (e.g. CountryExtractor, OSExtractor, BrowserExtractor).
Once we want to add another dimension, it will be very easy to do it. 
We just need to implement a new extractor class that implements the Extractor protocol and add it to the list of extractors that is passed to the LogParser.

### 6. Aggregator - Since I did not implement ProcessSpawner, this component will not be needed.
Counts and reports. Responsibilities:
- summarizes the numbers from all workers, calculating totals and percentages
- print the results to output


---

## Technology Choices & Rationale
- **Python 3.13** — rich ecosystem  and expressive enough to show clean abstractions (Protocols,
  generators, dataclasses/pydantic). It's also a langauage I'm comfortable with, which has strengths in text processing.
- **pydantic** — typed, validated models for config and `LogRecord`; turns
  malformed input into explicit, handleable errors.
- **multiprocessing** — Python suffers from GIL issue. Most of the work of the script is CPU bound work. In order to enable
true parallelism (not concurrency) we need to use multiprocessing. Other languages like Java and Go enable true parallelism (that utilizes all CPUs of the machine) with threads, 
which may be more lightweight than processes.

## Trade-offs & Assumptions
Unfortunately, I did not have enough time to write unit tests.
