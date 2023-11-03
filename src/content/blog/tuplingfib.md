+++
title = "フィボナッチ数列（Haskellタプリング法）"
date = 2020-05-03
[taxonomies]
categories = ["code"]
tags = ["Haskell"]
+++

## naive fib
まずnaiveな定義から。

```
slowFib 0 = 1
slowFib 1 = 1
slowFib n = slowFib (n-1) + slowFib (n-2)
```

```hs
*Main> slowFib 30
1346269
(1.54 secs, 929,853,032 bytes)
```

n=30くらいまではなんとか耐えられるが、びっくりするくらい遅い。[Learn You a Haskell for Great Good](https://www.amazon.co.jp/dp/B004VB3V0K/)に特に注釈無しで記載されているので、学習中の人は一度は試してみたことがあると思う。Haskellってもしかして遅いのかな？ と学習者を不安にさせる遅さだ。  
[Haskellによる関数プログラミングの思考法](https://www.amazon.co.jp/dp/4048930532/)によると、この関数の計算量はO(Φ^n)（Φ=(1+√5)/2, 黄金律）なので、指数オーダーで計算量が増えていくことになるが、黄金律と言われてもあまりピンとこないのでもう少しこねてみる。  
計算を分解してみると、たぶん次のようになるはずだ。

```hs
slowFib n
= slowFib (n-1) + slowFib (n-2)
= (slowFib (n-2) + slowFib (n-3)) + (slowFib (n-3) + slowFib (n-4))
= (slowFib (n-3) + slowFib (n-4)) + (slowFib (n-4) + slowFib (n-5)) + (slowFib (n-4) + slowFib (n-5)) + (slowFib (n-5) + slowFib (n-6))
...
```

２行めでは２項だったのが３行めでは４項、４行めで８項になっているので、ここまでは項数は^2で増えていく。もちろんすべての項が一律に倍の項数になるわけではなく、前の項から順番に、いずれ`slowFib 1(0)`に達するので、それ以上は項数は増えない。そして全体でみると、２より少し小さいくらいの数字（＝黄金律）の指数オーダーで項数が増えていく。…ということだと思う。

## タプリング法
[入門Haskellプログラミング](https://www.amazon.co.jp/dp/B07SFCMP66/)にあったヒントをもとに実装したもの。

```hs
fasterFib 1 (a,b) = a
fasterFib n (a,b) = fasterFib (n-1) (a+b,a)
```

```hs
*Main> fasterFib 30 (1,1)
1346269
(0.01 secs, 117,312 bytes)

*Main> fasterFib 50 (1,1)
20365011074
(0.01 secs, 127,296 bytes)
```

第一引数はカウンタで、これが1になるまで1つずつ減らしていく。減らしていく過程で第二引数のペアが足され、次のペアを生成する。これは（たぶん）タプリング法と呼ばれる手法なのだが、なぜこれが速いのか、自分で実装しておきながら理屈がいまいちピンとこなかったので、分解してみる。

```hs
fasterFib 30 (1,1)
= fasterFib 29 (2,1)
= fasterFib 28 (3,2)
= fasterFib 27 (5,3)
...
= fasterFib 1 (1346269,832040)
= 1346269
```

項数がどの行も同じ１つで済んでいるということが、こういうふうに書いてみれば明らかだ。
[Haskellによる関数プログラミングの思考法](http://https://www.amazon.co.jp/dp/4048930532/ "Haskellによる関数プログラミングの思考法")は少し違う形で実装していて、

```hs
--fib2 n = (fib n, fib (n+1))と考えて
fib2 0 = (0,1)
fib2 n = (b,a+b)
	where
		(a,b) = fib 2 (n-1)
```

としている。著者によると、「タプリング法では引数を追加して関数を一般化するのではなく、結果を追加して関数を一般化する」(p.161)。  
`fasterFib`は引数（左辺）のほうに追加しているが、実質的には`fib n = fib (n-1) + fib (n-2)`という計算の結果を引数として追加しているので、変形タプリング法と呼べる、かもしれない。`fib2`のほうは逆に、式の右辺にペアの形で追加している。タプル（ペア）の形で計算の結果をまとめて関数内で用いる、というのがタプリング法の肝であるようだ。