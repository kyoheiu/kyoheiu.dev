+++
title = "bashのhistoryを補完するプログラム"
date = 2022-10-10
math = false
[taxonomies]
categories = ["code"]
tags = ["Rust", "bash", "history", "sqlite"]
+++

## historyはすごい

bashを使っていて、historyを使ったことがないという人はいないというくらい、historyはターミナル生活の要となっているコマンドです。  
`history`でコマンド履歴を呼び出せるだけではなく、`Ctrl + p` / `Up Arrow`で最新の履歴から遡って呼び出していく機能、`!`で履歴にあるコマンドを指定して実行できる機能など、historyはビルトインでbashにがっちり組み込まれていて使い勝手も素晴らしく、その分、そう簡単に代替できるものではありません。  
（もちろん、様々な代替実装が各言語で作られていそうですが）

## 改善したいポイントもある

一方、不満がないわけではありません。大きく３つ、個人的に改善したいポイントがありました。

1. 別のターミナルで実行したコマンドが履歴として表示されない  
作業中、別のターミナルを開いてそこで何かしらを実行するということはよくあることだと思いますが、その履歴は元のターミナルでは（少なくともデフォルトでは）表示されません。

2. ターミナルマルチプレクサ内で実行したコマンドもデフォルトでは正確に記録されない、という仕様もあります。ただしこれにはワークアラウンドがあり、`.bashrc`なり`.tmux.conf`なりに追加で記述すれば保存されるようです。

3. 特定のディレクトリ内で実行したコマンドに絞って振り返ることができない  
ペットプロジェクトをしばらく放置したあとに戻ってきてみると、ビルドコマンドやテストコマンド、あるいはデプロイ用のコマンドなど、何をどう使っていたかさっぱり忘れている…という経験が何度かありました。  
Makefileなどに記録しておけば事足りる（し、いくつかのプロジェクトではそうしている）のですが、常にこれを忘れず実行できるわけでもありませんし、些細なコマンドをすべて記録するのも難儀です。ディレクトリパスでフィルタリングし、そこで実行したコマンドだけ見たい…という需要が個人的にはあります。

## historyを補完する

そこで、自分なりのhistoryを実装してみました。といっても今回は、historyを本格的に代替することを目指すのではなく、historyが提供していない機能を実装することを意識しました。

[https://github.com/kyoheiu/shi](https://github.com/kyoheiu/shi)

```
shi [ROWS]                       Print executed commands and time. If no input 50

Options:
  -a, --all                      Print all the history with the directory path where the command was executed
  -i, --insert <COMMAND>         Insert the command to the history
  -d, --delete <ID>              Delete the command that matches the id
  -r, --remove                   Drop the database table, delete all history
  -p, --path <PATH> [ROWS]       Show commands that were executed in directories that match the query
  -c, --command <COMMAND> [ROWS] Show commands that match the query
  -o, --output                   Export all the history to `~/.shi/history.csv`
```

例：
![](https://storage.googleapis.com/zenn-user-upload/548531c6e57e-20221010.png)

一番慣れているRustで書きましたが、実際にはsqliteとのやり取りにRustをグルーとして使っている形なので、他の言語でも書けそうです。  
機能としては単純で、実行コマンドをsqliteデータベースに登録し、後で様々な形でSELECTできるようにしているだけです。

もちろん、このプログラムをただインストールするだけでは何もできないので、`.bashrc`の最後に以下を追加で記述します。

```
source ~/.bash-preexec.sh
preexec() { shi --insert "$@"; }
```

ここでは[bash-preexec](https://github.com/rcaloras/bash-preexec)を使用しています。`preexec()`は、入力したコマンドの実行前に`{ }`内のコマンドを実行してくれます。これにより、ビルトインのhistoryとほぼ同じ使い勝手で履歴がデータベースに登録されています。

historyにないものを、という意識で実装したポイントとしては、
- 別のターミナルで実行したコマンドも即時保存  
  別のターミナルを開こうが、上記の`.bashrc`と`shi`によって実行コマンドは確実にsqliteデータベースにINSERTされるので、どのターミナルかというのは関係なくなります。（紐付かなくなることによるデメリットがないわけではない点に注意）
- たとえばzellijで実行したコマンドも保存できる（tmuxはデフォルトでは保存できない）  
  これは各マルチプレクサの仕様次第ですが、今デフォルトで使っているzellijは大丈夫だったのでとりあえずよしとしています。
- ディレクトリパスを保存しているので、パスに含まれる単語で履歴検索が可能
  
といったところです。

## パス検索はかなりいい

最後のパス検索について。たとえば、最近Zigを勉強するために、[ratfactor/ziglings: Learn the Zig programming language by fixing tiny broken programs.](https://github.com/ratfactor/ziglings)こちらを進めているのですが、少し離れて戻ってくると、どこまでやったか忘れていることがあります。まあ、そういうときのためにgitがあるとも言えるのですが、Vanilla Vim上でちまちまやっていたりするとパッとは分からないもので、そういうときに`shi -p ziglings`と打ち込むと、

```
 194 | zig build 65  | 2022-10-07 15:02:44 | /home/kyohei/zig/ziglings
 195 | zig build 65  | 2022-10-07 15:06:25 | /home/kyohei/zig/ziglings
 196 | zig build 65  | 2022-10-07 15:08:29 | /home/kyohei/zig/ziglings
 197 | zig build 65  | 2022-10-07 15:10:38 | /home/kyohei/zig/ziglings
 198 | fx            | 2022-10-07 15:21:12 | /home/kyohei/zig/ziglings
 199 | fx            | 2022-10-07 15:23:31 | /home/kyohei/zig/ziglings
 200 | zig build 66  | 2022-10-07 15:27:15 | /home/kyohei/zig/ziglings
 201 | zig build 66  | 2022-10-07 15:28:51 | /home/kyohei/zig/ziglings
 202 | zig build 66  | 2022-10-07 15:28:56 | /home/kyohei/zig/ziglings
 203 | zig build 66  | 2022-10-07 15:30:00 | /home/kyohei/zig/ziglings
 204 | zig build 66  | 2022-10-07 15:30:39 | /home/kyohei/zig/ziglings
 205 | zig build 66  | 2022-10-07 15:31:08 | /home/kyohei/zig/ziglings
 206 | zig build 66  | 2022-10-07 15:31:18 | /home/kyohei/zig/ziglings
 207 | zig build 67  | 2022-10-07 15:42:07 | /home/kyohei/zig/ziglings
 208 | zig build 68  | 2022-10-07 15:49:45 | /home/kyohei/zig/ziglings
 209 | zig build 69  | 2022-10-07 15:52:14 | /home/kyohei/zig/ziglings
 210 | zig build 69  | 2022-10-07 15:52:50 | /home/kyohei/zig/ziglings
 211 | zig build 69  | 2022-10-07 15:53:18 | /home/kyohei/zig/ziglings
 212 | zig build 70  | 2022-10-07 15:58:50 | /home/kyohei/zig/ziglings
 ...
```

といった感じで、「あ、70まではやったんだな」とか、「66で詰まってたんですね」と過去の自分の行動をコマンド単位で振り返ることができます。  
ちなみに、この２つめの「コンパイルエラーについてざっくりとでも詰まったポイントが見える」というのは、自分でも意図していなかったメリットでした。

## その他

履歴が大量になってきた場合のパフォーマンスについては測定できていませんが、sqliteを使用しているので、`.bash_history`を呼び出すビルトインhistoryよりは若干速いのでは…という期待もあります。

前述したようにsqliteにINSERTしていくだけのプログラムなので、zshなどほかのシェルにも対応していますし、シェルをまたがって履歴を保存していくこともできそうです。複数のシェルを使い分けている場合は、個々のhistoryよりも一覧性があるので有用かもしれません。

ビルトインの`!`や`Ctrl + p`同等の機能は未実装ですが、そこまでオーバーライドするのは避けたいという気持ちがあり、あくまで履歴をきちんと保存し、引き出せるようにする…という機能のみにとどまりました。前述した通り、historyの全面代替ではなく、historyが提供していない機能を補完的に実装することを目指した形です。

## 終わりに

ニッチといえばニッチなプログラムですが、「痒いところに手を届かせるために作った孫の手」としてはけっこう満足しています。他の方の”孫の手プロジェクト”もぜひ見てみたいです。
