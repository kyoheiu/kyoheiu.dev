+++
title = "Haskellの素因数分解"
date = 2020-05-02
[taxonomies]
categories = ["code"]
tags = ["Haskell"]
+++

```hs
headPrimeFactor :: Integer -> Integer
headPrimeFactor n = if fstprime == []
                    then n
                    else head fstprime
                        where
                            fstprime = filter primes [2..sqrt']
                            primes x = n `mod` x == 0
                            sqrt' = floor $ sqrt $ fromIntegral n

primeFactorsList :: Integer -> [Integer]
primeFactorsList 1 = []
primeFactorsList n = (headPrimeFactor n) : primeFactorsList (n `div` (headPrimeFactor n))
```

## メモ
たとえば`primeFactorsList 24 = [2, 2, 2, 3]`となるような関数`primeFactorsList`を作りたい。  
このリストがどう定義できるかを考えると、まず先頭の2というのは、24を[2..]で順番に割っていったときの最初の約数とおくことができる。さらにその次の2は、最初の約数である2で24を割った12について、[2..]で順番に割っていったときの最初の約数である。  
つまり、リストの`head`をとっていき、それを再帰でコンスしていくというのが、Haskellによる素因数分解の素朴な解法となるはずだ。

`headPrimeFactor`は`primeFactorsList`の補助関数で、nの平方根の整数部分までの整数のうち、nの約数となるものを`filter primes`で抽出し、その先頭の数字を返すもの。ただし、nが素数の場合はリストが空になるので、よく考えず`head`を使うとエラーが出てしまう（というか出た）。これを回避するために、リストが空である場合とそうでない場合で分岐を作らないといけない（`maybeHead`で`Nothing | Just Integer`を返すバージョンも書いてみたが、`head`を使う場合と使わない場合で分けたほうが当然ながらシンプル）。空の場合はnを、そうでない場合は最も小さい約数を返す関数となる。  
これを再帰的にコンスしていくのが`primeFactorsList`で、仕組みとしては上に書いた通り。

適当な整数を素因数分解してみると、次のようになる。

```bash
*Main> primeFactorsList 2039801
[23,131,677]
(0.01 secs, 170,624 bytes)
```
```bash
*Main> primeFactorsList 2380479237540923
[29,82085490949687]
(3.48 secs, 2,754,399,560 bytes)
```

ひとつの整数の素因数分解として速いか遅いか、まだよくわからないけれど…。 
もう少し工夫したやり方があるような気もするなぁ。