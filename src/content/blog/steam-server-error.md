+++
title = "Steamサーバー接続時トラブルを解決する（Arch Linux）"
date = 2020-12-23
[taxonomies]
categories = ["code"]
tags = ["linux", "Arch Linux", "steam", "DHCP"]
+++

### 環境
OS: Arch Linux x86_64  
Kernel: 5.9.14-arch1-1  
Steamは`pacman`のパッケージを使用。

### 問題
前提として、「ブラウザなどのネットワーク接続は異常なし」。  
1. ある日突然、Steamで購入したはずのゲームをダウンロードできなくなる。（ダウンロードアイコンをクリックしてもダウンロードが始まらない／一瞬で停止する）
2. 上記を解決するべくSteamを再インストールしてみたところ、今度はログインができなくなる。エラーメッセージは **"Steam is having trouble connecting to the Steam servers"**.

### 原因
僕の場合は、少し前にネットワークへの接続方法を`NetworkManager`から`systemd-networkd`に切り替えた際、DHCP接続の設定が抜けていたことが原因だった模様。  

### 対策
`systemd-networkd`でWi-FiにDHCP接続する場合は、
#### (1)
`/etc/systemd/network/interface.network`に

```
[Match]
Name=interface
[Network]
DHCP=yes
```

と書いておき、**同時に**

#### (2)
別途`dhcpcd`をインストールして

```
# systemctl start dhcpcd.service
# systemctl enable dhcpcd.service
```

しておかなければならない。

`NetworkManager`を使っていた元々の設定では、このあたりはクリアーできていたようなのだが、`networkd`へ切り替えたタイミングでDHCPまわりが抜けた結果起こった問題と思われる。

しかし(2)が抜けた状態でも、ブラウザやターミナルでのインターネット接続は問題なく行えていたので、`dhcpcd`不在によるトラブルだということを突き止めるまで時間がかかってしまった。

### cf
https://github.com/ValveSoftware/steam-for-linux/issues/2085
https://github.com/ValveSoftware/steam-for-linux/issues/4855

関連していそうなissue。「Steam以外はふつうにネット接続できている」というのがミソ。`networkd`以外を使っていても、同症状の場合は一度DHCP接続を確認してみるとよいかもしれない。
