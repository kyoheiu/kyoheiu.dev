+++
title = "systemdを使ってプログラムを定期実行する"
date = 2020-08-25
[taxonomies]
categories = ["code"]
tags = ["linux", "systemd"]
+++

1. [HaskellによるWebスクレイピング](@/post/haskellscraping01.md)
2. [HaskellでSlackに投稿する](@/post/posttoslack.md)
3. systemdを使ってプログラムを定期実行する（この記事）

linux上でプログラムを定期実行する手段は主に`cron`(とそのフォーク）と`systemd`を使うものの２種類あるが、今回は`systemd`を使ってみた。`cron`のフォークである`cronie`も試してみたのだが、`/etc/`以下にさしあたり必要でないディレクトリが作られたり、設定ファイルが個人的に扱いづらかったりであまり肌に合わなかった。  
`systemd`を使うメリットとしては、他のserviceと同様`systemd`管理下で一元的に扱え、動作状況などの`journal`も一覧で確認できること、依存関係を非常に簡単に設定できるので今回のようなネットワーク通信を前提とする実行ファイルの場合は特に取り回しが楽であること、あたりかと思う。デメリットは、ある程度込み入った定期実行設定をしたければ、.serviceとは別に.timerが必要であること。

実際の.serviceの内容は以下のようになる。

```toml
[Unit]
Description=scraping
Requires=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/user/xxxx
ExecStart=/home/user/.local/bin/xxxx-exe

[Install]
WantedBy=multi-user.target
```

.service作成後、`# systemctl enable`で起動時実行をオンにしておけばOK。  
ネットワークがつながった後でないとスクレイピングに失敗するため、`[Unit]`の`Requires`と`After`は必須。逆に言うとここさえ押さえれば、システム起動 -> ネットワーク確立 -> 実行という流れを作れるので、実際にはこの依存関係の設定で実行時間をある程度コントロールできるとも言える。一日一回とりにいけば十分なので、今回は.timerは作成しなかった。
