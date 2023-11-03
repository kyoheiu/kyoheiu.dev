+++
title = "RustプロジェクトのビルドテストをGithub Actionsで行う（Arch Linuxのタグに要注意）"
date = 2021-11-25
math = false
[taxonomies]
categories = ["code"]
tags = ["Github Actions", "Arch Linux", "docker", "Rust"]
+++

タイトルの通りなのだが、若干ハマったので記録しておきます。

Rustのプロジェクトにおいて、自分のローカル環境以外でもうまくインストールできるかのテストを行うためにGitHub Actionsを使っている。


```
# .github/workflows/install_test.yml

name: 'install test'

on:
  push:
    branches-ignore: 'main'
    paths-ignore:
      - '*.md'

env:
  CARGO_TERM_COLOR: always

jobs:
  ubuntu-install:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Install
      run: |
        cargo install --path .
  macos-install:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v2
    - name: Install
      run: |
        cargo install --path .
  archlinux-install:
    runs-on: ubuntu-latest
    container:
      image: archlinux:latest
    steps:
    - uses: actions/checkout@v2
    - name: Install
      run: |
        pacman -Syu --noconfirm
        pacman -S gcc --noconfirm
        pacman -S rustup --noconfirm
        rustup install stable
        rustup default stable
        cargo install --path .
```

jobsは３つ。Ubuntu上・macOS上・Arch Linux上それぞれでのインストールをテストしている。（`cargo install --path .`が通ればcrates.ioからのインストールも問題ないという認識）

ご覧の通り、UbuntuとmacOSでは特に追加でライブラリをインストールする必要なくパスしているが、archlinux:latestを使った最後のテストでは、`gcc`と`rustup`を先にインストールしている。
`rustup`がarchlinux:latestに含まれていないのは当たり前のことなのでこれは良い。問題なのは`gcc`。

`gcc`を事前インストールしない場合、テスト中に

```
error: linker `cc` not found
  |
  = note: No such file or directory (os error 2)
```

とビルドエラーが出てしまう。 

そもそものarchlinux:latestイメージの中に入ってみると、

```
# docker run -it archlinux:latest
[root@0fd34e31306a /]# pacman -Qi gcc
warning: database file for 'core' does not exist (use '-Sy' to download)
warning: database file for 'extra' does not exist (use '-Sy' to download)
warning: database file for 'community' does not exist (use '-Sy' to download)
error: package 'gcc' was not found
```

うーん、やっぱり入ってない。`gcc`が含まれてないなんて、そんなことある？　と思いながら、テストはパスするのでそのままにしていた。

でもやっぱり引っかかる。そこで、よく[公式の説明](https://hub.docker.com/_/archlinux)を読んで見ると…

> Besides `base` we also provide images for the `base-devel` package group. 

tagにちゃんと`base-devel`がある…！　そして

> The `latest` tag will always match the latest `base` tag.

はい、ありがちな`base-devel`抜け。  
何も考えずlatestを使ってはいけないという教訓を得ました。

というわけで冒頭のymlを次のように変更。

```
  archlinux-install:
    runs-on: ubuntu-latest
    container:
      image: archlinux:base-devel
    steps:
    - uses: actions/checkout@v2
    - name: Install
      run: |
        pacman -Syu --noconfirm
        pacman -S rustup --noconfirm
        rustup install stable
        rustup default stable
        cargo install --path .
```

データベースの更新はいずれにせよ必要として、`gcc`の明示的インストールを削除。テストももちろんパス。あースッキリした。