+++
title = "ULIDを学ぶ　コードリーディングから実装まで"
date = 2022-09-06
math = false
[taxonomies]
categories = ["code"]
tags = ["Rust", "Deno", "ulid", "zenn"]
+++

ビット演算なんもわからんから始める。

まずこのクレートを解読し、

https://github.com/dylanhart/ulid-rs

その後に自分なりに別言語で実装してみる。

### ULID とは

ULID は Time を表す 48bit とランダムな 80bit から作られる 128bit の sortable identifier。

> 128-bit compatibility with UUID
> 1.21e+24 unique ULIDs per millisecond
> Lexicographically sortable!
> Canonically encoded as a 26 character string, as opposed to the 36 character UUID
> Uses Crockford's base32 for better efficiency and readability (5 bits per character)
> Case insensitive
> No special characters (URL safe)
> Monotonic sort order (correctly detects and handles the same millisecond)
> https://github.com/ulid/spec

くわしくは上記リポジトリ。
たくさんの言語で実装されているが、今回は Rust の ulid-rs を読んでいきます。

```rust
impl Ulid {
    pub fn new() -> Ulid {
        Ulid::from_datetime(SystemTime::now())
    }
    pub fn with_source<R: rand::Rng>(source: &mut R) -> Ulid {
        Ulid::from_datetime_with_source(SystemTime::now(), source)
    }
    pub fn from_datetime_with_source<R>(datetime: SystemTime, source: &mut R) -> Ulid
    where
        R: rand::Rng,
    {
        let timestamp = datetime
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or(Duration::ZERO)
            .as_millis();
        let timebits = (timestamp & bitmask!(Self::TIME_BITS)) as u64;

        let msb = timebits << 16 | u64::from(source.gen::<u16>());
        let lsb = source.gen::<u64>();
        Ulid::from((msb, lsb))
    }
```

なので、実質`Ulid::new()` = `Ulid::from_datetime_with_source(SystemTime::now(), &mut rng)`。

### サンプルコード

```rust
use rand::prelude::*;
use std::time::SystemTime;
use ulid::Ulid;

fn main() {
    let mut rng = StdRng::from_entropy();
    let ulid = Ulid::from_datetime_with_source(SystemTime::now(), &mut rng);
    println!("{}", ulid.to_string());
}
```

サンプルの main 関数を上記のようにして、`git clone`したライブラリの中に`println!`を埋め込みまくることで愚直に表示していく。

### timestamp 取得

```rust
        let timestamp = datetime
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or(Duration::ZERO)
            .as_millis();
```

まずここでは、UNIX TIME を millis で取得している。取得できなければ 0 としている。

```
1662408777120 timestamp
```

### ビットマスク

```rust
        let timebits = (timestamp & bitmask!(Self::TIME_BITS)) as u64;
```

この`bitmask!`は何回も出てくるので、まずここから。

```rust
macro_rules! bitmask {
    ($len:expr) => {
        ((1 << $len) - 1)
    };
}
```

integer をとり、`1`をその integer 分シフトして 1 を引く…というマクロ。デバッグしてみる。

```rust
    let bitmask: u64 = ulid::bitmask!(40);
    println!("{:b}", bitmask);
```

```
1111111111111111111111111111111111111111
```

つまり全ての bit が 1 の、任意の長さのビットマスクを作るマクロですね。
気をつけないといけないのは、`u64`などと型をきちんと指定してあげないと、overflow でパニックを起こす点。

```
thread 'main' panicked at 'attempt to shift left with overflow', src/main.rs:9:19
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

型を指定しない場合、コンパイラが i32 と推測してくるのでこうなってしまう。何桁ほしいのかをちゃんと指定すれば問題なし。

で、そのビットマスクと timestamp を&演算子でつないでいるので、timebits というのは 64bit で表された timestamp ということになる。

```
11000001100001111010100110101000100001001 timebits
```

ただし leading 0s は`:b`だけでは表示されないので注意。

### random part

```rust
        let msb = timebits << 16 | u64::from(source.gen::<u16>());
        // println!("{:b} msb", msb);
        let lsb = source.gen::<u64>();
        // println!("{:b} lsb", lsb);
```

残りのここは最初何をやっているのかよくわからなかったのだけど、要するに、残りの 80bit = randomness を担保している部分を、16bit と 64bit に分けて作って入れている、ということらしい。

### 128bit 生成

```rust
impl From<(u64, u64)> for Ulid {
    fn from((msb, lsb): (u64, u64)) -> Self {
        let base = u128::from(msb) << 64 | u128::from(lsb);
        Ulid(base)
    }
}
```

そしてここに飛ぶ。
msb と lsb に分けているのは、それぞれを u64 として扱うため（多分）。
まず msb を左シフトしてから、u128 として読み込んだ lsb と OR 演算子でつないで、完成形の 128bit の ULID を生成している。

```
1100000110000111101010011010100010000100100100001010011000010110110100000111101100001101110011100100111110000001010001110 base
```

※leading 0s は非表示。

### エンコード

ULID は通常`01GC7N6M894562V87P3EE9Y0ME`といった形でよく見かけるが、これは base32 にエンコーディングされた見かけ。
このエンコード処理は`base32.rs`に定義されている。

```rust
pub fn encode_to(mut value: u128, buffer: &mut [u8]) -> Result<usize, EncodeError> {
    // NOTE: This function can't be made const because mut refs aren't allowed for some reason

    if buffer.len() < ULID_LEN {
        return Err(EncodeError::BufferTooSmall);
    }

    for i in 0..ULID_LEN {
        buffer[ULID_LEN - 1 - i] = ALPHABET[(value & 0x1f) as usize];
        value >>= 5;
    }

    Ok(ULID_LEN)
}
```

引数の buffer は通常`[u8, ULID_LEN]`（ULID_LEN = 26）として呼ばれるので、このエラーはほぼ発生しないタイプのエラーじゃないかなと思われる。

メインの for ループについて。buffer の後ろから文字を詰めていくスタイル。
これをデバッグプリントしてみると…

```rust
    for i in 0..ULID_LEN {
        let v = (value & 0x1f) as usize;
        println!("{:05b} v", v);
        buffer[ULID_LEN - 1 - i] = ALPHABET[v];
        value >>= 5;
    }
```

```
1100000110000111101100011110110011101111111010110101011010111011011101001010100100001110010001101010101000010001010101000 base
01000 v
10101 v
01000 v
...
```

となる。つまり`11111`と＆でつなぐことで、右のほうから５桁ずつ切り出して 5bit の usize を取り出しているというわけですね。その usize により、

```rust
const ALPHABET: &[u8; 32] = b"0123456789ABCDEFGHJKMNPQRSTVWXYZ";
```

と定義されている使用文字から一つをとってくることで、エンコードしている。
たとえば`01000`は usize でいうと 8 で、`ALPHABET[8]`は…8 なので、この ULID の一番右の文字は

```
01GC7P7PEZTTPQDTAJ3J6N88N8
```

ちゃんと 8 になっている。なるほどー。

128bit なので最後のほうは足りてないということになるはずだが、それはあんまり気にしなくていいやつなんですかね。

### 別言語での実装

https://github.com/kyoheiu/ulideno

Deno 向けのシンプルな ULID 生成ライブラリを作ってみた。
Rust のように`u128`なんて便利な型が用意されているわけでもないので、最初は`string`型で timestamp 部分と random 部分の疑似バイナリを扱っていたけれど、やっぱりなんか気持ちが良くないので、`bigint`でなるべく処理するようにしたらまあまあコードがすっきりしたような気がします。
