+++
title = "NimでCSVファイルをパースする" 
date = 2021-01-20
math = false
[taxonomies]
categories = ["code"]
tags = ["Nim", "CSV parser"]
+++
最近勉強中の言語Nimで、ちょっとした作業用にプログラムを書いてみた。
NimはPython風の文法で簡潔かつコンパクトに高速なプログラムを書ける言語。C / C++ / Objective-Cのコードにトランスパイルすることができ、Cのライブラリも使用することが可能。

今回触ったのはStandard Libaryのparsecsv。

```
import parsecsv

var p: CsvParser
p.open("sample1.csv")
p.readHeaderRow()
while p.readRow():
  echo "The average of ", p.row[0], " in ", 
       p.headers[2], " is ", p.row[1]
```

readHeaderRowはcsvの最初の行を読み込んでテーブルを作る関数。最初の行の要素にアクセスしたいときはheaders[i]を使う。
readRowは次の行があるかどうか判定してBoolを返してくれるので、whileの条件に使えばcsv全体に手続きを順に適用できる。

```
[kyohei@myarch csvsample]$ nim c -r csvparse.nim
Hint: used config file '/home/kyohei/.choosenim/toolchains/nim-1.4.2/config/nim.cfg' [Conf]
Hint: used config file '/home/kyohei/.choosenim/toolchains/nim-1.4.2/config/config.nims' [Conf]
..............CC: stdlib_assertions.nim
CC: stdlib_io.nim
CC: stdlib_system.nim
CC: stdlib_streams.nim
CC: stdlib_lexbase.nim
CC: stdlib_parsecsv.nim
CC: csvparse.nim
Hint:  [Link]
Hint: 35986 lines; 0.750s; 48.977MiB peakmem; Debug build; proj: /home/kyohei/nim/csvsample/csvparse.nim; out: /home/kyohei/nim/csvsample/csvparse [SuccessX]
Hint: /home/kyohei/nim/csvsample/csvparse  [Exec]
The average of May in  "2005" is   0.1
The average of Jun in  "2005" is   0.5
The average of Jul in  "2005" is   0.7
The average of Aug in  "2005" is   2.3
The average of Sep in  "2005" is   3.5
The average of Oct in  "2005" is   2.0
The average of Nov in  "2005" is   0.5
The average of Dec in  "2005" is   0.0

[kyohei@myarch csvsample]$ nim c -r csvparse.nim
Hint: used config file '/home/kyohei/.choosenim/toolchains/nim-1.4.2/config/nim.cfg' [Conf]
Hint: used config file '/home/kyohei/.choosenim/toolchains/nim-1.4.2/config/config.nims' [Conf]
Hint: 7847 lines; 0.013s; 6.98MiB peakmem; Debug build; proj: /home/kyohei/nim/csvsample/csvparse.nim; out: /home/kyohei/nim/csvsample/csvparse [SuccessX]
Hint: /home/kyohei/nim/csvsample/csvparse  [Exec]
The average of May in  "2005" is   0.1
The average of Jun in  "2005" is   0.5
The average of Jul in  "2005" is   0.7
The average of Aug in  "2005" is   2.3
The average of Sep in  "2005" is   3.5
The average of Oct in  "2005" is   2.0
The average of Nov in  "2005" is   0.5
The average of Dec in  "2005" is   0.0
```

１回めの実行は0.750sかかっているが、２回めは0.013sと短縮されている。

個人的なNimの使用感としては、わずらわしいこと抜きにさくっとシンプルなプログラムを書きたいときにとても良い感じ（もちろんもっと複雑なプログラムも書けるだろうけれど）。「今時の簡潔言語」の中では一番しっくりきてます。