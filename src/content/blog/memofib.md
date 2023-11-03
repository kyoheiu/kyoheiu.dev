+++
title = "フィボナッチ数列（memoization）"
date = 2020-05-04
[taxonomies]
categories = ["code"]
tags = ["Haskell"]
+++

## memoization(?)
次に、memoizationによるフィボナッチ数列関数の作成にトライしてみる。  
memoizationとは日本語だとメモ化とも呼ばれるプログラミングの手法で、「一度計算したものを記録しておき、必要なときに取り出すようにする」効率化のこと、らしい。

前回のslowFibが遅い理由は、一度計算してしまえばそのあと再利用できる項を愚直に展開して項数を増やしているからだ。これを解決するのに、memoizationの発想は有用ではないだろうか、というわけ。  
[wiki.haskell.org](https://wiki.haskell.org/Memoization)を参考に、memoizationを実装してみる。リストに計算結果を記録しておき、都度それを取り出す、というものだ。

```
memoFib1 = (map fib [0..] !!)
            where
                fib 0 = 1
                fib 1 = 1
                fib n = memoFib1 (n-1) + memoFib1 (n-2)
```

```
*Main> memoFib1 30
1346269
(0.01 secs, 120,256 bytes)
```

これは確かに速い。  
ところが、次のように少しだけ変形をすると、結果は全く異なるものになる。

```
memoFib2 n = (map fib [0..]) !! n
            where
                fib 0 = 1
                fib 1 = 1
                fib n = memoFib2 (n-1) + memoFib2 (n-2)
```

```
*Main> memoFib2 30
1346269
(1.46 secs, 2,312,682,608 bytes)
```

実は最初自分なりに実装したのが`memoFib2`のほうだったので、だいぶ混乱した。なぜこのような違いが出るのか理解ができなければ、他のケースでmemoizationを使っていくことができない。  
どうしてもわからなかったので、r/Haskellで質問してみたら、あっさり[過去ログの回答](https://www.reddit.com/r/haskell/comments/a3va9p/why_pointfree_makes_difference_to_this_simple/)をもらえた。感謝。  
以下、まずこの回答について。

## ラムダ計算表現による変形（？）

上記の回答によると、それぞれの`memoFibx`はラムダ計算表現を用いて次のように変形できる。

```
memoFib1 = let fibList = map fib [0..] in (fibList !!)
<-> memoFib1 = let fibList = map fib [0..] in \n -> fibList !! n

memoFib2 n = let fibList = map fib [0..] in fibList !! n
<-> memoFib2 n = \n -> let fibList = map fib [0..] in fibList !! n
```

したがって、結局

```
(memoFib1) let fibList = map fib [0..] in \n -> fibList !! n
(memoFib2) \n -> let fibList = map fib [0..] in fibList !! n
```

この２つの式の差はなにか、ということになる。  
`Fib1`では`map fib [0..]`が一度だけ計算されるが、Fib2では[0..n]までその都度計算されてしまう。これが上記回答の趣旨だった。

しかしこれがよく分からない。`Fib2`でnが２回出てきているあたりが怪しいようにも思うが、そもそも最初の関数定義に`fibList`が登場していないので、いまいち腑に落ちない感じがある。もちろん、ラムダ計算表現に慣れていないから飲み込みづらいということも否定できない。

## 関数本体とwhere節の関係から考え直す
そこで、最初の`memoFib2`を、次のように`where`節を用いて表現し直してみる。

```
memoFib3 n = fibList !! n
    where
        fibList = map fib [0..] 
        fib 0 = 1
        fib 1 = 1
        fib n = (fibList !! (n-1)) + (fibList !! (n-2))
```

```
*Main> memoFib3 30
1346269
(0.01 secs, 121,112 bytes)
```

redditの回答にヒントを得て、`map fib [0..]`を１行目から外し、実質の中身をすべて`where`節内でまとめようとしたものだ。この`memoFib3`は問題なく計算を行える。  
これを、次の関数定義と見比べると、何が問題なのかが見えてくるように思う。

```
memoFib4 n = (map fib [0..]) !! n
    where
        fib 0 = 1
        fib 1 = 1
        fib n = (map fib [0..] !! (n-1)) + (map fib [0..] !! (n-2))
```

```
*Main> memoFib4 30
1346269
(1.31 secs, 2,075,739,480 bytes)
```

Fib3では、`map fib [0..]`が一度だけ計算され、`fibList`に保存される。`fib n`も`memoFib3`も、この`fibList`から値をとってきているので、計算が速くなる。  
一方、`Fib4`は`map fib [0..]`が３回登場している。これはその都度`map fib [0..]`を計算しているということだから、遅い。

これを踏まえて元の定義をもう一度見てみると、話は実は非常に単純で、最初の`Fib2`では、`fib`は`memoFib2`に、そして`memoFib2`は`map fib [0..]`に結びついている。したがって`map fib [0..]`が最低限以上の回数計算されている。一方、`memoFib1`がポイントフリーで表現されているということは、`map fib [0..]`は最終的に必要になった段階でようやく評価される、ということを実質的に意味している。このポイントフリーと遅延評価の関係を意識できていないと、大変混乱する羽目になる、というわけだった。  
適当に人のコードを写経すると理解不足なところが出てくる、という教訓。

ところでmemoizationに話を戻すと、この場合、`fibList = map fib [0..]` がその役割を担っている。`slowfib`からスタートしてみると、`map f xs`で計算結果を記録していくmemoizationのやり方はとても自然に感じられる。