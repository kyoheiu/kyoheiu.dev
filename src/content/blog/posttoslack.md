+++
title = "HaskellでSlackに投稿する"
date = 2020-08-24
[taxonomies]
categories = ["code"]
tags = ["Haskell", "Slack"]
+++

1. [HaskellによるWebスクレイピング](@/post/haskellscraping01.md)
2. HaskellでSlackに投稿する（この記事）
3. [systemdを使ってプログラムを定期実行する](@/post/systemd-service.md)

scalpelで更新情報を抽出した後、保存されているテキストデータと異なっていた場合は、その旨をSlackへ通知を入れたい。
そのための関数は`Main.hs`とは別に`Lib.hs`へ保存する。

`Lib.hs`

```hs
{-# LANGUAGE OverloadedStrings #-}

module Lib where

import Network.Curl as NC

webhookurl :: URLString
webhookurl = "https://hooks.slack.com/services/xxxx/xxxxxxxxxxxxxxxxx"

message :: [String]
message = ["payload={\"text\": \"UPDATE: Check http://example.com/\" }"]

sendUDMessage = curlPost webhookurl message
```

最初は`slack-api`あたりを使おうかと色々探っていたのだが、単にSlack内のチャンネルに投稿するだけであれば、Incoming Webhooksを使って投稿するのが一番手っ取り早い。

cf: [Sending messages using Incoming Webhooks \| Slack](https://api.slack.com/messaging/webhooks)

コード内でWebhooksのURLが丸裸になるのが微妙だが、セキュリティ面を厳密に考慮する必要のない私的ミニプロジェクトなのでよしとする。  
Webhooksを叩くには、たとえばlinuxのターミナルからであれば`curl post`でいける。これをHaskellで実現するには、`Network.Curl`ライブラリの`curlPost`で十分。  
`message`の形式はSlackの仕様に合わせる必要があるが、投稿内容自体は件のWebサイトへのリンクがあれば事足りるので、全体として非常にシンプルにモジュールを作れた。
