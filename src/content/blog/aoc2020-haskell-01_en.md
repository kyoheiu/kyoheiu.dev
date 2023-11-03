+++
title = "Day 1: Solving Advent of Code 2020 in Haskell"
date = 2021-05-15
draft = true
[taxonomies]
categories = ["code"]
tags = ["Haskell"]
+++

> Advent of Code is an Advent calendar of small programming puzzles for a variety of skill sets and skill levels that can be solved in any programming language you like. People use them as a speed contest, interview prep, company training, university coursework, practice problems, or to challenge each other.  
<https://adventofcode.com/2020/about>

As an exercise in learning Haskell, I'm trying to solve this group of well-made coding problems.

### Problem
Let's see the first problem, which is about the search in a sequence.  
For example, we have this list:

```
1721
979
366
299
675
1456
```

We must find two numbers that sum to 2020 (of course). After that we need to multiply the pair, but this part isn't difficult any way.

### Answer
```hs
import Data.List as L

twoSum (x:xs)
    | x > 2020 = twoSum xs
    | otherwise = case L.find (== 2020 - x) xs of
                    Just n -> Just (x * n)
                    Nothing -> twoSum xs

readInt x = read x:: Int

main = readFile "aoc01.txt" >>= print. twoSum . map readInt . words
```

Using singly-linked list as iterator(basic in Haskell), `L.find` looks up `Maybe Int` that satisfies needed condition.  
`print` shows `Just (some number)`, not `some number`, but this is enough for answer.

### Part Two
This problem is followed by a little bit harder one: Search the three numbers that sum to 2020. So does we have to make subsequences of a sequence?  
`subsequences` in `Data.List` costs high, and takes long time to finish if the sequence is big. In this case, instead of full-search, we should re-use the first answer code like this:

```hs
import Data.List as L

twoSum _ [] = Nothing
twoSum n (x:xs)
    | x > n = twoSum n xs
    | otherwise = case L.find (== n - x) xs of
                    Just m -> Just (x * m)
                    Nothing -> twoSum n xs

threeSum [] = Nothing
threeSum (x:xs)
    |x >= 2020 = threeSum xs
    |otherwise = case twoSum (2020 - x) xs of
                   Just n -> Just (x * n)
                   Nothing -> threeSum xs

readInt x = read x:: Int

main = readFile "aoc01.txt" >>= print. threeSum . map readInt . words
```

Use `twoSum` in first answer as a helper, and finding three numbers becomes quite an easy task. Here, full-search is separated into two simple searchs.

### Conclusion
With this problem, we can learn:
- list as iterator
- avoid full-search when you can

GitHub repository:
[kyoheiu/aoc2020-haskell](https://github.com/kyoheiu/aoc2020-haskell)
