---
title: "Reactをaxumでサーブするためのテンプレートを作った"
date: 2024-01-07
categories: ["code"]
tags: ["react", "rust", "axum", "docker"]
---

https://github.com/kyoheiu/react-axum-template

## 概要
- クライアントサイド
  - vite
  - React
  - `npm create vite@latest`で初期化して不必要なファイルを削除したのみのシンプルな内容
- サーバーサイド
  - フレームワークはaxum
  - シリアライズはserde
  - 静的ファイルのサーブにtower-http
  - ロギングにtracing, tracing-subscriber
  
## 解説
個人プロジェクトの構成として、クライアントとサーバーを分けるかフルスタックでいくのかの選択を迫られることがままありますが、最近は分けて作ることが多いです。理由はいくつかあり、

- サーバーとクライアントの責務をきっちり分けるのがだんだん難しくなる
- Next.jsは避けたいがRemixもSvelteKitもまだそこまで安定していない
- TypeScriptでなくRustや他の言語でサーバーサイドを書きたい
  - サーバーのロジックの内容次第だが、特にファイルシステムをいじるような場合はNode.jsよりはRustのほうがいい

Remixがド安定する、もしくは非常に薄いReactフレームワークが出てくるなど、変化があればまた考えていきたいところ...

というわけでクライアントはピュアReactです。ルーティングなしだとつらいことも多いので、react-routerを使うのも想定の範囲内ですが、とりあえずテンプレートには入れていません。

### サーバー
サーバーにどの言語・フレームワークを選ぶかはそれこそ自由ですが、とりあえずRustです。そしてRustであれば、今はaxum一択と言い切ってしまいたいです。

axumで静的ファイルをサーブするには`tower-http`の`ServeDir`を使います。  
ちなみにクライアントサイドでルーティングをする場合は、やや不格好ですが、今のところ下記のようにすればルーティングをaxum側で拾うことができます（axum v0.7.2）。

```
    let static_dir = ServeDir::new("static");
    let app = Router::new()
        .route("/health", get(check_health))
        .route("/api/items", get(read))
        ...
        .nest_service("/", static_dir.clone())
        .nest_service("/items/:id", static_dir.clone())
        .nest_service("/search", static_dir);
```

`ServeDir`を使うパターンはaxumのリポジトリにもたくさんあるのですが、今のところその中のどれを使ってもうまくクライアントサイドのルーティングが拾えていません。上記のパターンであれば、（すべて`nest_service`でキャッチするという前提でですが）問題なくルーティングができます。  
enumでpathを型にしてexhaustiveな処理をすればキャッチ漏れの心配もなくなるかもしれません。このへんはルーティングの量次第ですね。

### dev
`make dev`でサーバーを立ち上げることができます（:3000）。  
ただしこれだとクライアントサイド側の変更をウォッチできないので、細かく変更して挙動を見たい場合はモックデータを使って`npm run dev`する必要があります。ここがちょっと面倒くさい。

### docker
セルフホストすることが多いので、クライアント・サーバーをまとめたdockerイメージを作れるようにしています。
```
make build VER=0.1.0
```
最終イメージはalpineがベースです。  
クライアント側は`node:slim`でビルドするだけ。  
サーバー側は、alpineで使うためにmuslが必要です。
```
FROM rust:1-alpine3.18 as server-builder
WORKDIR /server-builder
COPY ./server .
RUN apk update && apk add --no-cache musl-dev
RUN cargo build --release --locked
```
とすれば（使用しているcrateにもよりますが）ビルドできます。  
シンプルなアプリケーションであればだいたい20-30MBくらいのサイズ感になるのでうれしい。

## 結句
主に自分がうれしいたのしいテンプレートですが、ちょうどこういうのを探してたという方がいたら使ってみてください。
