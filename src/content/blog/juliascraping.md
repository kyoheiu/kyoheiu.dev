+++
title = "JuliaによるWebスクレイピング（簡易版）"
date = 2021-01-14
math = false
[taxonomies]
categories = ["code"]
tags = ["Julia", "WEBscraping"]
+++
Juliaで特定のWebページの更新日のみを取得するスクリプト。試し書きに近いのであしからず。

```
using HTTP

url = "http://example.com"

function main()
   head = HTTP.head(url)
   lastmod = head.headers[6]
   println(lastmod)
end

@time main()
```

```
julia> include("scraping.jl")
"Last-Modified" => "Thu, 10 Dec 2020 00:53:40 GMT"
  2.787799 seconds (9.54 M allocations: 479.701 MiB, 6.53% gc time)
```

関数定義部分はもうちょっとチェインっぽい感じでかっこよく書ける気もする。
使用するライブラリはHTTP.jlのみ。head.headersはarrayを返すので、[6]でarray中の要素を指定している（Juliaは1からカウント）。実際、head.headersと番号を指定せずにおくと

```julia
julia> head.headers
8-element Array{Pair{SubString{String},SubString{String}},1}:
           "Date" => "Thu, 14 Jan 2021 20:35:31 GMT"
   "Content-Type" => "text/html"
 "Content-Length" => "9480"
     "Connection" => "keep-alive"
         "Server" => "Apache"
  "Last-Modified" => "Thu, 10 Dec 2020 00:53:40 GMT"
  "Accept-Ranges" => "none"
           "Vary" => "Range,Accept-Encoding"
```

となる。

取得したHTMLをさらにパースしてbodyやh1など特定のタグの内容を抽出したい場合はGumbo.jlを用いる。

恐ろしく簡潔だが、ちょっと時間がかかりすぎのような気もする。ただ他言語と比較して、ということをやるまでの気力はないので、ここまでにしておきます。

#### .jlファイルの実行

ちょっと困ったのが.jlファイルの実行について。REPLモードでincludeして関数を叩く分には何の問題もないのだが、どちらかというとREPLモードに入らず直接ターミナルで実行ファイルを叩く形のほうが好みなので、方法がないか探した。
公式にはターミナルで.jlファイルのあるディレクトリにcdし、julia hoge.jlで実行可能だが、この際、.jlファイルはmoduleとしてではなく、上記のように

- 必要な関数定義
- 実行したいスクリプト

のみを記述する。ちなみにこの場合、REPLモードでも、上記のようにinclude("hoge.jl")のみで実行することはできる。
逆にmodule化してしまうと、julia hoge.jlでもinclude("hoge.jl")でもスクリプトが実行されることはない（REPLモードの場合は、スクリプト部分がシンタックスエラーと判定されてしまう）。