+++
title = "[Rust]依存関係にGitHub等のURLを指定している場合はcargo publishに注意しよう"
date = 2023-01-19
math = false
[taxonomies]
categories = ["code"]
tags = ["Rust", "cargo", "github"]
+++

## TL;DR
- Cargo.tomlのdependenciesセクションでは、crates.ioに上がっているパッケージ以外にGitHub等のURLを指定できる
- 上記のような記述をした場合、手元でビルドする分には何の問題もないが、crates.ioにpublishしたときはそのURLは無視され、自動的にcrates.io内部の同名のクレートを使ってビルドされる（名称がcrates.io内にあるパッケージと一致しない場合はエラー）
- 対処法は限定的なので注意しよう

## 何の話
上記の通りですが、自分でも気づかないうちにcrates.ioの仕組みにハマっていたので共有しておきます。  
一昨年の10月ごろから作っている[自作ファイルマネージャ](https://github.com/kyoheiu/felix)をcrates.ioから`cargo install`コマンドでインストールできるように、crates.ioへpublishしているのですが、そのパッケージの依存関係が自分の意図したものとは違う形でpublishされてしまったという話です。

## 文脈
具体的な実装と依存関係については本題ではないのでさらっと流しておきますが、ざっくり言うと、ファイルマネージャ内で実装しているテキストファイルのプレビューにおいてシンタックスハイライトをapplyする際に使っている`syntect`というクレートがあるのですが、そのクレート内の関数がマルチバイト文字に対応しておらず、場合によってはpanicしてしまうというものでした。

これについては発見時にPRを送っており、現在すでにmergeされていますが、まだリリースはされていないという状態です。いつかリリースされるでしょう…。

ともあれ上記のような仕様だったため、マルチバイト文字の言語の人間としてはそのまま使い続けるわけにはいかず、フォークしてパニックを起こさないように修正したものを下記のように明記してパッケージ内で使用していました。

```
[dependencies]
...
syntect = {version = "5.0.0", git = "https://github.com/kyoheiu/syntect"}
```

手元では当然問題はなかったので安心していたのですが…
先日、issueを立ててくれた方がいました。

[https://github.com/kyoheiu/felix/issues/169](https://github.com/kyoheiu/felix/issues/169)

まさに上記のpanicに引っかかった、というレポートでした。正直最初は原因がさっぱり分からず頭をひねっていたのですが、インストール経路がcrates.ioからの`cargo install`だったということで調べてみたところ、冒頭に書いた仕様に気づくことができました。

やや関連するcargoのissueはこちら。

[https://github.com/rust-lang/cargo/issues/6738](https://github.com/rust-lang/cargo/issues/6738)

> You cannot publish a crate that relies on git dependencies.

マジ？と思いましたがマジでした。  
**crates.ioにpublishするクレートが依存するパッケージは、同様にcrates.ioにpublishされていなければならない。**  
これがcrates.ioの条件ということでした。

最初はやや理不尽な印象を受けましたが、考えてみると合理的ではあります。依存パッケージがいつの間にか消失している可能性があると、ユーザーは困ってしまいます。crates.ioの管理下にはないGitHub上のリポジトリはいつ消えてもおかしくありません。一方、crates.ioのクレートは一度publishすると原則として削除することが**できません**。したがって、依存パッケージの消失の恐れも（原則的には）なく、安心して使えるパッケージ群をユーザーに提供できるというわけです。

しかしこの制約により、ちょっとした修正を加えたライブラリを使いたいというケースが非常に成立困難になります。GitHubのURLを使うようcrates.ioに伝えることができないからです。

つまりこのissueの原因は、**`cargo install`したものについてはフォーク元のクレートを参照するために、加えたはずの修正が反映されていなかった**、というものでした。

ここで話を少しややこしくしているのは、あくまでもこれはcrates.io上の仕様であって、手元では問題なく反映される、という点です。公式でも、

https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html

このように丁寧にGitHub URLを依存関係として指定する方法を紹介していますし、実際やったことのある方もたくさんいらっしゃると思います。手元でのビルドと、crates.ioへのpublishはまったく別の次元の話である、というのがこの件のキモです。

## [patch]は？
crates.ioのパッケージを手元でオーバーライドする`[patch]`というオプションは存在しています。

https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html

>The desire to override a dependency can arise through a number of scenarios. Most of them, however, boil down to the ability to work with a crate before it's been published to crates.io. For example:
> - A crate you're working on is also used in a much larger application you're working on, and you'd like to test a bug fix to the library inside of the larger application.
> - An upstream crate you don't work on has a new feature or a bug fix on the master branch of its git repository which you'd like to test out.
> - You're about to publish a new major version of your crate, but you'd like to do integration testing across an entire package to ensure the new major version works.
> - You've submitted a fix to an upstream crate for a bug you found, but you'd like to immediately have your application start depending on the fixed version of the crate to avoid blocking on the bug fix getting merged.
> These scenarios can be solved with the [patch] manifest section.

ただしこれは**ローカルでの話**で、やはりcrates.ioにpublishするパッケージには適用されないようです。上記の説明を読むとpublishするパッケージに適用できそうな雰囲気がプンプンしますが。

cf:
https://users.rust-lang.org/t/how-to-work-with-a-forked-dependency/13338/1

## どうすればよいか
実質的には２つ、方法があるように見えます。

１つめは、修正を加えたパッケージを、フォーク元とは別のパッケージとしてcrates.ioに登録し、それを依存関係として記述するというもの。  
このやり方に問題があるとすれば、「一時的にしか使用されない臨時のパッケージがcrates.ioに氾濫する可能性がある」という点ですが、もともと原則として削除できないリポジトリですから、そこは仕様、といったところでしょうか。

もう１つは、依存パッケージを自分のパッケージにmodとして含んでしまい、当該の依存については内部で完結するように構成するというもの。  
ライセンス上衝突がなければこれはこれでアリだと思いますが、パッケージが肥大化するのは避けられません。

個人的にはどちらもやりたくなかった（し、フォーク元の開発者からはレスポンスをもらえていた）ので、臨時パッケージをpublishはせず、自分のパッケージに飲み込むこともせず、忘れたことにしてアップデートを待っています。

ただ、フォーク元がすでに音信不通だったり、動きが見られなかったりした場合はつらいかもしれません。（その場合は、`cargo publish`がどうこうの前にそもそもフォークすることが検討対象になりそうですが）

以上、フォークして調整したライブラリに依存するパッケージを`cargo publish`するときは気を付けましょう、という話でした。
