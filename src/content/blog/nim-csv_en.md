+++
title = "Parsing CSV file in Nim" 
date = 2021-01-20
math = false
[taxonomies]
categories = ["code"]
tags = ["Nim", "CSV parser"]
+++
As an exercise, I wrote a small program in Nim, the programming language that I'm learning these days.
Here, we use `parsecsv` library in standard lib.

```nim
import parsecsv

var p: CsvParser
p.open("sample1.csv")
p.readHeaderRow()
while p.readRow():
  echo "The average of ", p.row[0], " in ", 
    p.headers[2], " is ", p.row[1]
```

`readHeaderRow` is a function that gets the first row of csv and makes table (in order to access to elements of the first row, use `header[i]`.)
`readRow` sees whether we have next line or not, so we use this function in while expression to work on the entire csv.

```sh
$ nim c -r csvparse.nim
[...]
The average of May in  "2005" is   0.1
The average of Jun in  "2005" is   0.5
The average of Jul in  "2005" is   0.7
The average of Aug in  "2005" is   2.3
The average of Sep in  "2005" is   3.5
The average of Oct in  "2005" is   2.0
The average of Nov in  "2005" is   0.5
The average of Dec in  "2005" is   0.0
```

BTW, first exec time was 0.750s, second 0.013s, due to cache.

Nim shines when we want to build a small but need-to-be-efficient program in daily use, though of course it can be used for more complex applications.
