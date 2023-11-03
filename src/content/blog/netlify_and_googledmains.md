+++
title = "Netlifyで独自ドメイン（Google Domains）を使う"
date = 2021-04-30
math = false
[taxonomies]
categories = ["blog"]
tags = ["Netlify", "Google Domains"]
+++
Google Domainsで管理している独自ドメインを使っているのだが、少し前にロリポップ！のサーバーから引越しをした。その際、いくつかのホスティングサービスの中でどれがいいか少し迷ったので、メモ。

まず、オプションとして以下のものを考えた。

- Firebase
- GitLab pages
- Netlify


Firebaseは良さげだったが、動的サイトのホスティング向けのような気がしたので今回はパス。

次にGitLab pages。僕はGitLabをメイン使いしているので当初はこれ一択かなと思っていたのだが、はっきり言って期待外れだった。  
というのは、独自ドメイン適用周りがどうにもこうにもうまくいっていないのだ。

### なぜ
そもそも公式のドキュメントが矛盾しているので、何を信用したらいいのかわからないから。

[チュートリアル](https://docs.gitlab.com/ee/user/project/pages/custom_domains_ssl_tls_certification/)ではAレコードをこれこれに、TXTレコードをこれこれに設定しろと書いてあるのに、カスタムドメインの設定画面ではCNAMEとTXTの設定を求めてくる。どういうことだ。  
実際両方やってみたのだが、どっちもうまくいかず途方に暮れた。

### Netlifyでのレコード設定
というわけで、Zolaのテーマサイトのホスティングにも元々使っていたNetlifyをチョイス。
Google Domainsの設定は以下のようにすればOK。

name | type | TTL | data
:-- | :-- | :-- | :--
@ | A | 10m(or whatever you like) | 75.2.60.5
www | CNAME | same as above | YOURSITENAME.netlify.app.

NetlifyはDNS設定が認証された後、自動的にTLS証明書をLet's Encryptからとってきてくれる。独自ドメインでのホスティングは今のところNetlifyが圧勝。GitLab頑張れ。