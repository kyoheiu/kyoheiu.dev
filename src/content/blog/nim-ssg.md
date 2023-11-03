+++
title = "Nimで静的サイトジェネレーターを実装する"
date = 2021-02-02
math = false
[taxonomies]
categories = ["code"]
tags = ["Nim", "Static Site Generator"]
+++
Rust製の静的サイトジェネレーターZolaでスクラッチからテーマを自作したことで、静的サイトジェネレーターそのものに興味が出てきた（以下、「ジェネレーター」と略す箇所が多々あります）。  
そこで調べてみて初めて知ったのだが、実は世の中には無数といっていい数の静的サイトジェネレーターがある。

[Static Site Generators - Top Open Source SSGs | Jamstack](https://jamstack.org/generators/)

このページでは、GitHubのスターが多い順に322ものジェネレーターをリストアップしている。Next.js、Hugoに始まり、見たこともないジェネレーターも上のほうにけっこうあったりする。  
中には、同じ言語・同じテンプレートエンジンで作られているものもある。たとえば[Pytyon, jinja2]の組み合わせはちょっと数えただけでも10以上ある。それぞれ実装している機能が異なるのだろうし、使い勝手も違うのだろうと思うが、それにしても静的サイトジェネレーターの機能というのはコアの部分はシンプルなはずなので、「ジェネレーターがたくさん作られている」というこの現象は面白い。  
なぜなのか、少し考えてみたけれど、まず触っていて気持ちがいいというのは大きいと思う。バッとビルドすれば自分のホームが完成する。こうなるだろうと思ったところから外れることはほとんどない。それでいて、成果物は自分好みのページになっている。これは楽しい。  
そして仕組みも、いじっているうちにだんだんわかってくる。テンプレートがあって、マークダウンのファイルがあって、組み合わせて…と、なんだか自分で作れそうな気持ちが湧いてくる。そんな風にして、すでに存在しているジェネレーターと機能は被っている（あるいは場合によっては劣っている）としても、みんなジェネレーターを作ってみたくなるんじゃないだろうか。

僕も実装してみたところ、ざっくりしたプリミティブなジェネレーターが出来たので、紹介してみたい。

[Kyohei Uto / Casa · GitLab](https://gitlab.com/kyoheiu/casa)

今回は、ただジェネレーターを実装するだけでなく、若い言語Nimを触りながら何かを作ってみる、という狙いもあった。  
ちなみにNim製の静的サイトジェネレーターはすでに存在しているし、機能も今のところそちらのほうがずっと多い。

### なぜNimなのか

ジェネレーターを作るとして、言語の縛りはない。というかむしろ、自分の好きな言語／テンプレートエンジンでジェネレーターを実装する、というところが楽しいはずだ。  
最初に検討したのはHaskell。Pandocがあるということ、自分がある程度慣れた言語であるということ、Haskell製のジェネレーターHakyllは公式のテーマリストが長らく更新されていないこと、が理由だったのだが、これは厳しかった。最近触る機会がなかったというのもあるけれど、やっぱりHaskellは難しい。Haskellは好きだけど、今回はできればあまり血と涙と時間を費やしたくなかったので、他の言語を検討することに。

一方でなるべく新しい言語に触れたいという気持ちがあって最近ドキュメントを読んでいたのがJuliaとNimだったが、どちらかというとNimのほうが実行まわりで個人的に相性がよさそうだな…というくらいの感じで、Nimでジェネレーターを作ることに決めた。後述するがNimには言語付属のテンプレートエンジンがあり、これが実にサイトジェネレーター向けの仕様だった。

### 構成

```
.
├── casa
├── casa.nim
├── config.json
├── content
│   ├── 1
│   │   ├── 1.json
│   │   └── 1.md
│   ...
├── css
├── public
└── templates
```

全体のフローは非常にシンプルで、contentフォルダに対してforループをまわし、markdownファイルをパースしつつjsonで書いた各記事の設定ファイルを読み込んで、記事ページ、ランディングページおよびタクソノミーのテンプレートに必要な変数を渡す、という流れになる。

テンプレートについては、Nim付属のSource Code Filtersと呼ばれるテンプレートエンジンを使った。たとえば各記事ページのテンプレートを用意したい場合は、こうなる。

```
#? stdtmpl(subsChar = '$', metaChar = '#')
#proc generatePageHtml(siteTitle, siteUrl, pageContent, pageDate, pageTitle: string, pageCategories, pageTags: seq): string =
#  result = ""
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
    <title>
      $pageTitle | $siteTitle
    </title>

  <link rel="shortcut icon" type="image/png" href="$siteUrl/static/image/icon.png">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link id="style" rel="stylesheet" type="text/css" href="../../main.css">
</head>

<h2>
  $pageTitle
</h2>

<div class="date">
  $pageDate
</div>

#for category in items(pageCategories) :
  <a href="$siteUrl/categories/$category">/$category</a>
#end for

#for tag in items(pageTags) :
  <a href="$siteUrl/tags/$tag">#$tag</a>
#end for

<p>
  $pageContent
</p>

<div class="footer">
  <a href="$siteUrl">$siteTitle</a> | built in Nim
</div>
```

SCFのテンプレート内では、#を文頭につければNimのコードを動かせる。このMetaCharは自由に変更可能なので、#をテンプレート内の文頭で使いたいときは、たとえば+なり@なりを設定すればいい。ただし１行目の#?だけは変更不可なので注意して!!  
これにpage_base.nimfと名前をつけ（拡張子は自由だがコンベンションとして.nimfが推奨されている）、.nimファイル内でincludeした上で、テンプレート内の関数を呼び出す。

```
import markdown, ...

include "templates/page_base.nimf"
...

let pageHtml   = generatePageHtml(siteTitle, siteUrl, pageContent,...
```

これでHTMLファイルとして生成できる。今の設定で生成できるpublicディレクトリの内容は以下の通り。

```
.
├── categories # サンプルとして色名をカテゴリに
│   ├── blue
│   ...
│   └── yellow
├── content # 1から100までのサンプル記事
│   ├── 1
│   ...
│   └── 100
├── index.html
├── main.css
└── tags　# サンプルとして色名をタグに
    ├── blue
    ...
    └── yellow
```

ただしjinja2やTera Templateにおけるextendsのような拡張機能はまだ実装されていないので、各テンプレート毎に一から実装する必要がある、というのは難点といえば難点。headerやfooterをいじるとき、ちょっと面倒かも。  
また、設定ファイルをいじったとき、ビルドし直さないと反映されない。  
さらに、静的サイトジェネレーターというのはしばしば、サイト全体の設定ファイルに自前の変数を追加し、各テンプレートで使用する…ということをやるわけだが、このSCFを使う場合は、そもそもNimのコードから書き直して実装しなければならない。ここまでくると、お世辞にも手軽なテンプレートエンジンとは言えなさそう。その意味でも、HugoやZolaの拡張性の高さ・自由度は本当にすごいと思う。

### パフォーマンス

現在自分が使っているRust製ジェネレーターのZola、そして以前使っていたHugoと、自作ジェネレーターCasaのパフォーマンスを比較してみる。サンプルとして作成した100記事からなるサイトを生成するのにかかった時間は以下の通り。

Casa（リリースビルド）|	Casa(通常ビルド) |Zola | Hugo
:---: | :---: |:---: |:---:
0.220s | 0.600s | 0.094s | 0.101s

ちなみに、ジェネレーターの草分け的存在・Jekyllは、 [Hugo vs Jekyll: Benchmarked | Forestry.io](https://forestry.io/blog/hugo-vs-jekyll-benchmark/) こちらの記事によると100記事で3〜4s程度。

ただし、サンプルに用いたファイルはわずかなmarkdownパースしか必要としない。複雑なmarkdownファイルを使うと、Zola/Hugoへのビハインドはもっと大きくなる。

ちなみに最初はさらに遅かったので、設定ファイルの形式を変更した。元々はZolaにならってmarkdownのテキストデータと各記事のフロントマター（toml形式）を１つのファイルに同居させ、あとでsplitしてそれぞれを読み込む…ということをしていたのだが、このsplit周りのコードがかなり汚くて微妙だったのと、パフォーマンス的にこの辺で時間を食ってそう、という感じがあったので、割り切って本文のmarkdownファイルとjsonファイルは分けて作る形に切り替えた。これでビルド時間を半減。

markdownパーサはnim-markdownを使用。パフォーマンスのボトルネックがこのパーサなのでどうにかできるといいのだが、現状、Nimのパッケージライブラリにあるmarkdownパーサが実質的にはnim-markdownしかない。とりあえず高速化はここまで。  
とはいえ、当然markdownファイルのパース以外にも色々処理をしているわけなので、全体としてNimが確かに速いということは実感できた。正直ここまでとは思っていなかった。まだコードの内容も未熟だから、きっともっと速くできる。  
（ついでに言うと、やっぱりZolaはHugoよりもちょっとだけ速そうな気配）

### Nim雑感

以前小さなスクリプトを書いたときに「素直な言語」という手応えを得たが、今回ジェネレーターを実装したことで、ただ単に素直なだけではない、「実直でパワフルな言語」という認識に変わった。コードの書き心地がとてもシンプルで、書いたことがそのまま反映されるし、しかも速い。forループをぶん回しても涼しい顔をしている。ライブラリのさらなる充実に期待（どこかでmarkdownパーサを書いてみたい…）。