+++
title = "Arch Linuxインストールメモ(2020)"
date = 2020-09-20
[taxonomies]
categories = ["code"]
tags = ["linux", "Arch Linux"]
+++

# (2021-03-21) このメモは古く、現行バージョンでは使えません。記録として残しています。ArchWikiを読みましょう。

Arch Linuxインストールの覚書。将来の自分へのメモとして。

liveインストールの時点でどの程度パッケージを入れておくかは自由だが、インストール自体が初めての場合は`pacstrap`段階では基本パッケージ、エディタ、ネットワーク関係（これも選択肢は複数ある）くらいにとどめておき、後でX以下を入れていくほうが理解が進むのでいいと思う。

### インストール後トラブルの未然防止策
- ネットワークに接続できない -> インストール時にネットワーク周りのパッケージを導入しておく。  
- `pacman`が見つからない -> インストール時に`base-devel`を入れておく。

### はじめに
UEFIモードでliveUSBを起動すること

### まずwifi接続
wifi-menu

### パーティション
#### リストを確認
`fdisk -l`
#### パーティションブレイク
`sgdisk --zap-all /dev/nvme0n1`
#### パーティション分割開始

```
gdisk /dev/nvme0n1
Command (? for help): o
This option deletes all partitions and creates a new protective MBR.
Proceed? (Y/N): y

Command (? for help): n
Partition number (1-128, default 1): default
First sector (34-xxxxxxxxx, default = xxxx) or {+-}size{KMGTP}: default
Last sector (xxxx-xxxxxxxxx, default = xxxxxxxxx) or {+-}size{KMGTP}: +500M
Hex code or GUID (L to show codes, Enter = 8300): ef00

Command (? for help): n
Partition number (2-128, default 2): default
First sector (34-xxxxxxxxx, default = xxxxxx) or {+-}size{KMGTP}: default
Last sector (xxxxxx-xxxxxxxxx, default = xxxxxxxxx) or {+-}size{KMGTP}: default
Hex code or GUID (L to show codes, Enter = 8300): default

Command (? for help): w

Do you want to proceed? (Y/N): y
OK: writing new GUID partition table (GPT) to /dev/nvme0n1
```

### フォーマット
```
mkfs.fat -F32 /dev/nvme0n1p1
mkfs.ext4 /dev/nvme0n1p2
```

### マウント
```
mount /dev/nvme0n1p2 /mnt
mkdir /mnt/boot
mount /dev/nvme0n1p1 /mnt/boot
```

### ミラーリストの編集
`vi /etc/pacman.d/mirrorlist`

### 時計合わせ
`timedatectl set-ntp true`

### パッケージインストール開始
#### 基本パッケージ
`pacstrap /mnt base linux linux-firmware base-devel man-deb man-pages`
#### ネットワーク関係
`pacstrap /mnt networkmanager nm-connection-editor network-manager-applet`
#### テキストエディタ
`pacstrap /mnt nano vi nvim`
#### デスクトップ環境（X）
`pacstrap /mnt  xorg-server xorg-apps xorg-xinit`
#### デスクトップ環境（WM）
`pacstrap /mnt i3`
#### i3関連
`pacstrap /mnt vifm feh picom rxvt-unicode rofi parcellite`
#### 日本語周り
`pacstrap /mnt fcitx fcitx-mozc fcitx-im fcitx-configtool`
#### その他
`pacstrap /mnt chromium xf86-video-intel lightdm lightdm-gtk-greeter`

### Fstab作成
`genfstab -U /mnt >> /mnt/etc/fstab`

### chroot
`arch-chroot /mnt`

### タイムゾーン
`ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime`

### adjtime生成
`hwclock --systohc`

### LANG
```
vi /etc/locale.gen
	en_US.UTF-8 UTF-8
	ja_JP.UTF-8 UTF-8

locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
export LANG=en_US.UTF-8
```

### ホストネーム
```
echo hostname > /etc/hostname
vi /etc/hosts
127.0.0.1	localhost
::1		localhost
127.0.1.1	hostname.localdomain	hostname
```

### rootパスワード
`passwd`

### リポジトリアップデート
`pacman -Syy`

### マイクロコードアップデート　インストール
`pacman -S intel-ucode`

### boot-loader
```
pacman -S grub efibootmgr
mkdir /boot/efi
mount /dev/nvme0n1p1 /boot/efi
grub-install --target=x86_64-efi --bootloader-id=GRUB --efi-directory=/boot/efi
grub-mkconfig -o /boot/grub/grub.cfg
```

### 終了・再起動
```
exit
umount -R /mnt
shutdown now
```