+++
title = "Haskellで種類の数を数える（重複の削除）"
date = 2020-05-01
[taxonomies]
categories = ["code"]
tags = ["Haskell"]
+++

複数の要素を扱うための基礎的なライブラリをいろいろテストしてみる題材として、こちらの問題を使用させてもらう。

At Coder abc164 C - gacha 

https://atcoder.jp/contests/abc164/tasks/abc164_c

>実行時間制限: 2 sec / メモリ制限: 1024 MB
>配点 : 300点
>問題文
>くじ引きをN回行い、i回目には種類が文字列Siで表される景品を手に入れました。
>何種類の景品を手に入れましたか？
>
>制約
>1 <= N <= 2*(10^5)
>Siは英小文字のみからなり、長さは1以上10以下

たとえば入力が

```
3
apple
orange
apple
```

の場合は、appleとorangeの２種類を入手することになるので、正解の出力は2となる。

結局のところ、「種類の数」をどう定義するか（Haskellではどう定義できるか）を考えるわけだが、

1. ひとつひとつの要素が、すでにあるリストに含まれていないかを、再帰関数でチェックしていった結果生成されるリストのlength
2. 要素のかたまりを、同じ要素のかたまりに分けたときの、そのかたまりの数

たとえばこういったふうにおくことができると思う。

## 再帰関数で解く
### リストを用いた再帰関数

まずリストで再帰関数を作ったバージョン。

```hs
--TLE
import Control.Monad

delDupe :: [String] -> [String] -> [String]
delDupe [] _ = []
delDupe (x:xs) lst
    | x `notElem` lst = x : delDupe xs (x : lst)
    | otherwise       = delDupe xs lst

main = do
    n <- readLn
    s <- replicateM n getLine
    print $ length $ delDupe s []
```

`delDupe`は、与えられるリストを`(x:xs)`とし、重複がなければ`x`を第二引数の`lst`に加えつつ、`x`を含むリストを返す再帰関数。
しかしこれでは遅く、18の入力のうち７つがTLEとなってしまう。

### nubの正体
あとで気づいたのだが、Preludeにはリストの重複を削除する関数`nub`が標準でついているので、次のように書けることは書ける。

```hs
import Control.Monad

main = do
    n <- readLn
    s <- replicateM n getLine
    print $ length $ nub s
```

が、これは実は最初の「再帰での重複チェック→新たなリストの生成」と実行時間・メモリ使用量ともに変わらなかった。Preludeの`nub`の定義はこちら。

https://hackage.haskell.org/package/base-4.12.0.0/docs/src/Data.OldList.html#nub

```hs
-- | /O(n^2)/. The 'nub' function removes duplicate elements from a list.
-- In particular, it keeps only the first occurrence of each element.
-- (The name 'nub' means \`essence\'.)
-- It is a special case of 'nubBy', which allows the programmer to supply
-- their own equality test.
--
-- >>> nub [1,2,3,4,3,2,1,2,4,3,5]
-- [1,2,3,4,5]
nub                     :: (Eq a) => [a] -> [a]
nub                     =  nubBy (==)

-- | The 'nubBy' function behaves just like 'nub', except it uses a
-- user-supplied equality predicate instead of the overloaded '=='
-- function.
--
-- >>> nubBy (\x y -> mod x 3 == mod y 3) [1,2,4,5,6]
-- [1,2,6]
nubBy                   :: (a -> a -> Bool) -> [a] -> [a]
#if defined(USE_REPORT_PRELUDE)
nubBy eq []             =  []
nubBy eq (x:xs)         =  x : nubBy eq (filter (\ y -> not (eq x y)) xs)
#else
-- stolen from HBC
nubBy eq l              = nubBy' l []
  where
    nubBy' [] _         = []
    nubBy' (y:ys) xs
       | elem_by eq y xs = nubBy' ys xs
       | otherwise       = y : nubBy' ys (y:xs)
```

これは最初に作った再帰関数そのものだから、結果が同じになって当然なのだった。

## sortしてみる
### sortしてgroup（リスト）
そこで２つめの、`sort`して重複をまとめる方法。
まずはリストを用いると、このようになる。

```hs
--AC
import Control.Monad
import Data.List as List

main = do
    n <- readLn
    s <- replicateM n getLine
    print $ length . group $ List.sort s
```

Data.Listの`sort`関数をかませたリストに、隣接する同要素をリスト内リストにまとめる`group`関数をさらにかませてリスト内要素の長さをとるという手順。
かなり泥臭いやり方だが、再帰や`nub`よりも速いというのはちょっとおもしろい。

### Data.Vectorのuniq関数を用いる
リスト以外のデータ構造ではどうだろう。  
まずData.Vectorから。普通に入門書を読んでいるだけだとまず遭遇しないライブラリだが、海外のQ&AサイトではSequenceとどっちがいいの、といった質問でたまに見かける名前だ。

Data.Vector  
https://hackage.haskell.org/package/vector-0.12.0.1/docs/Data-Vector.html

これはポリフォーミックなarrayで、リスト操作とarray操作のいいとこどりをしたものである、とHackageでは説明されている。
一通りの標準的な関数は装備されているが、ここで用いたいのは`uniq`関数。

```hs
uniq :: Eq a => Vector a -> Vector a
```

隣接した同じ要素を`drop`できるものだが、「隣接している」ことが条件なのでsortedが前提となる。
そこで`sort`関数と組み合わせて次のようにする。

```hs
--AC
import Control.Monad
import qualified Data.Vector as V
import qualified Data.List as L

main = do
    n <- readLn
    s <- replicateM n getLine
    print $ length . V.uniq . V.fromList $ L.sort s
```

これでも一応問題はクリアだが、実はリストによる`group . sort`のほうが若干早いということも分かった。
感覚的には必要のない重複を`drop`できる`uniq`関数のほうがmake senseではあるのだけれど、`V.fromList`でO(n)かかってしまっているので致し方ないというところだろうか。

## Data.Setのsize関数
もうひとつ、Data.Setを見てみる。その名の通り、集合論をベースにした、同型の要素のSetを扱えるライブラリだ。  

Data.Set  
https://hackage.haskell.org/package/containers-0.6.2.1/docs/Data-Set.html  

このライブラリが楽しいのは、`Set.fromList`でリストからSetを生成する過程で、重複要素が自動的に`drop`される点。この自動`drop`がいかにも自然に感じられるところがmake senseだ。  
Data.Setを用いたコードは次のようになる。

```hs
--AC
import Control.Monad
import qualified Data.Set as Set
 
main = do
    n <- readLn
    s <- replicateM n getLine
    print $ Set.size $ Set.fromList s
```

`Set.size`はリストでいう`length`だが、これはO(1)。  
実行結果も、リスト版`group . sort`と大差がつくわけではないものの、最速。  
集合論的な発想を武器にできれば、色々な場面でかなり効率的にデータ処理ができそうな予感がする。