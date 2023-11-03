+++
title = "各パーサーコンビネータにおけるtry/eof(endOfInput)の挙動"
date = 2021-07-31
[taxonomies]
categories = ["code"]
tags = ["Haskell", "Megaparsec", "Attoparsec", "Parsec"]
+++
[Advent of Code 2020のDay 19](https://adventofcode.com/2020/day/19)を解いていて、複数パーサーの選択でしばらくつまずいていたのでメモ。

### TL;DR
- MegaparsecおよびParsecでは、tryでくるんだパーサー内でeofを使うと正常に動かない場合がある？
- Attoparsecではchoice内でも問題なくendOfInputが動く。

### テキストを直和型のリストにパースする

Day 19では次のようなテキストを適切にパースすることが求められる。

```
0: 4 1 5
1: 2 3 | 3 2
2: 4 4 | 5 5
3: 4 5 | 5 4
4: "a"
5: "b"
```

これを、ひとまず次のような型としてパースしたい。

```
data Rule = Zero [Int]
          | Pairs Int [(Int,Int)]
          | Key Int Char
          deriving Show

-- expected result
[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']
```

- ０から始まる行は「特殊ルール」として、Zero [Int]で拾う。
- それ以外の行は、
  - 数字と"|"のみの行についてはPairsで、
  - アルファベットが含まれる行はKeyで拾う。

### Magaparsec - `try`で失敗してくれない？

最初に使ったのはMegaparsec。このソースコードから始めよう。

```hs
import qualified Data.Map.Strict as M
import Text.Megaparsec
import Text.Megaparsec.Char
import qualified Data.Text as T
import Data.Void
import Data.Either (rights)

type Parser = Parsec Void String

readInt x = read x :: Int

data Rule = Zero [Int]
          | Pairs Int [(Int,Int)]
          | Key Int Char
          deriving Show

zero :: Parser Rule
zero = do
  string "0: "
  list <- sepBy1 (many alphaNumChar) (char ' ')
  return $ Zero (map readInt list)

pair :: Parser (Int,Int)
pair = do
  y <- many digitChar
  char ' '
  z <- many digitChar
  return (readInt y, readInt z)

pairs :: Parser Rule
pairs = do
  n <- readInt <$> many alphaNumChar
  string ": "
  p <- sepBy1 pair (string " | ")
  return $ Pairs n p

key :: Parser Rule
key = do
  n <- readInt <$> many alphaNumChar
  string ": \""
  c <- letterChar
  char '\"'
  return $ Key n c

rules = try zero <|> key <|> pairs

main = readFile "day19e.txt" >>= print . rights . map (parse rules "") . lines
```

`cabal repl`で`main`を実行すると、結果はこうなる。

```
[Zero [4,1,5],Key 4 'a',Key 5 'b']
```

`Data.Either`の`rights`で強制的に`Right`のみを抽出しているので分かりにくいが、２〜４行めはパースに失敗している。ちなみにエラーメッセージはかなり難解。

```
Right (Zero [4,1,5]),Left (ParseErrorBundle {bundleErrors = TrivialError 1 (Just (Tokens (':' :| " 2"))) (fromList [Tokens (':' :| " \""),Label ('a' :| "lphanumeric character")]) :| [], bundlePosState = PosState {pstateInput = "1: 2 3 | 3 2", pstateOffset = 0, pstateSourcePos = SourcePos {sourceName = "", sourceLine = Pos 1, sourceColumn = Pos 1}, pstateTabWidth = Pos 8, pstateLinePrefix = ""}}),Left (ParseErrorBundle {bundleErrors = TrivialError 1 (Just (Tokens (':' :| " 4"))) (fromList [Tokens (':' :| " \""),Label ('a' :| "lphanumeric character")]) :| [], bundlePosState = PosState {pstateInput = "2: 4 4 | 5 5", pstateOffset = 0, pstateSourcePos = SourcePos {sourceName = "", sourceLine = Pos 1, sourceColumn = Pos 1}, pstateTabWidth = Pos 8, pstateLinePrefix = ""}}),Left (ParseErrorBundle {bundleErrors = TrivialError 1 (Just (Tokens (':' :| " 4"))) (fromList [Tokens (':' :| " \""),Label ('a' :| "lphanumeric character")]) :| [], bundlePosState = PosState {pstateInput = "3: 4 5 | 5 4", pstateOffset = 0, pstateSourcePos = SourcePos {sourceName = "", sourceLine = Pos 1, sourceColumn = Pos 1}, pstateTabWidth = Pos 8, pstateLinePrefix = ""}}),Right (Key 4 'a'),Right (Key 5 'b')]
```

色々と試行錯誤した結果わかったのは、`try`でくるんでいるからといって必ず適切なパーサーを選択してくれるわけではない（適切に選択してもらうためには工夫が必要）ということ。

たとえば２行目の`1: 2 3 | 3 2`のみをパースしてみると、

```
*Main> parseTest rules "1: 2 3 | 3 2"
1:2:
  |
1 | 1: 2 3 | 3 2
  |  ^^^
unexpected ": 2"
expecting ": "" or alphanumeric character
```

`try`でくるんでいるから最終的にはpairsを使ってパースしてくれるはずなのに、そうなっていない。  
ちなみに`pairs`単体でパースすると、

```
*Main> parseTest pairs "1: 2 3 | 3 2"
Pairs 1 [(2,3),(3,2)]
```

となって正しい結果が出るので、`pairs`自体にミスがあるわけではなさそうだ。

`rules`はまず`zero`をトライするが、`string "0: "`にマッチしないので失敗し、backtrackが発生する。  
次に`key`をトライする。そうすると、最初の`many alphaNumChar`は成功するが、次の`string ": \""`は失敗するのでまたbacktrackが発生する…はずなのだがそうならず、パースは失敗に終わる。

### `try`以降の選択肢の順番なのか？
最初に、`try`のくるみ方に問題があるのかもしれないと考えて、`try`のあとを色々と変えてみた。すると実際、`rules = try key <|> zero <|> pairs`とした場合は、

```
[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']
```

となり成功している。

さらに、`rules = try key <|> pairs <|> zero`の場合。

```
[Pairs 0 [(4,1)],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']
```

一見成功しているように見えるが、第１行めが`Zero`ではなく`Pairs`でのパースになってしまっているので間違っている。

`zero`, `pairs`, `key`の順番を入れ替えて試した結果は以下の通り。

order | result | T/F
:-   | :- | :-:
`zero key pairs` | `[Zero [4,1,5],Key 4 'a',Key 5 'b']` | F
`zero pairs key` | `[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)]]` | F
`pairs zero key` | `[Pairs 0 [(4,1)],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']` | F
`pairs key zero` | `[Pairs 0 [(4,1)],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']` | F
`key zero pairs` | `[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']` | T
`key pairs zero` | `[Pairs 0 [(4,1)],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']` | F

このあたりで薄々ストーリーが見えてくる。`zero`で拾いたいのに`pairs`になってしまっているのは、`0: 4 1 5`で言うと"1"までは`pairs`で拾えてしまえることがまず発端になっている。それだけなら残りを失敗するのでいいじゃないか、となりそうだが、途中でパースが止まっても成功扱いとなり、次の行に進んでしまう。

実際、

```hs
pairs :: Parser Rule
pairs = do
  n <- readInt <$> many alphaNumChar
  string ": "
  p <- sepBy pair (string " | ")
  return $ Pairs n p
```

と、`sepBy1`から`sepBy`にしてみると、結果は

```
[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Pairs 4 [],Pairs 5 []]
```

となって最後の２行が`pairs`で拾われてしまっていることがわかる。

### Megaparsecでのeofの挙動

`4: "a"`が`pairs`ではなく`key`で拾うべき行だということをプログラムに伝えるには、`try`以降のパーサーの順番をあれこれいじるよりも`eof`を使えばよいのではないか、と思いつき、以下のようにしてみる。

```hs
zero :: Parser Rule
zero = do
  string "0: "
  list <- sepBy1 (many alphaNumChar) (char ' ')
  eof
  return $ Zero (map readInt list)

pair :: Parser (Int,Int)
pair = do
  y <- readInt <$> many alphaNumChar
  char ' '
  z <- readInt <$> many alphaNumChar
  return (y,z)

pairs :: Parser Rule
pairs = do
  n <- readInt <$> many alphaNumChar
  string ": "
  p <- sepBy1 pair (string " | ")
  eof
  return $ Pairs n p

key :: Parser Rule
key = do
  n <- readInt <$> many alphaNumChar
  string ": \""
  c <- letterChar
  char '\"'
  eof
  return $ Key n c
```

しかし結果は変わらず、

```
-- try zero <|> pairs <|> key
[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)]]
```

入力の終了にのみマッチするはずの`eof`が動いていない。

念のため、テストパーサーを書いてみるとこちらはちゃんと機能する。

```
test :: Parser String
test = do
  s <- many alphaNumChar
  eof
  return s

---

*Main> parseTest test "aaa"
"aaa"
*Main> parseTest test "aaa111"
"aaa111"
*Main> parseTest test "aaa111+++"
1:7:
  |
1 | aaa111+++
  |       ^
unexpected '+'
expecting alphanumeric character or end of input
```

### Attoparsecでの挙動

つまり、`try`でくるんだパーサーにおいて`eof`がちゃんと動いていないのではないか？ということだ。  
どこかのコードが間違っている可能性も十分あるし、ソースコードを読んでいないのでMegaparsecの調査としてはここまでなのだが、本来であれば、`try`以降のパーサーの順序は極力考慮せず組み立てられるのが理想…だと思うので、これは困る。ちなみに、後に検証してみたところ、Parsecの`try`/`eof`でも同じ問題が発生する。

そこで、試しにAttoparsecを使ってみるとこちらはうまくいった。

```hs
import Data.Attoparsec.Text
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import Data.Either (rights)

readInt x = read x :: Int

data Rule = Zero [Int]
          | Pairs Int [(Int,Int)]
          | Key Int Char
          deriving Show

zero :: Parser Rule
zero = do
  string "0: "
  list <- many1 digit `sepBy1` char ' '
  endOfInput
  return $ Zero (map readInt list)

pair :: Parser (Int,Int)
pair = do
  x <- readInt <$> many1 digit
  space
  y <- readInt <$> many1 digit
  return (x,y)

pairs :: Parser Rule
pairs = do
  n <- readInt <$> many1 digit
  string ": "
  p <- sepBy1 pair (string " | ")
  endOfInput
  return $ Pairs n p

key :: Parser Rule
key = do
  n <- readInt <$> many1 digit
  string ": \""
  c <- letter
  char '\"'
  endOfInput
  return $ Key n c

rules = choice [pairs, key, zero]

main = TIO.readFile "day19e.txt" >>= print . rights . map (parseOnly rules) . T.lines

---

*Main> main
[Zero [4,1,5],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 'a',Key 5 'b']
```

もちろん、`choice`以降のリスト内の順序をどのパターンにしても、結果は変わらなかった。

ちなみに各パーサーの`endOfInput`を外すと、

```
-- rules = choice [pairs, key, zero]
[Pairs 0 [(4,1)],Pairs 1 [(2,3),(3,2)],Pairs 2 [(4,4),(5,5)],Pairs 3 [(4,5),(5,4)],Key 4 "a",Key 5 "b"]
```

となって１行目を`pairs`で拾ってしまっているので、やっぱり`endOfInput`が機能していることがわかる。

コード自体はほぼ変わらない。主な変更点としては、

Megaparsec | Attoparsec
:-: | :-:
`try` | `choice`
`eof` | `endOfInput`

まず１点め、`try`でなく`choice`を使うというのは、Attoparsecがデフォルトで失敗時backtrackをする仕様のためで、これは素晴らしい（`try`も実装されているが、これはParsecとの互換性のためと[明記されている](https://hackage.haskell.org/package/attoparsec-0.14.1/docs/Data-Attoparsec-ByteString.html#v:try)）。  
そしてMegaparsecの`eof`とAttoparsecの`endOfInput`は、どうやら局所的に違う挙動をするらしい。（MegaparsecとParsecがこの点で同じ動きをしたのは、MegaparsecがParsecのフォークだからかもしれない）

同じようなディテールで頭を悩ませている人がいたら、参考になれば幸いです。
