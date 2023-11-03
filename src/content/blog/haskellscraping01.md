+++
title = "HaskellによるWebスクレイピング"
date = 2020-08-23
[extra]
math = false
[taxonomies]
categories = ["code"]
tags = ["Haskell", "WEBscraping", "scalpel"]
+++

RSSを吐かず、実際に訪れないと更新されたかどうか確認できないWebサイトの情報を追うために、ささやかだがスクレイピング・プロジェクトを作った。
流れとしてはこういう感じになる。

1. Haskell(`scalpel`)により、更新情報の通知エリアのみを抜き出す
2. 抜き出してきた情報をローカルの`update.txt`の中身と比較し、同一であれば何もしない、異なっていればそれを`update.txt`に上書きした上でSlackのチャンネルへ通知（投稿）
3. このプログラムを、linux起動時にネットワークを確保した上で走るように`systemd`を使って.serviceを作成

この記事では(1)と(2)の`update.txt`の上書きまでをまとめる。続く部分は以下の記事に。

1. HaskellによるWebスクレイピング（この記事）
2. [HaskellでSlackに投稿する](@/post/posttoslack.md)
3. [systemdを使ってプログラムを定期実行する](@/post/systemd-service.md)

`Main.hs`は以下の通り。

```hs
{-#LANGUAGE OverloadedStrings#-}

module Main where

import qualified Data.ByteString.Char8 as B
import Text.HTML.Scalpel
import Data.Maybe
import Lib

url :: URL
url = "http://example.com"

filePath :: FilePath
filePath = "update.txt"

data NewsText
    = NewsText { time :: B.ByteString
               , contents :: B.ByteString } deriving (Show,Read,Eq)

main = do
    new <- scrapeURL url information
    old <- B.readFile filePath
    let new2 = B.pack $ show $ fromJust new
    if new2 == old then print "no update."
                   else do
                       Lib.sendUDMessage
                       B.writeFile filePath new2
    where
            information :: Scraper B.ByteString [NewsText]
            information = chroots ("div" @: [hasClass "information"]) newsTexts

            newsTexts :: Scraper B.ByteString NewsText
            newsTexts = do
                time <- text $ "dt"
                contents <- text $ "dd"
                return $ NewsText time contents
```

HaskellにおけるWebスクレイピング用のライブラリは他にいくつかあるようだけれど、`scalpel`は豊富な機能を持ち、たいていのことは可能という印象を受ける。今回の作業においてはオーバーキル気味かもしれないが、一回いじっておくとわりとすんなり他のケースに対しても応用できる、素直なライブラリのように感じた。  
`scalpel`を使う部分は初心者にも大して難しくなかった。`div`の`class`でまず絞り、さらにそこからタグで絞って抜き出す、という感じだ。きちんとやるならもっとエラーケースについて考えないといけないはずだが今回はパス。`scrapeURL`は`StringLike str => URL -> Scraper str a -> IO (Maybe a)`となっているので、仮に該当するタグが消失していても`Nothing`が返ってくる。シンプルだが`Maybe`の威力を感じる部分。  
結局未解決なのは、抜き出してくるテキストに日本語が含まれている場合、`Data.Text`系を採用しても正確に日本語を拾えない点。これはこちらの文字列の拾い方が悪いのか、対象のWebサイトの仕様なのかよくわからない（要調査）。今回の狙いは更新の有無のみをテキストの「イコールorノットイコール」で判別し、通知する、というものなので、文字化けは許容範囲と判断した。  
その上で、`Data.Bytestring.Char8`を採用しているのは、`String`はパフォーマンス上一応避けておきたいというのと、過去のテキストと現在のテキストそれぞれを読み込む際のすり合わせのしやすさから。`now`と`old`の型が違っていると、内容が同じでも違うものと判断してしまうので、型をちゃんと見なくてはいけない。Visual Studio Codeのエクステンション`Haskell`に最近`haskell-ide-engine`が統合されたので、型チェックにはとても有用だった。
