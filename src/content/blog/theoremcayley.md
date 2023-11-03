+++
title = "ケーリーの定理の証明"
date = 2020-07-08
[taxonomies]
categories = ["math"]
tags = ["group", "category"]
[extra]
math = true
+++

Steve Awodey, *Category Theory*で圏論を少しずつ学習中。いきなりつまずいた表題の定理の証明についてまとめておく。

> Theorem(Cayley). Every group G is isomorphic to a group of permutations.  
(p.13)  
群$G$は置換群の部分群と同型。

単語の定義から。  
$X$を群とするとき、全単射写像$f: X \rightarrow X$を$X$の置換という。$X$の置換全体からなる群を$X$の置換群という。  
置換群とは、$cod(f)$を指すのではないことに注意。つまり定理の出発点になる群$G$とはレイヤーの異なるところに位置する群としてイメージすることで、定理の意味を把握しやすくなると思う。

定理の証明は以下の順序で行う。

1. 全単射写像$\bar{g}: G \rightarrow G$を定義する。
2. $i: G \rightarrow \bar{G}$が同型写像であること、つまり$G \cong \bar{G}$を示す。

### (1) $\bar{g}: G \rightarrow G$

ある$g \in G$について、すべての$h \in G$に対し

$$\bar{g}(h) = g \cdot h$$

となる写像$\bar{g}$があるとする。   

#### 単射性

$\bar{g}(a) = \bar{g}(b)$であれば、

$$g \cdot a = g \cdot b$$  
$$g^{-1} \cdot g \cdot a = g^{-1} \cdot g \cdot b$$  

したがって$a = b$となる。

#### 全射性

$y \in G$について、$G$のある元$x$が存在して$\bar{g}(x) = y$となることを示す。  
$G$は群なので、

$$y = e \cdot y = g \cdot g^{-1} \cdot y = g \cdot (g^{-1} \cdot y)$$

したがって、$x = g^{-1} \cdot y$とおくと、$\bar{g}(x) = y$とおけ、$\bar{g}$は全単射。

### (2) $i: G \rightarrow \bar{G}$と$j: \bar{G} \rightarrow G$

各元$g \in G$について、$G$の置換への写像（つまり関数を呼び出す関数）$i$を

$$i: G \rightarrow \bar{G}$$  
$$i(g) = \bar{g}$$

とする。

また、各元$\bar{g} \in \bar{G}$について、ある元$x \in G$への写像$j$を

$$j: \bar{G} \rightarrow G$$  
$$j(\bar{g}) = \bar{g}(x)$$

とする。

ここで、iが同型写像であることを示すためには、$j$が群$X$の置換$\bar{g}$からその置換$\bar{g}$のもととなった$g \in G$への写像となるような$x$をとる必要がある。

$$\bar{g}(x) = g = g \cdot u$$

したがって求めるべき$x$は$x = u$となり、$j(\bar{g}) = \bar{g}(u)$と書ける。

実際、このとき

$$(i \circ j)(g) = j \circ (i(g)) = j(\bar{g}) = \bar{g}(u) = g \cdot u = g$$

また、

$$(j \circ i)(\bar{g}) = i(j(\bar{g})) = i(\bar{g}(u)) = i(g \cdot u) = i(g) = \bar{g}$$

より、$i$は同型写像。$\square$