# Statistical Reporting Module — Technical Design

## Goal
Read an Apache web server access log (~10K lines) and produce a statistical
report showing the percentage breakdown of requests by **Country**, **OS**, and
**Browser**. Each dimension is reported separately, sorted by frequency
(descending), with two decimal places.


## High-Level Components

### 1. CLIParser
The entry point and the only component that talks to the outside world's
arguments. Command line arguments should include:
- path to log file we want to parse
- log type (e.g. "Apache")


### 2. ProcessSpawner
Orchestrates parallel processing. It can use ProcessPoolExecutor.
Environment variables should set:
- number of lines that each processor should handle (e.g. 1000)
- maximum number of worker processes to spawn (e.g. 4)


### 3. FileReader
Streams raw log lines from its assigned byte range. Responsibilities:
- Open the file and seek to the chunk's start offset, reading until the end
  offset, yielding one line at a time (a generator) so memory stays flat
  regardless of file size.
- Stay format-agnostic: it knows nothing about Apache syntax — it only produces
  strings.


### 4. LogParser
- We should have a LogParser class for every log type. All LogParser classes inherit from the same interface. 
One LogParser holds a class per each dimension. All dimensions implement the same interface.
Environment variable should set a list of dimensions to be used for every log type.
- LogParser should give a number of occurrences for each dimension. For example, for Apache log, it should give a number of occurrences for Country, OS and Browser dimensions.

**Extensibility:** adding a new dimension (e.g. "Status Class", "Path") means
writing one extractor class and registering it — no change to the reader,
spawner, or aggregator. This is the primary extension point the assignment
asks about.

### 5. Aggregator
Counts and reports. Responsibilities:
- summarizes the numbers from all workers, calculating totals and percentages
- print the results to output

### 6. Database Reader

---

## Technology Choices & Rationale
- **Python 3.13** — rich ecosystem  and expressive enough to show clean abstractions (Protocols,
  generators, dataclasses/pydantic). It's also a langauage I'm comfortable with, which has strengths in text processing.
- **pydantic** — typed, validated models for config and `LogRecord`; turns
  malformed input into explicit, handleable errors.
- **multiprocessing** — CPU-bound per-line work benefits from true parallelism.

## Trade-offs & Assumptions

