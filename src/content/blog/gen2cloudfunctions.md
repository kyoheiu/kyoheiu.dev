---
title: "gen2 Cloud FunctionsをCloud Schedulerで定期実行する"
date: 2023-11-17
categories: ["code"]
tags: ["GCP", "cloud functions", "cloud scheduler", "Go"]
---

```
23-11-18 nil checkについての記述を修正
```

## 概要

RSS Feedを取得して、定数時間内に更新された記事のタイトルとURLをDiscordのプライベートチャンネルに投稿するだけのCloud Functionsをデプロイし、それをCloud Schedulerから定期実行したい。

## 背景

これまでFreshRSSをセルフホストしていたのですが、豊富な機能をほぼ使っていないことが気になっていました。結局FressRSS上でテキストを読むことはあまりせず、URLをあとで読む用にWebアプリに送るだけだったので、それならとにかく更新された記事のタイトルとURLだけ分かればよさそうです。

プライベートで使っているDiscordサーバーがあり、これまでもちょっとしたものをWebhook経由でそこに送りこんでいたので、今回もこれをフロントエンド代わりに使います。

※フロントエンドとしてチャットアプリケーションを使うというのはけっこう好きな発想で、当然アプリケーション自体に依存することになるとはいえ、大幅に工数を減らすことができるのでよいですね。

この規模であればかんたんなサーバーを立ててcronで定期実行する、と考えるのが一番実装時間が短くて済むはずですが、今回は勉強を兼ねて、GoとGCPを触ります。

## 構成

- Cloud Schedulerが認証付きCloud Functionsを定期実行する。
- Cloud Functions内のGoのコードでRSS Feedを取得してパースし、適当な期間内にpublishされたもののタイトルとURLをWebhook経由でDiscordのチャンネルに投稿する。

https://github.com/kyoheiu/discorss

## Cloud Functions

Feedのパースには`gofeed`を使います。

```go
func ParseItem(siteTitle string, item *gofeed.Item) (*DFeed, error) {
	//Send feed 3 times in a day (24/3)
	timeLimit := 8

	if item.PublishedParsed == nil {
		return nil, errors.New("cannot get published date: " + item.Title)
	} else if item.PublishedParsed.Before(time.Now().Add(time.Duration(-(timeLimit)) * time.Hour)) {
		return nil, errors.New("too old post: " + item.Title)
	} else if item.PublishedParsed.After(time.Now().Add(time.Duration(timeLimit) * time.Hour)) {
		return nil, errors.New("too new post: " + item.Title)
	}

	return &DFeed{
		Title:     siteTitle,
		ItemTitle: item.Title,
		Url:       item.Link,
		Published: item.PublishedParsed,
	}, nil
}

func GetFeedConcurrently(feeds []string, ch chan DFeed) {
	defer close(ch)

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	fp := gofeed.NewParser()

	for _, feed := range feeds {
		success := 0
		skipped := 0
		parsed, err := fp.ParseURLWithContext(feed, ctx)
		if err != nil {
			fmt.Println(err)
			continue
		}
		items := parsed.Items
		for _, item := range items {
			d, err := ParseItem(parsed.Title, item)
			if err != nil {
				skipped += 1
				continue
			}
			if d != nil {
				ch <- *d
				success += 1
			}
		}
		fmt.Println(parsed.Title + " SUCCESS: " + fmt.Sprint(success) + " SKIPPED: " + fmt.Sprint(skipped))
	}
}
```

### nil check

パースする中で`*time.Time`型であるPublishedParsedフィールドを取り出すプロセスがあるのですが、ここで当初`SIGSEGV`が出てしまい、詰まっていました。  
調べてみるとGoのnilは、特に`interface{}`についてのnil checkをする際には気をつけないといけない点があるとのこと。

https://amyangfei.me/2021/02/17/golang-nil-panic/

> Interface in Go contains both type and value, when checking whether nil with an interface, there are two cases
>
> 1. Interface has nullable type(like pointer, map, etc) and value is nil
> 2. Interface itself has a nil type.

`if item.PublishedParsed == nil`とやっていたのがnil checkをしきれていなかった原因かと考えて、、型キャスト `item.PublishedParsed == (*time.Time)(nil)` してみたのですが、`SIGSEGV`が消えません。  
色々と変えてみたところ、結局これは`gofeed.ParseURLWithContext`が第１引数に空の文字列をとるときにerrを出すのをキャッチできていなかったことが原因でした。  
テキストファイルを読み込んで改行でsplitするプロセスを踏むような場合は、sliceの要素が空文字列でないかの確認が必要になります。

この関数をgoroutineで並列処理します。

```go
func SendFeed(w http.ResponseWriter, r *http.Request) {
	feeds := SetFeedList()

	ch := make(chan DFeed)

	go GetFeedConcurrently(feeds, ch)

	client := http.Client{
		Timeout: 30 * time.Second,
	}

	for dfeed := range ch {
		content := fmt.Sprintf("%s %s <%s>", dfeed.Title, dfeed.ItemTitle, dfeed.Url)
		j, err := json.Marshal(Req{Content: content})
		if err != nil {
			fmt.Println(err)
			continue
		}

		url := os.Getenv("DISCORSS_URL")
		if len(url) == 0 {
			fmt.Println("Cannot get webhook url.")
			continue
		}

		req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(j))
		if err != nil {
			fmt.Println(err)
			continue
		}
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		if err != nil {
			fmt.Println(err)
			continue
		}
		fmt.Println(dfeed.ItemTitle, dfeed.Url, resp.StatusCode)
	}
}
```

Discordでは通常、URLはプレビューが表示されて便利なのですが、今回はURLを複数一度に投稿する関係上、プレビューを消したいです。この場合、`<URL>`とカッコでくくってあげるとプレビューが出ずに一覧性が増します。

これを`GoogleCloudPlatform/functions-framework-go/functions`の`functions/HTTP`でサーブします。

```
import (
	feed "github.com/kyoheiu/discorss/feed"

	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
)

func init() {
	functions.HTTP("SendFeed", feed.SendFeed)
}
```

## Cloud Functionsにデプロイする

Cloud Schedulerとの連携が必要なので、サービスアカウントを作っておきます。  
注意点として、gen2のCloud FunctionsはCloud Runベースなので、`Cloud Run Invoker`ロールを付与しておく必要があります。このへんドキュメンテーションにあったかな…ないような気がするけど気のせいかな…

サービスアカウントを作っておいてから、下記のコマンドでデプロイすします。

```
gcloud functions deploy discorss --gen2 --runtime go121 --trigger-http --entry-point SendFeed --region=us-west1 --service-account example@example.com
```

デプロイ中に認証されていないアカウントからの起動を許可するかどうか聞かれるので、デフォルトのNoとしておきます。

ちなみに、package名がmainだとデプロイに失敗してしまうので、適当なpackage名にし、main関数も書かずにデプロイしないといけません。

:::message
つまり`go run main.go`で愚直に結果を見る、というのをやりづらいので、ちゃんとテストコードを書いたほうがいい。
:::

## Cloud Schedulerを設定する

ターゲットはHTTP、メソッドはGET。  
Auth HeaderにOIDC Token、サービスアカウントにすでに作成済みのアカウントを設定すればOK。
（とかんたんに書いているが、ここでだいぶ時間を食われました）

## 感想

Goがだんだんおもしろくなってきました。
