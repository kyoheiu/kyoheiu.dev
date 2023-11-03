+++
title = "URL短縮サービスを勢いだけで実装する"
date = 2022-09-03
math = false
[taxonomies]
categories = ["code"]
tags = ["Rust", "Backend", "zenn"]
+++

https://www.shuttle.rs/blog/2022/03/13/url-shortener
こちらのノリノリの記事にインスパイアされたので、axum を使った URL 短縮サービスを実装してみたいと思います（※バックエンドだけ）。

めちゃくちゃ雑に考えると、URL 短縮サービスとは、

- URL を受け取り、短縮された URL を返す
- その短縮版 URL にアクセスすると、元の URL にリダイレクトされる

というものです。  
したがって、短縮 URL を key、元の URL を value としてストアするデータベースが必要になります。  
丁寧にやっていくなら postgres などの永続するデータベースで実装しなければなりませんが、今回は sled を使ってみることにします。  
sled は Rust で書かれたインメモリの key/value 型のデータベースです。

> sled is a high-performance embedded database with an API that is similar to a BTreeMap<[u8], [u8]>, but with several additional capabilities for assisting creators of stateful systems.
> https://docs.rs/sled/latest/sled/index.html

さらにすべての操作が atomic ということで、インメモリということを気にしなければサーバーサイドでも活用できそうです。

### hello, world

さて、まずは axum の hello, world をとにかく形にします。

```
[dependencies]
axum = {version = "0.5.15", features = ["macros"]}
env_logger = "0.9.0"
log = "0.4.17"
tokio = {version = "1.21.0", features = ["full"]}
```

```rust
//main.rs

mod router;

use axum::{routing::get, Router};
use router::*;

#[tokio::main]
async fn main() {
    env_logger::init();
    println!("Server started.");

    let app = Router::new().route("/", get(health));

    axum::Server::bind(&"0.0.0.0:8080".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
```

```rust
//router.rs

use axum::debug_handler;

#[debug_handler]
pub async fn health() -> String {
    "Hello, developer.".to_string()
}
```

```shell-session
# cargo runの後...
$ xh -b :8080
Hello, developer.
```

無事ヘルスチェックができました。ちなみに`#[debug_handler]`はハンドラ関数のエラーメッセージをわかりやすくしてくれるマクロです。  
注意点として、`cargo add tokio`しただけでは`#[tokio::main]`がうまく動いてくれませんので、`features=["full"]`としておきましょう。

Rust で一番楽しいのはエラーハンドリングだと思っている私ですが、今回はシンプルに進めていくため`thiserror`も`anyhow`もナシでいきます。

### UUID の生成

次に、URL から短縮形を返すハンドラを実装していきます。  
各 URL に対し固有の短縮形を返さないといけないので、とにかくまず uuid を生成して返す関数を作りましょう。今回は元記事と同じく、nanoid を使ってシンプルに作ります。

```rust
//main.rs

    let app = Router::new()
        .route("/", get(health))
        .route("/shorten", post(shorten));
```

```rust
//router.rs

#[debug_handler]
pub async fn shorten(body: String) -> String {
    let uuid = nanoid::nanoid!(8);
    return uuid;
}
```

```shell-session
$ xh post localhost:8080/shorten
-0rZCBia
```

リクエストに関係なく、8 桁の UUID を返すものを実装しました。

### データベースへ登録

次に、この UUID と、リクエストの中身の URL を紐付けて、データベースへ保存します。  
データベースの初期化は main 関数の中で行い、それを shared state としてハンドラと共有するために`axum::Extension`を使います。

```rust
//main.rs

#[tokio::main]
async fn main() {
    env_logger::init();
    info!("Server started.");

    let db: sled::Db = sled::open("my_db").unwrap();
    info!("Database started.");

    let app = Router::new()
        .route("/", get(health))
        .route("/shorten", post(shorten))
        .layer(Extension(db)); // shared stateとしてハンドラと共有する

    axum::Server::bind(&"0.0.0.0:8080".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
```

ハンドラ側で shared state を呼ぶには以下のようにします。

```rust
//router.rs

// データベースに登録するため、JSONを受け取る形にします。
#[derive(Debug, Deserialize)]
pub struct Payload {
    url: String,
}

#[debug_handler]
pub async fn shorten(Json(payload): Json<Payload>, Extension(db): Extension<sled::Db>) -> String {
    info!("{:?}", payload);
    let mut uuid = nanoid::nanoid!(8);
    // uuidが登録済のものと被らないか確認
    while db.contains_key(&uuid).unwrap() {
        uuid = nanoid::nanoid!(8);
    }
    let url_as_bytes = payload.url.as_bytes();
    db.insert(&uuid, url_as_bytes).unwrap();
    info!("key: {}, value: {:?}", uuid, url_as_bytes);
    assert_eq!(&db.get(uuid.as_bytes()).unwrap().unwrap(), url_as_bytes);
    uuid
}
```

```json
# sample.json
{"url": "https://google.com"}
```

```shell-session
$ xh -b :8080/shorten < sample.json
ZAbBi7Hw
```

パニックを起こさないので問題なく DB へ追加できているようです。

### データベースから引き出す

続けて、DB から value を引き出すための関数…`/redirect/:id`へアクセスして元の URL を返すハンドラを実装していきましょう。

```rust
//main.rs
//main内でURLをキャプチャする
    let app = Router::new()
        .route("/", get(health))
        .route("/shorten", post(shorten))
        .route("/redirect/:id", get(redirect))
        .layer(Extension(db));
```

`shorten`関数と同じく、`redirect`関数内でも Extension(db)で shared state を取り出していきます。

```rust
//router.rs

#[debug_handler]
pub async fn redirect(Path(id): Path<String>, Extension(db): Extension<sled::Db>) -> String {
    match &db.get(&id).unwrap() {
        Some(url) => {
            let url = String::from_utf8(url.to_vec()).unwrap();
            info!("URL found: {:#?}", url);
            url
        }
        None => "Error: Not found.".to_string(),
    }
}
```

```shell-session
$ xh post :8080/shorten < sample.json
-8ij5irt

$ xh :8080/redirect/-8ij5irt
https://google.com
```

### リダイレクト

あとはリダイレクトの実装だけです。redirect 関数の返り値を、`axum::Redirect`とします。データベースに key がなかった場合はとりあえず`/`へリダイレクトしています。

```rust
//router.rs

#[debug_handler]
pub async fn redirect(Path(id): Path<String>, Extension(db): Extension<sled::Db>) -> Redirect {
    match &db.get(&id).unwrap() {
        Some(url) => {
            let url = String::from_utf8(url.to_vec()).unwrap();
            info!("URL found: {:#?}", url);
            Redirect::to(&url)
        }
        None => {
            info!("URL not found.");
            Redirect::to("/")
        }
    }
}
```

```shell-session
$ xh -b :8080/shorten < sample.json
9B3LgnGc

xh :8080/redirect/9B3LgnGc
HTTP/1.1 303 See Other
Content-Length: 0
Date: Sat, 03 Sep 2022 05:23:13 GMT
Location: https://google.com
```

実際に`localhost:8080/redirect/9B3LgnGc`へブラウザでアクセスしてみると、`google.com`へリダイレクトされ、ページが表示されました。

![](https://storage.googleapis.com/zenn-user-upload/d035f7fff81b-20220903.png)

実際のサービスで`/redirect/hogehoge`という URL になるのはダサいので、ルーティングをもうちょっとよしなにできるはずですが、満足したのでいったんここでお開きとします。

今回のソースコードはこちら。
https://github.com/kyoheiu/url-shortener-axum-sled
