+++
title = "starshipで絵文字を表示させる（Arch Linux）"
date = 2021-03-31
math = false
[taxonomies]
categories = ["code"]
tags = ["Linux", "Arch Linux", "starship", "fonts"]
+++
先日のArch Linux再インストールに伴い、色々とアプリケーションを入れ直していたのだけれど、[starship](https://starship.rs/)の絵文字表示ができなくなってしまいちょっと手こずったので、メモ。

#### 必要なパッケージ
- `starship`
- nerd font(AURの`nerd-fonts-source-code-pro`を使っているが何でもいいはず)
- `noto-emoji`
- `noto-fonts`
- `noto-fonts-cjk`

最後の２つのパッケージがないとカバーできないUnicode絵文字が微妙に存在する（たとえば[⇡]）。

starshipの意義については正直なんとも言えないが、デバッグを繰り返しているときに前の実行結果との切れ目がわかりやすい…という効果はある。かもしれない。