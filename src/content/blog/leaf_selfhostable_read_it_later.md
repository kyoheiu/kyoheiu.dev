+++
title = "leaf - self-hostable read-it-later app"
date = 2023-03-20
math = false
[taxonomies]
categories = ["code"]
tags = ["Rust", "Nextjs", "selfhosted"]
+++

## はじめに
みなさん、「あとで読む」サービスは何を使ってますか？  
技術系のブログやZennのような投稿サイト、もちろんそれ以外にも、インターネットには読み応えのある記事がたくさんあるので、「あとで読む」サービスを使っている方は多いと思います。  
僕がもう何年も使っていたのは[Instapaper](https://www.instapaper.com/)です。WEBでもスマートフォンのアプリでも読める便利さ、ブラウザの拡張機能によりワンクリックでページを保存できる手軽さ、進捗状況を保存してくれるありがたさ、かゆいところに手のとどく素晴らしいサービスだと思います。  
ただ、記事を分類するフォルダ機能はやや使い勝手が悪く、全文検索はプレミアム会員でないと使用できない。さらに全文検索は会員になった直後は動かず、数日してインデックスされるようで、先日どうしても読み返したかった記事を把握するのに時間がかかってしまいました。  
そんなこんなでもうちょっとどうにかできないかな、と考えていたときふと思いついた、「自分で作ればいいんじゃない？」
というわけで、作りました。

[https://github.com/kyoheiu/leaf](https://github.com/kyoheiu/leaf)


セルフホストする「あとで読む」WEBアプリです。  
今回はこちらの開発について、記録がてら書いていきます。

くわしく書くこと：
- セルフホストアプリとは
- 技術選定プロセス
- puppeteerとrust_headless_chromeの比較

書かないこと：
- フロントエンドの細かい実装
- RustでのWEBサーバーの作り方

## セルフホストアプリとは
現在「個人開発」と言うと、スケーラブルでマネタイズも視野に入れた野心的なマネージドWEBサービスか、さもなくば自分で使うユーティリティ的／効率化用途の小さいプログラムを指すことが多いように思いますが、「開発」はもっと多様なはず！
世界には「セルフホスト」というジャンルがあります。  
詳しくは[r/selfhosted](https://www.reddit.com/r/selfhosted/)を眺めてもらえばつかめると思いますが、要するに、ポピュラーなサービス（その多くはWEBベースで中央集権的であり、ビッグテックが提供するもの）がどんどん人を集めていく中、それに対するオルタナを個人／小規模チームで作ったり自分で使っていくムーブメント／人々のことです。

有名どころでいうとたとえばメディア管理アプリの[Jellyfin](https://jellyfin.org/)やパスワード管理の[vaultwarden](https://github.com/dani-garcia/vaultwarden)などがあります。なかにはtodoアプリの[Vikunja](https://vikunja.io/)のように、マネージドとセルフホスト版両方を提供して、マネージドのほうで収益を得るような形のものもあり、野心的な人はおおむねこちらを目指してOSSをスタートさせる傾向にあります。これはいわゆる「個人開発」の世界にかなり近い立ち位置ですね。  
でも多くの人は当然ながらそこまで到達はできず（せず）、ごく小規模でアプリ開発を続けています。  
ちなみに今はほとんどのアプリがdockerコマンド一発で立ち上がるように作られているので、その気になれば導入もかんたんです。

世界には様々なマネージドサービスがあるのに、なぜそんな面倒なことをするのか？

- 自分のデータは自分で持ちたい
- 自分のサーバーを充実させていくのが楽しい
- 自分好みのアプリを作るのが楽しい

と理由は様々だと思いますが、基本的には「自由」で「楽しい」からやっている人が多いのかな、という印象です。このあたりのフレーズや「DIY」みたいな言葉にピンとくる人はぜひ界隈を覗いてみてください。

今回のアプリも、マネージドで収益化を狙っているかというと全然そんなことはなく、とにかく「自分用」を追求して作ったものなので、他の人がどんどん使ってくれるかというとたぶんそんなことにはならないでしょう。それでもあえて紹介するのは、

- セルフホスト界隈がもっと広がって多様になってくれると嬉しいから
- 実装が大変だった部分を記録しておきたいから

といったあたりが理由です。

cf:
[https://github.com/awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)

## Instapaperのオルタナを作る
このあたりで話を「あとで読むアプリ」に戻します。

今回はInstapaperをもっと自分にとって使いやすいものにしたいという発想からスタートしているので、当初のイメージは以下の通りでした。

- セルフホストするWEBアプリケーションとして作成する。
- WEBページをURLで保存し、仮に元ページが消失しても（少なくともテキストだけは）あとで読めるようにする。
- 保存されるテキストは、ADやサイドメニュー、フッターなど余計なものを取り除き、極力シンプルでかつ自前で設定したCSSを適用した形で読めるようにする。
- どこまで読んだかをアプリ側で保存し、デバイスが変わっても最新の位置から読み始められるようにする。
- Instapaperでは有料機能だった全文検索をデフォルトで実装する。
- ディレクトリ構造でなく、タグ付けによって記事を管理する。
- 可搬性を重視する。

他に細かい仕様はもっとたくさんあるのですが、要するに「Instapaperでできていることは原則としてできるようにしつつ、自分好みにカスタマイズしたい」ということです。

１点、Instapaperで実装しているけれど自作アプリでは実装していない機能として、ハイライト機能があります。  
これは読んでいる最中にテキストをハイライトでき、そのハイライトは保存されてあとで見返すことができる、というものです。  
実装していない理由は、

- 個人的に一度も使ったことがなかったこと
- ノートテイキングの機能は「読む」アプリからは分離していたほうがよさそうだと感じたこと
- 実装が大変そうだったこと

の３点です。よく言えばUNIX精神です。

## 進め方

さて、自前で実装しようと言っても、具体的にどうすればいいのかはリバースエンジニアリングをするしかありません。とかっこよく言いましたがオープンソースでもないWEBサービス、大したことは調査できないので、地道にブラウザコンソールのログを読んでいきます。  
たとえば記事の進捗状況を保存する仕組みですが、これはログを見れば一目瞭然で、スクロールごとにHTTPリクエストを送っていることがすぐわかりました。とすると、クライアントサイドでイベントリスナーを設定しているのでしょう。  
といった具合に、「たぶんこうなっているだろう」「ここはこういう実装でなんとかなるだろう」を積み重ねていきつつ、

1. バックエンドの設計
2. フロントエンドの実装
3. ドッグフーディングによるデバッグ、改善

おおまかにはこの順序で進めていきました。

時系列としては、

```
１月１日　Initial commit
１月中旬　バックエンドがほぼ完成
　　　　　ここからフロントエンドの長い旅が始まる
２月中旬　VPSにデプロイ、以降ドッグフーディング
```

といった感じです。

## 技術スタック

次に、現在使用している技術スタックの概要です。

![](https://storage.googleapis.com/zenn-user-upload/568785f20247-20230401.png)

上記のアーキテクチャの通りですが、フロントエンドにNext.js。バックエンドにRust（axum）を使い、データベースはSQLiteを採用しています。  
たとえば記事取得時の流れとしては、

1. フロントエンドでURLを入力
2. Next.jsのAPIルートからaxumの`POST /articles`へHTTPリクエストを送る
3. axum内でheadless-chrome経由でchromiumを立ち上げ、ページ遷移してHTMLコンテンツを取得
4. mozilla/readabilityベースのコンテンツ抽出アルゴリズムで極力「記事本文」に近いHTMLをはき出す
5. ammoniaでHTMLをサニタイズ
6. SQLiteに記事本文、URL、カバーイメージURLなどを保存

となります。  
このように、現在は基本的にデータの処理はすべてバックエンドで処理する形をとっていますが、この構成に落ち着くまでには色々と試行錯誤がありました（後述）。

### バックエンド
前述したように当初から全文検索は実装したいと思っていたため、以下の条件でライブラリを探します。

- なるべく高速で処理できる
- サーバー型ではなくスタンドアローン

１つめはいいとして、２つめについては、次のデータベースのチョイスとも関連してきますが、こだわりといえばこだわりの部分です。  
基本的に世で使われている全文検索エンジンというのはサーバー型が多いです。ElasticsearchやApache Solrなど、有名OSSはだいたいこの形です。  
今回サーバー型を採用しなかったのは、「可搬性」を重視したかったためです。前述しましたが、あえてInstapaperなどの企業サービスを使わずわざわざセルフホストなんていう面倒なことをする理由のひとつは、やはり自分でデータを管理でき、場合によっては持ち運べる、というメリットがあるからです。  
（特に今使っているVPSはなかなかの低スペックなので、引っ越しする可能性が高いということもありました）  
持ち運ぶ＝別のサーバーに移しやすくする、ということを考えたとき、ローカルのディスクにデータがあり、コピーするだけですぐ移せるスタンドアローンのメリットは非常に大きいです。

上記の条件で探したところ、Rustで実装されている[tantivy](https://github.com/quickwit-oss/tantivy)というクレートを見つけました。これはまさに条件を満たす理想的なライブラリで、現在進行系で活発に開発されているのも魅力的だったので、これを採用することに決めました。  
そうすると当然バックエンド全体もRustで、ということになるので、今まで何度か使ってきて慣れているaxumをサーバーフレームワークとして採用。

### データベース
上記したとおり可搬性を重視するとなると、選択肢はほぼ１択でsqlite以外はない、という感じになりますが、ここはやや迷いがありました。というのは、セルフホスト勢が使っているアプリケーションはPostgreSQLを採用しているケースがかなり多いので、ユーザーが自前のPostgreSQLのポートを指定してそこにストアするように設計するということも使用感を考えるとアリではあったからです。  
最終的にsqliteを選んだのはやはり可搬性と導入のしやすさ、そしてそのシンプルさを評価してです。シンプルであるということは、特に開発時のスピード面で大きくプラスであるように今も思います。  
ちなみにRust実装でsqlite-ishに使用できるデータベース（[BonsaiDB](https://github.com/khonsulabs/bonsaidb)）もあるのですが、挑戦的なチョイスも許される検索ライブラリとは違い、ここは絶対に堅牢でないといけなかったので、その意味でもsqliteは強かったです。

### フロントエンド
ここが一番迷走した部分で、正直な話ちゃんと動けばどのフレームワークでもいいのですが、その分どれを使うべきか決め手がない、という状況でもありました。特に僕自身フロントエンドには苦手意識があり、なるべく楽をしたいという気持ちがある一方で、どうせオレオレアプリを作るんだから新しめのフレームワーク／概念を試したいという欲もあり、この２つの間で揺れ動いた結果選定に非常に時間がかかってしまいました。  
試したフレームワークとしては順番に

- （そもそもサーバーサイドでテンプレートエンジン（tera）を使う）
- Deno Fresh
- SvelteKit
- Next.js

という感じで節操もなにもあったものではなかったのですが、最終的にはNext.jsに落ち着きました。

- （そもそもサーバーサイドでテンプレートエンジン（tera）を使う）　→　ふつうに動くものは作れたがさすがにつらい
- Deno Fresh　→　クライアントサイドの処理がうまく動かなかった
- SvelteKit　→　Get startedがうまく動かなかった

Next.jsは単純に流通している情報量が非常に多く、詰まったときもissueやSOを見ればなんとかなることが多い（なんとかならないこともある）のが魅力です。またエコシステムも整っていて、組み合わせられるライブラリも豊富なのがありがたかったです。特に今回はユーザー認証をクライアントサイドで完結させることにしたので、Next.jsの強さを実感しました。ただ、middlewareなど最近実装された機能は若干バグい印象も。

### コンテンツ取得にはpuppeteer？
WEBページのコンテンツを取得する…というとき、ふつうにHTTPリクエストでGETできるページとできないページがあります。SPAサイトなどはこれではまったくうまくいきません。ということで、「ブラウザのふりをしてコンテンツを取ってくる」ライブラリが必要になってきますが、どれを使えばいいのでしょうか？  
第一候補はGoogle製のnode.jsライブラリであるpuppeteerです。ある意味お膝元であるだけに、Chromeへの追従スピードも早いですし、OSSとしての規模が大きいのでトラブルシューティングもしやすい。  
実際僕も当初はpuppeteerを使って、

1. フロントエンドでURLを入力
2. Next.jsのサーバーサイドでpuppeteerを立ち上げ、コンテンツを取得
3. Next.jsのサーバーサイドでmozilla/readabilityを呼び出し、コンテンツ本文を抽出
4. コンテンツ本文など一式をaxumに送り、ammoniaでHTMLをサニタイズ
6. sqliteに記事本文、URL、カバーイメージURLなどを保存

というフローを組んでいましたし、これでなんの問題もありませんでした。もちろんmozilla/readabilityもこなれています。  
ではなぜ現在のように、コンテンツ取得・抽出もサーバーサイドで行うように切り替えたのかというと、理由は２つあり、

- 最終のDockerイメージに含まれるnode_modulesの大きさがつらい
- なるべくRustで処理したい

１つめについては、自分が使っているVPSが貧弱なため、なるべくコンテナイメージをスリムにしたいという意図があります。２つめについては完全に自己満足です。  
結果から言えば現在のフローで問題なく動いていますが、他人にはあまりおすすめできないチャレンジでした。

#### headless_chromeについて

[headless_chrome](https://github.com/rust-headless-chrome/rust-headless-chrome)はRust実装のChrome/Chromium操作ライブラリで、Node.jsにおけるpuppeteer、という位置づけです。現在はこのライブラリをバックエンドで使用していますが、いくつか注意すべきポイントがあります。

まず、headless_chromeは最近v1がリリースされたばかりであり、また開発者の規模もやはりpuppeteerとは比べ物にならないので、不安定な部分があったり、ChromeのAPIすべてには対応できていないという点は重要です。今回のアプリケーションでは、シンプルにページのコンテンツ＝HTMLさえとって来れればOKだったため問題なくワークしていますが、もっと細かい作業が必要な場合は注意したほうがよさそうです。

また、Rust製のheadless_chromeにしたからといって、ページコンテンツをとってくるのが早くなるわけではありません。

##### ベンチマーク（Node.js / Rust）

###### Node.js + puppeteer sample
```js
#!/usr/bin/env node

import puppeteer from "puppeteer";

const main = async () => {
	let content;
	const url = "https://kyoheiu.dev";
	const browser = await puppeteer.launch({
		executablePath: "chromium",
		headless: true,
		args: [
			"--disable-gpu",
			"--disable-dev-shm-usage",
			"--disable-setuid-sandbox",
			"--no-sandbox",
		],
	});
    const page = await browser.newPage();
    await page.goto(url);
	content = await page.content();
    console.log(content);
	await page.close();
	await browser.close();
	return;
};

await main();
```

```
λ hyperfine "node index.mjs"
Benchmark 1: node index.mjs
  Time (mean ± σ):     558.6 ms ±  23.0 ms    [User: 264.0 ms, System: 51.5 ms]
  Range (min … max):   522.9 ms … 603.4 ms    10 runs
```

###### Rust + headless_chrome
```rust
use headless_chrome::{Browser, LaunchOptionsBuilder};

const CHROME_ARGS: [&str; 4] = [
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--no-sandbox",
];

fn main() -> Result<(), anyhow::Error> {
    let url = "https://kyoheiu.dev/";

    let option = LaunchOptionsBuilder::default()
        .sandbox(false)
        .path(Some(std::path::PathBuf::from("/usr/bin/chromium")))
        .args(
            CHROME_ARGS
                .iter()
                .map(|x| std::ffi::OsStr::new(x))
                .collect(),
        )
        .build()
        .unwrap();
    let browser = Browser::new(option)?;

    //Scrape by headless_chrome
    let tab = browser.new_tab()?;
    tab.navigate_to(url)?;
    tab.wait_until_navigated()?;
    let content = tab.get_content()?;
    println!("{}", content);
    tab.close(true)?;
    drop(browser);
    Ok(())
}
```

```
λ hyperfine "./headless_chrome_sample"
Benchmark 1: ./headless_chrome_sample
  Time (mean ± σ):      2.875 s ±  0.244 s    [User: 0.091 s, System: 0.032 s]
  Range (min … max):    2.535 s …  3.155 s    10 runs
```

###### Node.js for loop x10
```js
...
	for (let i = 0; i < 10; i++) {
		const page = await browser.newPage();
		await page.goto(url);
		content = await page.content();
		console.log(content);
		await page.close();
	}
...
```

```
λ hyperfine "node index.mjs"
Benchmark 1: node index.mjs
  Time (mean ± σ):     909.3 ms ±  61.2 ms    [User: 433.9 ms, System: 133.6 ms]
  Range (min … max):   849.4 ms … 1039.7 ms    10 runs
```

###### Rust for loop x10
```rust
...
    for _i in 0..10 {
        // Scrape by headless_chrome
        let tab = browser.new_tab()?;
        tab.navigate_to(url)?;
        tab.wait_until_navigated()?;
        let content = tab.get_content()?;
        tab.close(true)?;
        println!("{}", content);
    }
...
```

```
λ hyperfine "./headless_chrome_sample"
Benchmark 1: ./headless_chrome_sample
  Time (mean ± σ):     24.174 s ±  0.211 s    [User: 0.192 s, System: 0.182 s]
  Range (min … max):   23.999 s … 24.687 s    10 runs
```

`/usr/bin/time`によるベンチマーク

| Tested Command               | node index.mjs | ./headless_chrome_sample | node index.mjs | ./headless_chrome_sample |
|------------------------------|----------------|--------------------------|----------------|--------------------------|
| User time (seconds)          | 0.30           | 0.07                     | 0.43           | 0.19                     |
| System time (seconds)        | 0.03           | 0.04                     | 0.11           | 0.17                     |
| Percent of CPU this job got  | 57%            | 4%                       | 62%            | 1%                       |
| Elapsed (wall clock) time    | 0:00.57        | 0:02.68                  | 0:00.88        | 0:22.89                  |
| Maximum resident set size    | 198696         | 195100                   | 196836         | 195444                   |
| Minor page faults            | 22445          | 10813                    | 28689          | 12031                    |
| Voluntary context switches   | 2152           | 1405                     | 9577           | 7925                     |
| Involuntary context switches | 8              | 9                        | 50             | 22                       |
| Page size (bytes)            | 4096           | 4096                     | 4096           | 4096                     |
| Exit status                  | 0              | 0                        | 0              | 0                        |


ベンチマークの結果としては、

- Rustはやたら時間がかかる
- そのわりにはCPU使用率は優れている
- 最大メモリ消費量はほぼ変わらず
- 最重要課題がなにかによって使い分けることはできそう

といった感じです。  
今回はどちらかというと速度よりもVPSのCPU使用率を省エネしたかったので、やはりRustにしてよかった…のかもしれません。ただ、CLIで動かすのと、Next.jsに組み込まれた形で動かすのでは様々な数値が異なってくるとは思うので、あくまでも参考数字です。

#### コンテンツ抽出について
個人的に一番つらかったのはここで、Node.jsにはmozilla謹製の[readability](https://github.com/mozilla/readability)というライブラリがある一方で、Rustにはそれに完全準拠したライブラリがない…というのが問題でした。

readabilityというのは、ブラウザにおいていわゆるreader viewを提供するライブラリで、歴史をたどると[arc90という企業（？）が作ったもの](https://ejucovy.github.io/readability/)に端を発しているようです。mozillaはこれをフォークしてスタンドアローン版を作り、Firefox内で使っています。

ここで注意しないといけないのは、世の中のreadabilityライブラリがどちらの実装なのかということです。arc90版の実装もいくつかあるのですが、現在のWEBページからのコンテンツ抽出の精度という点ではかなりいまいちで、本文中のコードがスキップされてしまったり、途中でテキストが切れてしまったりということはざらです。  
Rustでおそらく一番使われているのは[kumabook/readability](https://github.com/kumabook/readability)ですが、これはarc90実装なのでうまくいかないケースがかなりある、ということにやや経ってから気づかされました。

これが足かせになって最初はpuppeteer + mozillaで組んでいたのですが、「いや、自分で実装できるのでは？」と思い直し、mozilla実装を書いてみよう…となったのが３月の中旬。そこからのmozilla実装（当然JavaScript）とのにらめっこがハードでした。読み込んでみればしっかり書かれた良質なコードなのですが、JavaScriptが苦手な自分にはつらい。そしてRustでNodeを操作するのがまたつらい。  
そんな折、[nipper](https://github.com/importcjj/nipper)というクレートのサンプルコードに途中まで実装されたものがあるのを発見し、それを修正する形でなんとか稼働までこぎつけた…というのが今の状況です。非常に勉強にはなりましたが。

ちなみに、[mozilla実装のクレート](https://github.com/readable-app/readability.rs)もあるのを後日見つけたのですが、若干仕様が現在のmozilla版と異なる箇所もありました。ただこのクレートの完成度は非常に高いので、今からreadability的なライブラリを使いたいという方には圧倒的にこちらをおすすめします。

RustでのNode Tree操作のつらさを隠蔽するためにnipperやkuchikiなどのクレートがあるにはあるのですが、基本的にこういう作業はもしJS/TSで行えるのであれば無理にRustでやらなくてもいい、というのが実感です。

##### ベンチマーク（readability）

ちなみに、puppeteer + mozilla/readabilityと、headless_chrome + 自作readabilityの比較はこちら。

| Statistic | Node index.mjs | ./headless_chrome_sample |
| --- | --- | --- |
| Command being timed | "node index.mjs" | "./headless_chrome_sample" |
| User time (seconds) | 0.57 | 0.10 |
| System time (seconds) | 0.08 | 0.01 |
| Percent of CPU this job got | 85% | 4% |
| Elapsed (wall clock) time (h:mm:ss or m:ss) | 0:00.76 | 0:02.72 |
| Maximum resident set size (kbytes) | 197020 | 197220 |
| Major (requiring I/O) page faults | 5 | 0 |
| Minor (reclaiming a frame) page faults | 41363 | 11065 |
| Voluntary context switches | 2501 | 1463 |
| Involuntary context switches | 25 | 9 |
| Page size (bytes) | 4096 | 4096 |
| Exit status | 0 | 0 |

コンテンツ抽出プロセスの分はわずかにRust版のほうが早いかもしれません。Rustのほうは単体／統合それぞれについてまだ最適化の作業をしていないので、フロー全体で見たときもうちょっと巻ける可能性はありそうです。

## デプロイ環境

さくらのVPSで

- 石狩第1ゾーン
- SSD 50GB
- 仮想2Core
- 1GB メモリ
- スワップ2GB

これで動いています。スワップがないと、重い記事（ITメディア系のページなど）ではハングします。

自作アプリのいいところは、どの箇所でどれくらいコンピューティング資源を使うかが肌感でわかっていること、自分の環境に合わせて最適な仕様にしていけることですね。

ちなみにご多分にもれず`docker-compose.yml`で管理しているので、もし興味のある方はリポジトリのInstall to your server欄を見てみてください。

## セルフホストは最高

と、長々とこだわりの部分について書いてきましたが、自分の好きな技術と好きなレイアウトを使って自分が普段遣いするアプリを作るのは「最高！」の一言に尽きます。皆さんもぜひ、好きなものを好きな技術で作って世界を豊かにしてきましょう。
