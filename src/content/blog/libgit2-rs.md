+++
title = "Rustで疑似マイクロサービスを動かす体験がすごくよい - libgit2編"
date = 2023-09-04
[taxonomies]
categories = ["code"]
tags = ["rust", "git", "libgit2", "nodejs", "nodegit", "svelte", "docker"]
+++

## 文脈

ここのところ、セルフホストするオンラインテキストエディタを自作していたのですが、作っているうちに「テキストファイルに変更を加えたときに自動で`git add {filename}` `git commit -m {message}`できると便利？」と思いつき、色々試していました。その結果得られた知見の共有です。

作ったもの  
https://github.com/kyoheiu/carbon  
Rustaceanに大人気[要出典]のSvelteKit + axumで作っています。

ちなみにこのテキストも上記のテキストエディタでドッグフード的に書いています。

## TL;DR
- 特定の処理だけRustに切り出してミニミニサーバーを作るのは思った以上に体験がよい
  - Rustのエラーハンドリングの恩恵を受けられ、またfeature-gateにより依存パッケージも極力減らすことができる　→　コンテナサイズも最小化できる
- 例としてlibgit2の処理を紹介

ここでいう「特定の処理」とは、とりあえず【JSフレームワーク内でどうしてもうまくいかない処理】のことを指していますが、通常Rustへの切り出しを検討されるような重い計算を含む処理についても同じ考え方が適用されるのではないかと思います。

もちろんFFIも選択肢としてありますが、型のことを考えたり、FFI自体、いくつかのライブラリの中から選ぶコストがあったりと、単純にFFIでいいじゃんとなる場面ばかりではないと思います。そうした場合、一考の価値があるパターンではないでしょうか。

## git操作の２つのパターン
今回Rustにアウトソーシングしたのはgit操作です。

バックエンドでgitを動かしてあれこれするのはGit-poweredとも呼ばれ、gollum wikiなども実装している古来よりの知恵ですが、方法としてはざっくり２パターンあり、

1. 素直にchild processをspawnして実行する
2. libgit2（のバインディング）を呼び出して実行する

このどちらかを選ぶことになると思います。  

### child processを使う場合

こちらはいつものコマンドを叩くだけなので、だいたいこんな感じになるでしょう。

```rust
use std::process::Command;

let status = Command::new("git")
                     .args(["add", file_name])
                     .status()
                     .expect("failed to execute process");
// 以下略
```

この方法のメリットとしては、実行環境にgitがインストールさえされていればいつもの感覚で動かせること。しかしデメリットもあります。

- gitをインストールするには依存パッケージも一緒にインストールしないといけないため、たとえばコンテナ環境の場合コンテナサイズが膨らんでしまう。依存パッケージにはopensslなども含まれるため、セキュリティ面で考えなければいけないことも同時に増えます。
- addとcommitだけだったとしても、１つの変更につき２つプロセスを生成しないといけない。

今回はコンテナサイズをなるべく縮めたかったため、以下の方法をとることにしました。

### libgit2を使う
> libgit2 is a portable, pure C implementation of the Git core methods provided as a re-entrant linkable library with a solid API, allowing you to write native speed custom Git applications in any language that supports C bindings.  
(https://libgit2.org/)

上記引用のとおり、gitのC実装ライブラリがlibgit2です。各言語でバインディングライブラリが提供されており、Rustではrust-langチームによるgit2-rsが、Node.jsではnodegitがそれにあたります。

コードとしてはどの言語でも大体似たような感じになります。たとえばRustだと、
```rust
let repo = Repository::open(dir_path)?;
let mut index = repo.index()?;
index.add_path(std::path::Path::new(file_to_add))?;
//git add
index.write()?;

let new_tree_oid = index.write_tree()?;
let new_tree = repo.find_tree(new_tree_oid)?;
let author = git2::Signature::now(git_user, git_email)?;
let head = repo.head()?;
let parent = repo.find_commit(
    head.target()
        .ok_or_else(|| Error::Git("Failed get the OID.".to_string()))?,
)?;
//git commit
repo.commit(
    Some("HEAD"),
    &author,
    &author,
    commit_message,
    &new_tree,
    &[&parent],
)?;
```
こんな感じです。（一部カスタムエラーを使用していますが、そのへんはよしなに処理してください）

nodegitでも、
```typescript
export const addAndCommit = async (file: string, message: string) => {
	const repo = await git.Repository.open(DATA_PATH);
	const index = await repo.refreshIndex();
	const result = await index.addByPath(file);
        //git add
	await index.write();

	const changes = await index.writeTree();
	const head = await git.Reference.nameToId(repo, 'HEAD');
	const parent = await repo.getCommit(head);
	const author = git.Signature.now(name, email);
        //git commit
	await repo.createCommit('HEAD', author, author, message, changes, [parent]);
};
```
てな感じでほぼ一緒なので、どれかひとつの言語で触ってみれば他の言語のバインディングもかんたんに動かせるようになります。

## nodegitの問題点

フロントエンドはJavaScriptのフレームワークで作るケースが圧倒的多数で、最近はフルスタックで全部JS/TSで書いてしまうことも多いと思います。その場合はlibgit2もJSのバインディングで動かせれば一番話が早いわけです。
自分のケースでも、最初はSvelteKitで全部書いてしまうつもりだったので、まずnodegitを選択しました。  

nodegitは、ふつうの開発環境（≒`ssh`したりいくつかの言語をビルドしたりできる環境）であれば特に追加のパッケージをインストールすることなく動き、またビルドできるはずです。
自分の手元でも、特に環境をいじることなく上記のコードは動いていたし、ビルドでもエラーは出ませんでした。

ただ、今回のケースでは最終的にDockerイメージを作成する必要があり、そこで詰みました。

### 依存パッケージの問題
nodegitのリポジトリは最近動きが少なく、インストール方法もかなり簡略化された記述になっているので、まずnodegitをビルドできるステージを用意するのに一苦労です。
```
RUN apt-get install -y python3 libkrb5-dev gcc openssl libssh2-1-dev g++ make
```

たとえば`node:slim`を使った場合、インストールするのにまずこれだけのパッケージが必要になります。これらのパッケージの依存パッケージも含めると、すでにコンテナサイズが巨大になる未来が見えます。

### コンテナ内の挙動

さらに、`npm ci`と`npm run build`が成功したとしても、コンテナ内で正常に動くとは限りません。
自分の場合、`node:slim`では`Cannot read properties of undefined (reading 'open')`と実行時エラーメッセージが出てしまいました。何らかのパッケージが足りず、結局ビルドが出来ていないように見えますが、未解決です。

## git2-rs comes to rescue!

そこで、gitの操作だけ切り出し、専用のバックエンドを用意することでnodegitとおさらばする道を探りました。
切り出すことを決めた時点でどの言語を採用してもよかったのですが、Rustのgit2-rsは以前触ったことがあった（＋もちろん、速度と最終ビルドバイナリのサイズ感への期待もあった）ので、Rustのaxumをフレームワークとして使い、その中でミニマルなgit操作を行うことにしました。

このミニミニバックエンドは200行に満たないので、興味のある方はリポジトリを見てみてください。基本的にはAPIのパスを用意し、そこで`POST`と`DELETE`のリクエストを受けつけるだけです。

git2-rsの素晴らしいところは、Rustのエラーハンドリングの恩恵を受けられるだけでなく、**feature-gate**で機能を限定してインポートできる点です。  
デフォルトではopenssl-sysをはじめとしたネットワーク周りのクレートに依存してしまうため、それなりのサイズになってしまうのですが、`git pull`や`git push`相当のリモートリポジトリとのやりとりを行わない（操作範囲をローカルにおさめる）場合は
```
git2 = { version = "0.17.2", default-features = false }
```
このように`default-features`を`false`にしておけば、依存関係を最小限に抑えられます。

さらにベースのイメージにalpineを採用し、
```
FROM rust:1-alpine3.18 as builder
WORKDIR /carbon-builder
COPY . .
RUN apk update && apk add --no-cache musl-dev
RUN cargo build --release --locked

FROM alpine:3.18
WORKDIR /carbon-server
COPY --from=builder /carbon-builder/target/release/carbon-server . 
ENV RUST_LOG info
EXPOSE 8080
ENTRYPOINT [ "./carbon-server" ]
```
このような構成にすると、compressed sizeで5.54MBと、めちゃくちゃ小さいマイクロサービス（？）が完成します。

## コンテナサイズの比較
トータルでのサイズ感を見てみましょう。

- nodegitを用い、すべてSvelteKit内で書いた場合　…　774.03 MB
- git操作を上記のように疑似マイクロサービスに切り出した場合　…　フロントエンド 108.82 MB / 疑似マイクロサービス 5.54MB

最初はコンテナの数を増やすことでブロートなものが出来上がってしまうのでは、と心配していましたが、めちゃくちゃいい開発体験が得られました。  
libgit2のように、feature-gateで依存パッケージを限定して使うことができるライブラリは他にもあるはずです。そのような場合、JS/TSで全部書かないといけない、という意識をいったん脇において、マイクロサービス的に切り出すことを検討してみるとよいかもしれませんね。
