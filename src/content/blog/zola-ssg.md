+++
title = "静的サイトジェネレーターZolaへ移行する"
date = 2021-01-07
math = false
[taxonomies]
categories = ["code"]
tags = ["Zola", "Static Site Generator"]
+++
### 概要

以前はGo製のSSG(Static Site Generator)Hugoを使っていたのだけれど、色々考えた結果、Rust製SSGのZolaに乗り換えることに。そしていじっているうちに自分で納得いくまでやりたくなってしまい、テーマも作成してみました、という話です。

### 移行理由

HugoではAcademicという（おそらく）メジャーなthemeを使っていて、特に支障があったわけでもなかったのだけれど、気になるといえば気になっていたのが、「細かいところが気になったとき、すらすらと自分で書き直せるほどの理解を得ないまま使っている感じ」。ただしこれについては、デザインを自分で本格的にいじっていないために手になじんでいないだけかもしれない。

直接的な動機になったのは、各記事のカテゴリやタグを記事一覧でちゃんと表示してくれる、かつデザイン的に好みのthemeが見つからなかったことだったが、結果的には、Zolaに移行してテーマも自作したことで、とてもスッキリした。

### Zolaについての個人的pros/cons

#### pros

- zola buildが通ればだいたい大丈夫という安心感
- しかも早い。Hugoよりも体感的にはちょっとだけ早い気がする。
- buildエラー時のメッセージが丁寧かつ有用
  - Hugoでは何も考えずthemeを使っていたのでそもそもあまりエラーが出なかった印象だが、一から独自変数ありの.htmlを組んでいく中でこれはとても有難かった。
- zola checkがけっこう使える
  - 内部及び外部リンクをチェックしてくれるコマンドで、リンクミス・リンク切れを教えてくれる。

#### cons

- 手間がかかる
  - zola init時に勝手に各ページのサンプルを生成してくれればいいのにな…と、自作themeを作りながら何回か感じた。git cloneでthemeを入れた後、全体の構造を理解した上で.htmlをいじらないといけない局面があり、SSGに詳しくない人がいきなり手を出すのはややつらい気がする。最初のSSGとしてはHugoのほうがよさそう。
  - そして.htmlやconfig.tomlをいじっていく際、Tera Templateという独特のテンプレートエンジンを使う必要があり、学習コストが高いとまでは言わないけれど、お目当ての機能にたどり着くのにけっこう時間はかかるというのが実感。
  - 慣れるとそこそこ扱いやすいこのTera Template、Rust用のエンジンということなので、Rustを普段書いている人にとっては学習しておくと一石二鳥…かどうかはよくわかりません。
- themeがまだまだ少なそう
  - 公式で紹介されているのは2021年初頭時点で29。一方さすがのHugoは公式に載っているものだけでも300近くあるようなので、ここの差は人によっては大きいと思う。ただし、結局自分好みのサイトにしようとするなら、自分でいじらないといけない（いじることのできる）範囲が広いので、自力で全部書くのであれば関係ない。
- 公式ドキュメントが若干わかりにくい
  - トータルで見ると必要なことは全部書いてあるのだが、知りたいことがどこに書いてあるのか直感的に掴みづらい。たとえば、使用できるシンタックスハイライトのテーマ一覧がSyntax HighlightingというページではなくConfigurationにある、など。
- hugo new post/new.mdのような記事作成コマンドがない
  - 人によっては若干不親切と感じられるかもしれない。

総合して考えると個人的にはZolaのほうが馬が合う感じで好み。いちから自分の手でちまちま構築する（必要がある）雰囲気がArchと似ていて、「これについては自分が一番よく知っているし、何かあったら自分でなんとかできるはず」という感覚を得られる。これが個人的にはけっこう大事なポイントなので。

### Getting Started

以下は、themeを使用しない場合の導入方法です。

基本的な仕組みは、公式のドキュメントのGetting Startedに。

```
$ tree
.
├── config.toml
├── content
├── sass
├── static
├── templates
└── themes
```

さらにtemplatesの中身は以下。

```
[templates]$ tree
.
├── base.html
├── categories
│   ├── list.html
│   └── single.html
├── index.html
├── post.html
├── post-page.html
└── tags
    ├── list.html
    └── single.html
```

templatesに入っているこれらすべてのファイルと、親ディレクトリのconfig.tomlが必須要素。（タグ等の分類を使わなければtags及びcategoriesディレクトリは不要）。

#### 全体構造

- base.html すべてのページのテンプレート。head、header、footerなどはここに書く。
- index.html いわゆるトップページの内容。
- post.html, post-page.html それぞれ、記事一覧と各記事ページのテンプレートになる。

```
( base.html > index.html     ) + main.scss = example.com/index.html
( base.html > post.html      ) + main.scss = example.com/post
( base.html > post-page.html ) + main.scss + content/post/hoge.md   = example.com/post/hoge
( base.html > post-page.html ) + main.scss + content/hoge/index.md  = example.com/hoge
content/post/_index.md = content/post以下の記事群についてのメタデータ
```

このように、雛形の.htmlをベースにして（記事の場合は.mdファイルの各変数が代入され）そこに.scssから生成されるCSSファイルが適応されて最終的なhtmlが出力される、という流れになっている。この流れを可能にしているのがTera Template流の変数の仕組み。

content/hoge/index.mdとcontent/hoge/_index.mdの違いは、前者はexample.com/hogeへアクセスしたときに表示されるページとしてレンダリングされるが、後者はcontent/hoge以下の記事群についてのメタデータを記したファイルであるということ。

たとえばexample.com/aboutに直接aboutページを載せたいときは、content/about/index.mdにその内容を書く。逆に、記事一覧など、content/hoge以下の記事群に対応する変数はcontent/hoge/_index.mdに記載しておく。（この説明はちょっと怪しいけど…）

### tips

以上が分かればあとは自分好みに仕上げていくだけだが、個人的に詰まったところ・記録しておきたいところを書いておく。

#### Hugo(Academic)からの移行

Academicの.mdテンプレートはフロントマター（タイトルや投稿日などの記事のメタデータ）の区切りが+++でなく---になっているので、逐一変換する必要がある。記事数が多い場合は何らかのスクリプトを組まないと厳しい。

#### シンタックスハイライト

config.tomlに好みのテーマを書き、各.mdのコードブロック先頭に言語を明示することで適用される。対応しているテーマがまだ少ないので、こだわりのある人は先に公式をチェックしておきましょう。

#### 内部リンク

独特の内部リンク文法を使用しており、たとえば記事内で/post/hoge.mdにリンクを貼りたいときは@/post/hoge.mdとなる。

#### taxonomies

Zolaにおけるタグやカテゴリなどのtaxonomiesは各記事のフロントマターに明示するだけではダメで、templatesにTAXONOMIES/list.html, TAXONOMIES/single.htmlという２種類のテンプレートを作る必要がある。

#### scss

cssのメタ言語だが、学習コストはかなり低いので触っておいて損はないと思う。といっても自分はscss独自の機能はほぼ使用していないけれど…。

#### index.htmlに直接記事一覧を表示する

set_section関数を使用してpage.htmlを拾った上で、for構文を用いて表示する。

全記事でなく一部のみを表示したい場合はループカウントすることになるが、Tera Templateはloop.indexという特殊変数を用いてカウントするので注意。

#### config.extra.variable

config.tomlの[extra]（自作の設定）でなるべく変数定義することでコードがクリーンになる気がする。ただし、.scss内で自作変数を使うことはできないっぽい。.scssでなく直接.cssを書いて置いておくのであれば使えそう。

#### 数式

数式の表示はMathJaxを使用した。関連する部分のコードを貼っておくので参考までに。

```html
  {% if page.extra.math %}
  <script>
    MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']]
      }
    };
  </script>
  <script type="text/javascript" id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
  </script>
  {% endif %}
```

### まとめると

わかってくると楽しい、そういうジェネレーターです。興味がある方はぜひ。

### theme

自分で構築さえできれば、それそのものをテーマとして配布することができる。手順も簡単で、通常のサイトディレクトリにtheme.tomlを追加するだけ。

自分のサイトをテーマ化して独立させたものをGitLabに載せています。  
 [Kyohei Uto / emily_zola_theme · GitLab](https://gitlab.com/kyoheiu/emily_zola_theme)