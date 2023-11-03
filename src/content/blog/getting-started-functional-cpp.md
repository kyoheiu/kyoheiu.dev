+++
title = "関数型的に入門するC++"
date = 2021-09-08
[taxonomies]
categories = ["code"]
tags = ["C++", "Haskell"]
+++

C++に興味が出てきて勉強中。参考としているのは[江添亮の C++入門](https://ezoeryou.github.io/cpp-intro/#%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0)。わかりやすく、ユーモアもところどころあって楽しい。とりあえずアルゴリズムについて、関数型（というか Haskell）的な視点でまとめておく。

#### 一覧

[アルゴリズム](https://ezoeryou.github.io/cpp-intro/#%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0)の章で紹介されている各関数は高階関数として捉えると理解が捗る。とくにこの場合、イテレータから説明が続いているので、`Foldable a`に対して適用される`Data.List`収録の関数として変換していくととても覚えやすいと思う。

```
for_each -> map || foldr
all_of -> all
any_of -> any
none_of -> !all
find -> elem
find_if -> head . filter f
count -> length . filter (==x)
count_if -> length . filter f
equal -> [a] == [b] || f([a]) == f([b])　 //関数をとる場合もある
search -> ???
transform -> map

//ラムダ式
[](a x) -> b {...}
\x -> f(x) :: a -> b
```

練習も兼ねて書いてみよう。上が Haskell、下が main 関数で記述した C++（厳密には対応していないので悪しからず）。

#### for_each

```
map (*2) [1..4]

-----

void f(int x)
{
    x = x * 2;
    std::cout << x << "\n";
}

int main()
{
    std::vector<int> v = {1, 2, 3, 4};
    for_each(std::begin(v), std::end(v), f);
}

//ラムダ式
for_each(std::begin(v), std::end(v), [](auto x)
             { std::cout << x * 2 << "\n"; });
```

#### all_of

```
all (even) [2,4,6,8]

-----

int main()
{
    std::vector<int> v = {2, 4, 6, 8};
    std::cout << std::boolalpha;
    std::cout << all_of(std::begin(v), std::end(v), [](auto value)
                        { return value % 2 == 0; });
}
```

#### find

```
3 `elem` [1..4] // True
5 `elem` [1..4] // False

-----

int main()
{
    std::vector<int> v = {2, 4, 6, 8};
    if (std::end(v) == find(std::begin(v), std::end(v), 4))
    {
        std::cout << "Not found.\n";
    }
    else
    {
        std::cout << "Found.\n";
    }
}
```

`find(first, last, value)`の場合、value が見つからなかったときに返るのは last だが、出力時に要素の`0`と区別がつかなくなってしまうので、`std::end(v)`との比較でケースを分けている。パターンマッチングでもっとシンプルにしたいが…？

#### count

```
(length . filter (==1)) [1,2,1,1,2,1,3]

-----

int main()
{
    std::vector<int> v = {1, 2, 1, 1, 2, 1, 3};
    std::cout << count(v.begin(), v.end(), 1);
}
```

#### search

```
import qualified Data.List as L

search :: Eq a => [a] -> [a] -> Maybe Int
search xs ys =
  case L.elemIndex (head xs) ys of
    Just n ->
      if take (length xs) (drop n ys) == xs
        then Just n
        else (+) <$> Just (n + 1) <*> search xs (drop (n + 1) ys)
    Nothing -> Nothing

-----

int main()
{
    std::vector<int> v1 = {1, 2, 3, 4, 5, 6};
    std::vector<int> v2 = {2, 3, 4};

    std::cout << *search(v1.begin(), v1.end(), v2.begin(), v2.end());
}
```

`search(first1,last1,first2,last2)`は、[first1,last1)の範囲に[first2,last2)があれば、見つかったサブシークエンスの先頭のイテレータを返す関数。微妙に複雑だ。  
これを Haskell で実装してみると…。単に「含むかどうか」を`Bool`で返すなら`isInfixOf`があるが、最初の要素となると、先頭がマッチするだけでなく、そのあとの並びがきちんと求めるリストと一致しているかどうかを見た上で、`drop`した数と足していかないといけない。

#### C++、面白い

「C++で関数型プログラミングをする」ために書かれた本もいくつかあるようだ。

[Manning | Functional Programming in C++](https://www.manning.com/books/functional-programming-in-c-plus-plus)

[Amazon | Hands-On Functional Programming with C++: An effective guide to writing accelerated functional code using C++17 and C++20 (English Edition) \[Kindle edition\] by Bolboaca, Alexandru | Hardware | Kindle ストア](https://www.amazon.co.jp/dp/B07MTBCCV5)

上の Manning の本を読み始めているが、関数合成的（？）なことができるパイプというものがあるらしく、色々できそうで楽しみです。
