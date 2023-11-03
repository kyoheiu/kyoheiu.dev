+++
title = "Haskell環境再構築"
date = 2021-05-05
math = false
[taxonomies]
categories = ["code"]
tags = ["Haskell", "haskell-language-server"]
+++
ここ数ヶ月、ずっとimperative programmingをしていてちょっと疲れてきたのと、今Haskellに戻ったら前よりはもう少し書ける／わかるようになっているかもしれないという期待で、あらためてHaskellに入門してみる。
### 環境構築
前にやっていたときは確か存在していなかったような気がするのだが、`ghcup`という`rustup`的なツールが登場していたのでさっそく入れてみる。  
これはghc, cabal, haskell-language-server(HLS)のインストール・バージョン管理を行ってくれるありがたいツールで、途中２回ほどコマンド入力する場面があるので完全放置では完了まで行かないが、スムーズにインストールが可能。以前はstackを使っていたが、cabalがだいぶフレンドリーになってきているという噂を見かけたのでcabal一本でやってみようかと思っている。
### 鬼門・haskell-language-server
`hie`の頃からHaskellのLSPにはいい思い出がなく、ビルド時間が地獄のように長いとか、頑張って入れても全然動かないとかで、この辺の環境構築周りのもどかしさもあっていったん離れることに決めたのだった。今はというと、ほぼ公式のLSPであるHLSがghcupでツルッと入ってくる。これを使えばいい。

ただ、Arch Linux系のディストロを使っている人は、HLSとVS Codeのインテグレーションでおそらく引っかかるだろう。

[VSCode extension not detecting Cabal/Stack due to incomplete $PATH in `/etc/profile` · Issue #236 · haskell/haskell-language-server](https://github.com/haskell/haskell-language-server/issues/236)

このissueで指摘されているが、Arch系の場合、`.bashrc`にghcupのPATHを書いてもVS Codeが認識せず、`etc/profile`に書かないと動かない。~~そして僕の場合は、`etc/profile`に書いた上で、（ランチャーからではなく）ターミナルから`code`とコマンドを打って起動しないとHLSが動かなかった。ここまでわかるのに半日費やしてしまった…。~~

(2021-05-22追記)`etc/profile`への記述が間違っていた模様。以下のようにすればVS Codeでバッチリ動いてくれました。

```
# etc/profile
PATH=~/.ghcup/bin/:$PATH
PATH=~/.cabal/bin/:$PATH
```

ランチャーからの起動が実質できないのは良くないので、これを機にneovimでの編集に移行してみる。  
ただしvim/neovimであっても、Arch系であれば`etc/profile`にPATHを書かなければならないのは同じ（記入後、要再起動）。その上で、HLS公式のイントロダクションに書いてあるとおり、CocでHLSを設定すれば、動く。

久々にHaskellを書くと、頭も指も全然動かなくて逆に面白い。  
以前いじっていたときには存在に気づかなかったパイプライン演算子を使って、Project Eulerの２問め。

```hs
import Data.Function

fib:: Integer -> Integer -> Integer -> Integer
fib a b count
    | count == 1 || count == 0 = b
    | count >= 2 = fib b (a+b) (count-1)
    | otherwise = 0

makeFib = fib 1 1

euler2FibList:: Integer -> Integer
euler2FibList n = takeWhile (\x -> makeFib x < n) [1..] & map makeFib & filter even & sum

main = print $ euler2FibList 4000000
```

`makeFib`を２回使っているのがかっこよくないですね。
