---
title: "passkeyを腹落ちさせる"
date: 2023-11-27
categories: ["code"]
tags: ["auth", "passkey", "2FA"]
---

## 文脈

さくらのVPSでホスティング・公開している種々のWebアプリケーションへのアクセスを保護するために認証サーバーを自作して使っている。そこにpasskey技術を導入すべきか迷っている。  
ちなみに自分で認証サーバーを作ってみるのは、認証に対するownershipがかんたんに得られるのでとてもよいです。

## 現状の認証フロー
現状は2FAを採用している。

1. 認証サーバー経由でLDAPサーバーにDN/Passwordを送る
2. モバイルのAuthenticatorアプリでパスコードを取得し、それを認証サーバーに入力する
  
モバイルのAuthenticatorアプリは、指紋認証をかけることができるMicrosoft Authenticatorを使用している。このことにより、

- Something you know <- DN/Password
- Something you have <- モバイルデバイスのアプリ
- Something you are <- finger print

と、３要素を満たすことができている…という認識。

一方で最近passkey認証が盛り上がってきており、セキュアな認証を使いたいというモチベーションと、新しい技術を触っておきたいというモチベーションがあるので、passkeyの技術をこのセルフホストアプリケーションの認証サーバーで使えないか検討している。

色々Bardに尋ねてみているが、まだちょっと腹落ちできていないところがあったので、疑問点や懸念点、現状の自分なりの結論を記録しておきたい。

## passkey単体では３要素を満たすことができない？
> Passkey authentication only satisfies two of the three parts of authentication: something you have and something you are. This is because passkeys are stored on a physical device and are authenticated using a biometric factor.

ただし上記のような2FAでもphishing attacksにはvulnerableであるので、要素数と想定される攻撃と、それぞれをどう評価するかでセキュリティレベルについては判断が分かれるところ、ということのよう。  
また、数桁のパスコードを入力させる現状の（そして多くの2FAで使われている）認証方法だとbrute force attackには弱いので、それなりの対策をとる必要がある（し、とっている）。

## passkeyの利便性を向上させる手段としてパスワードマネージャーとの併用が挙げられるが、これによりセキュリティレベルが下がることはないのか？

> Yes, sharing passkeys through a password manager like Bitwarden does introduce a potential security risk. If a password manager is compromised, all stored passkeys could be exposed. This is because password managers typically store the secret keys for passkeys in an encrypted form, but the encryption key itself is also stored within the password manager. If an attacker gains access to the password manager's encryption key, they could decrypt all of the stored passkeys and use them to access the user's accounts.  
To minimize this risk, it is recommended to use passkeys directly whenever possible and only use password managers as a last resort. If you do decide to use a password manager to store passkeys, make sure to choose a reputable and trustworthy provider that has a strong track record of security. You should also enable two-factor authentication on your password manager account to add an extra layer of protection.  
Here are some additional tips for using passkeys securely:  
> - Only use passkeys on websites and apps that you trust.
> - Be careful about phishing attacks. Phishing attacks are attempts to trick you into revealing your passkeys or other personal information.  
> - Use a strong and unique passphrase for your passkeys.
> - Enable two-factor authentication on your accounts whenever possible.

パスワードマネージャーのセキュリティリスクというのはわりと大事な話だと思うのだけど、あまり見かけない話題でもある。  
もちろん僕もパスワードマネージャーを使っている。今はBitWardenを使っていて、よいソフトウェアだと思うし、これ自体に不満はあまりない。  
（フォーク版のVaultWardenに移行しようか迷っているが）  
BitWardenでいうと、BitWarden自体へのログインは

- マスターパスワード
- PIN
- 生体認証

といった感じで複数用意されている。今はマスターパスワードを使っているが、生体認証に対応したOSであれば生体認証が一番セキュアであることは確かだと思う。  
では生体認証でログインすれば、BitWardenにpasskeyを保存してもよいか？　ここのリスク評価は難しくてまだ答えが出せていない。これはパスワードマネージャー依存とはまた別の問題のような気がする。

## やっぱりpasskeyのほうがよい？
あらためて、生体認証付きの2FAとpasskey単体のセキュリティレベルをBardに聞いたところ、回答の中に次の一節が出てきた。

> In terms of overall security, passkeys and 2FA with biometric authentication offer comparable levels of protection when implemented effectively. Passkeys provide a passwordless approach, eliminating password-related vulnerabilities, while 2FA with biometrics adds an extra layer of security to password-based authentication.

この文章を読んで、「やっぱりpasskeyのほうがセキュアなのでは？」という理解に傾いてきた。というのは、パスワードベースの認証レイヤーを加えることでセキュリティレベルを上げる…というのは効果的でないどころか、それ自体がセキュリティホールになりうる、と感じたから。  
（実際、LDAPサーバーってセキュリティどうなのと聞かれたら言葉に詰まる）    
passkeyの大目標である「パスワードを抹殺する」はそれ自体に大義あり、と共感するならやはりpasskeyをいずれは使うべきで、いや、パスワードにもいいところはあると思うならガチガチの2FAで運用していけばよい…ということなのかもしれない。