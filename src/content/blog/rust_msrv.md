+++
title = "MSRV - どこまで古いバージョンを保証するか"
date = 2023-05-27
math = false
[taxonomies]
categories = ["code"]
tags = ["Rust", "msrv"]
+++

## TL;DR

* MSRVとはMinimum Supported rustc Versionの頭文字をとったもの
* MSRVはメンテナビリティとある程度のトレードオフの関係にある
* 考慮する場合はターゲットを明確にしておくべき

## MSRVとは

Rustではcargoを用いてプロジェクトの依存関係やパッケージングをマネジメントするために普段はあまり意識しませんが、コンパイラはあくまでもrustcです。MSRVとはMinimum Supported rustc Versionの頭文字をとったもので、「そのプロジェクトがどれくらい前のrustcのバージョンでコンパイルできるか」を示すものです。たとえばプロジェクトページでMSRVが1.65.0であると明言されている場合、お手元のrustcが少なくとも1.65.0以上であればそれはコンパイルできる、ということになります。

Rust >= 1.56では rust-version fieldをMSRVを示すために使うことができます。  
[https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field](https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field)

このMSRVは、通常プログラミング言語で議論されるBackward Compatibilityともちょっと違うニュアンスの概念です。RustではBackward Compatibilityはeditionという概念によって段階的に解決されている、ということになっています。

> Rust 1.0 のリリースでは、Rust のコア機能として「よどみない安定性」が提供されるようになりました。 Rust は、1.0 のリリース以来、いちど安定版にリリースされた機能は、将来の全リリースに渡ってサポートし続ける、というルールの下で開発されてきました。  
> 一方で、後方互換でないような小さい変更を言語に加えることも、ときには便利です。 最もわかりやすいのは新しいキーワードの導入で、これは同名の変数を使えなくします。 例えば、Rust の最初のバージョンには async や await といったキーワードはありませんでした。 後のバージョンになってこれらを突然キーワードに変えてしまうと、例えば let async = 1; のようなコードが壊れてしまいます。  
> このような問題を解決するために、エディションという仕組みが使われています。 後方互換性を失わせるような機能をリリースしたいとき、我々はこれを新しいエディションの一部として提供します。 エディションはオプトイン、すなわち導入したい人だけが導入できるので、既存のクレートは明示的に新しいエディションに移行しない限りは変化を受けません。 すなわち、2018 以降のエディションを選択しない限り、たとえ最新バージョンの Rust であっても async はキーワードとして扱われません。 導入の可否はクレートごとに決めることができ、Cargo.toml への記載内容により決定されます。 cargo new コマンドで作成される新しいクレートは、常に最新の安定版のエディションでセットアップされます。
> 
> [エディションとは？ - エディションガイド](https://doc.rust-jp.rs/edition-guide/editions/index.html)

エディションというのは上記のとおり、言語自体の仕様の互換性を保証する区切りです。これに対してMSRVは、もう少し細かい区切りを指すことになります。

例として、空の新規プロジェクトを立ち上げるところから見ていきましょう。

```
cargo init msrv-test
cd msrv-test
```

ここでは`cargo-msrv`という、どこまでrustcをさかのぼってコンパイルできるかをチェックしてくれるプラグインクレートを使用します。([foresterre/cargo-msrv: 🦀 Find the minimum supported Rust version (MSRV) for your project](https://github.com/foresterre/cargo-msrv))

```
$ cargo msrv
Fetching index
Determining the Minimum Supported Rust Version (MSRV) for toolchain x86_64-unknown-linux-gnu
Using check command cargo check
Check for toolchain '1.63.0-x86_64-unknown-linux-gnu' succeeded
Check for toolchain '1.59.0-x86_64-unknown-linux-gnu' succeeded
Check for toolchain '1.57.0-x86_64-unknown-linux-gnu' succeeded
Check for toolchain '1.56.1-x86_64-unknown-linux-gnu' succeeded
   Finished The MSRV is: 1.56.1   ████████████████████████████████████████ 00:00:32
```

MSRVは1.56.1と出ました。中のコードは初期状態で依存パッケージもありませんから、RustのエディションがMSRVを決めています。この場合はEdition 2021で、2021は1.56以降を範囲としているので、1.56.1と出るのは妥当ですね。（1.56.0でない理由はcargo-msrvの判定アルゴリズムによるものだと思います）

さて、ではここに、何でもいいのですがクレートを一つ追加してみましょう。

```
cargo add simplelog
cargo msrv
```

```
Fetching index
Determining the Minimum Supported Rust Version (MSRV) for toolchain x86_64-unknown-linux-gnu
Using check command cargo check

Check for toolchain '1.63.0-x86_64-unknown-linux-gnu' failed with:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ error: package `time-macros v0.2.9` cannot be built because it requires rustc   │
│ 1.65.0 or newer, while the currently active rustc version is 1.63.0             │
└─────────────────────────────────────────────────────────────────────────────────┘
Check for toolchain '1.66.1-x86_64-unknown-linux-gnu' succeeded

Check for toolchain '1.64.0-x86_64-unknown-linux-gnu' failed with:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ error: package `time-macros v0.2.9` cannot be built because it requires rustc   │
│ 1.65.0 or newer, while the currently active rustc version is 1.64.0             │
└─────────────────────────────────────────────────────────────────────────────────┘
Check for toolchain '1.65.0-x86_64-unknown-linux-gnu' succeeded
   Finished The MSRV is: 1.65.0   ████████████████████████████████████████ 00:00:03
```

おや、なんとクレートをひとつ追加しただけで、MSRVが1.65.0に上昇…bump upしてしまいました。

cargo-msrvは、「なぜ古いrustcでコンパイルできないか」も教えてくれます。ログを見ればわかるように、これはsimplelogが依存しているクレートである`time-macros`が1.65.0よりも前のバージョンではコンパイルできないからです。

また、当然ですがMSRVはプロジェクト自身のコードにも影響を受けます。  
いったん依存パッケージを取り除き、`main.rs`を次のように書き換えてみましょう。

```
fn main() {
    let name = "John";
    println!("Hello, {name}");
}
```

これでMSRVを確認してみると：

```
$ cargo msrv
Fetching index
Determining the Minimum Supported Rust Version (MSRV) for toolchain x86_64-unknown-linux-gnu
Using check command cargo check
Check for toolchain '1.63.0-x86_64-unknown-linux-gnu' succeeded
Check for toolchain '1.59.0-x86_64-unknown-linux-gnu' succeeded

Check for toolchain '1.57.0-x86_64-unknown-linux-gnu' failed with:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Checking msrv-test v0.1.0 (/home/kyohei/rust/msrv-test)                         │
│ error: there is no argument named `name`                                        │
│  --> src/main.rs:3:22                                                           │
│   |                                                                             │
│ 3 |     println!("Hello, {name}");                                              │
│   |                      ^^^^^^                                                 │
│                                                                                 │
│ error: could not compile `msrv-test` due to previous error                      │
└─────────────────────────────────────────────────────────────────────────────────┘
Check for toolchain '1.58.1-x86_64-unknown-linux-gnu' succeeded
   Finished The MSRV is: 1.58.1   ████████████████████████████████████████ 00:00:01
```

MSRVは1.58.1と出てきます。これは、`println!`マクロ内で使われている、プレースホルダーの中に直接変数名を入れる文法が1.58以降でしか使えないからです。

つまりMSRVというのは、常にプロジェクト自身、もしくは依存パッケージのMSRVに律速される数である、ということになります。

## なぜ気にするのか
自分で書いて自分で使うだけのプロジェクトの場合はMSRVなんてものは気にする必要がありません。コンパイルできた時点で手元のrustcでは動くことが確定しているので、問題がないのです。

意識するタイミングはやはり書いたものを配布するときでしょう。  
MSRVという概念によって気付かされるのは、他人の環境でプロジェクトが問題なくコンパイルできるかは、実はOSなどの環境**だけでなく**、その人がどのバージョンのrustcを使っているかにも依るということです。  
僕自身は大掛かりなライブラリをメンテしているわけではなく、主にバイナリとして実行するプロジェクトをメンテしている人間なので、その観点からMSRVを考慮すべきシチュエーションをまとめてみます（ライブラリの場合は他にも考えるべきポイントがあるかもしれません）。

### バイナリのコンパイル環境
コンパイル可能性はOSなどの環境だけに依存するのではない、と書きましたが、バイナリのコンパイル環境を考える上で、実はOSというのはわりと重要です。  
これは、rustcが各自のOSにどういう経路でインストールされるか、ということに関わってきます。  
現状、経路としては主に以下の２パターンでしょう。

- rustupを用いたインストール
- 各OSのパッケージマネージャによるインストール

rustupを使用する場合はデフォルトで自動的に最新のrustcがインストールされるので、ユーザーにとってみればMSRVはあってないようなものとなり、意識せずにどのプロジェクトもコンパイルできるはずです。  
考慮しなければいけないのは２つめの各種パッケージマネージャによるインストールの場合です（ユーザーのインストール方法をメンテナは決めることができません！）。Arch Linuxなどのローリングリリースタイプのディストロであれば、rustc自体のアップデートにそれなりのスピードで追従してくれます。現にpacmanでは23年5月27日時点で1.69.0が配布されています。しかしこうしたディストロばかりではありませんね。  
たとえばdebian stableでは、配布されているrustcはなんと1.48.0です。cargoについては0.47が配布されていますが、対応するrustcは同じく1.48前後になっているはずです。これはやや極端ですが、最新のrustcを使っているユーザーばかりではない、というのはわかると思います。

エッジィなローリングリリース／アップデートを避けてstableな環境で開発／運営したい、という需要は常に存在しており、サーバーの中身がそうした保守的なOS、というのはよくある話です。このような環境でもコンパイルできることを保証したい、というとき、MSRVはひとつの重要な指標になり得ます。

## どこまで保証するか
ただし、闇雲にどこまでも古いバージョンまで保証する、というのはバグと疲弊の元です。  
そもそもなぜMSRVがbump upするかを考えてみると、その原因は２つしかありませんでした。つまり、己のコードで新しい言語仕様を採用するか、依存パッケージが新しい言語仕様を採用するか、です。  
そして、新しい言語仕様というのは、少なくともRustの場合は、「書きやすさ」なり「読みやすさ」を意識して導入されることが多いと思います。上記のプレースホルダー内の変数はその最たる例です（ただ個人的には使っていませんが…）が、MSRVを維持したいために新しい仕様をひたすらに拒否するというのもおかしな話です。つまりメンテナビリティとMSRV維持はある程度のトレードオフの関係にある、と考えてもいいかもしれません。

メンテナビリティとの関係は依存パッケージのアップデートからも考えることができます。  
たとえば、非常に多くのプロジェクトが直接的または間接的に依存している`time`クレートは、MSRVをstable minus twoとしていく方針を決めたとのことです。（[MSRV policy is changing beginning 2023-07-01 · time-rs/time · Discussion #535](https://github.com/time-rs/time/discussions/535)）これは新しい言語仕様の恩恵を積極的に受けるためである、と説明されていますが、そのことによって結果的にバグが減り、セキュリティが確保されていくということもある…言い換えると、コードの見通しをさらによくしていくことにより、メンテナビリティを維持・向上させるという効能は確実にあるでしょう。この観点からしても、MSRVを低く維持することが目標になってはいけないと思います。

### 考慮する場合はターゲットを決めよう
もちろんトレードオフですから、MSRV=stable、とまでしなくてもよいとは思います。大事なのは、自分のプロジェクトのユースケースをある程度意識して、どれくらいの範囲を保証すれば大きな問題とならないかを決めることでしょう。  
たとえば上記のように、OSから考える、つまりユーザー環境から絞っていくという手があります。Ubuntuであれば、rustcは1.65.0が配布されており、これは十分現実的な数字だと個人的には思います。  
あるいは、言語仕様の中でこれは使いたい／これはまだ必要ない、というものを見極めてもいいでしょう。これはプロジェクト自体のメンテナビリティから考えていくパターン、と言い換えられます。  
いずれにしても、続けること、メンテナビリティは大事。場合によっては、MSRVを下げることによって得られる（かもしれない）ユーザー数／ユーザー体験よりも大事なことではないかと、個人的には思うのです。
