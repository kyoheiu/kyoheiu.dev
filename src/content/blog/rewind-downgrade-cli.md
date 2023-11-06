---

title: "rewind - A CLI tool to downgrade packages using local Pacman cache"
date: 2021-08-08
categories: ["code"]
tags: ["Haskell", "Arch Linux", "CLI"]
---[kyoheiu/rewind](https://github.com/kyoheiu/rewind)

![gif](./images/rewind.gif)

### Installation

```
git clone https://github.com/kyoheiu/rewind.git
cd rewind
cabal install
```

### Usage

```
rewind [package name you want to downgrade]
```

like `rewind neovim`.
You can use mutliple arguments like `rewind neovim emacs` as well.
