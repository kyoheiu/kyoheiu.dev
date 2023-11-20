---
title: "GoのwaitGroupとchannelについて整理する"
date: 2023-11-20
categories: ["code"]
tags: ["Go", "goroutine"]
---
確実にgoroutineを終わらせるためにブロックする方法として、WaitGroupとchannelを整理する。

## 何も使用しないパターン
```go
package main

import (
	"fmt"
	"time"
)

func do() {
	time.Sleep(2 * time.Second)
	fmt.Println("Woke up.")
}

func main() {
	fmt.Println("Starting goroutine.")
	go do()
	fmt.Println("Finished.")
}
```
```
Starting goroutine.
Finished.
```

`do()`内に記述されているfmt.Println()を実行する前にmain関数が終了してしまう。

## sync.WaitGroupのみを使うパターン
```go
func do(wg *sync.WaitGroup) {
	defer wg.Done()
	time.Sleep(2 * time.Second)
	fmt.Println("Woke up.")
}

func main() {
	var wg sync.WaitGroup
	wg.Add(1)
	fmt.Println("Starting goroutine.")
	go do(&wg)
	wg.Wait()
	fmt.Println("Finished.")
}
```
```
Starting goroutine.
Woke up.
Finished.
```

1. `wg.Add(1)`でタスクを登録する。
2. main関数内の`wg.Wait()`で、タスクカウンタが０になるまで待ち受ける。これにより、起動中のgoroutineを無視してmainが終了するのを防ぐ。
2. `do()`内の`defer wg.Done()`で、関数終了時にタスクカウンタをひとつ減らす。

goroutineとのデータ受け渡しがない、つまりchannelを使う必要がない場合はこれで十分に見える。

Bardによると、

> Whether or not using a WaitGroup is necessary when using channels depends on the specific use case. In some cases, using channels alone can be sufficient to block the main function from exiting until all goroutines have completed their tasks. However, in other cases, using a WaitGroup can be a more efficient and reliable way to ensure that all goroutines have finished before proceeding.  
When to use a WaitGroup  
A WaitGroup is typically used when you need to track the number of goroutines that are still running and wait for them all to finish before proceeding. This is particularly useful when you have a fixed number of goroutines that are all performing independent tasks. For example, if you're making multiple HTTP requests in parallel, you can use a WaitGroup to wait for all of the requests to complete before processing the responses.  
When not to use a WaitGroup  
If you don't need to track the number of goroutines that are still running, or if you don't need to wait for them all to finish before proceeding, then you can usually get away with using channels alone. For example, if you're producing a stream of data from a goroutine and consuming it in the main function, you can use a channel to communicate between the two goroutines without needing to use a WaitGroup.

特に上記コードでは、シンプルにgoroutineの終了を待ち合わせたいだけなので、WaitGroupで必要十分。

## channelのみを使用するパターン
### unbuffered（バッファサイズなし）のchannel
```go
func do(ch chan string) {
	ch <- "Hello from goroutine 1"
	ch <- "Hello from goroutine 2"
}

func main() {
	ch := make(chan string)
	fmt.Println("Starting goroutine.")
	go do(ch)
	fmt.Println(<-ch)
	fmt.Println(<-ch)
	fmt.Println("Finished.")
}
```
```
Starting goroutine.
Hello from goroutine 1
Hello from goroutine 2
Finished.
```

FIFOキューであるchannelに２つデータを送信し、２つ受信している。  
このとき、もう一行足して次のようにすると、
```go
func main() {
	ch := make(chan string)
	fmt.Println("Starting goroutine.")
	go do(ch)
	fmt.Println(<-ch)
	fmt.Println(<-ch)
	fmt.Println(<-ch)
	fmt.Println("Finished.")
}
```
```
Starting goroutine.
Hello from goroutine 1
Hello from goroutine 2
fatal error: all goroutines are asleep - deadlock!

goroutine 1 [chan receive]:
main.main()
	/tmp/sandbox3749670160/prog.go:18 +0x198
```
デッドロックが発生する。  

キャパシティが満タンのchannelへの書き込みは、空きが出るまで待機をし、空のchannelからの読み出しは、少なくとも要素が１つ入るまで待機をする。

channelがどのタイミングでブロックを解除するのかわかりやすい例として、
```go
func do(ch chan string) {
	defer fmt.Println("goroutine finished.")
	ch <- "Hello from goroutine 1"
	ch <- "Hello from goroutine 2"
}

func main() {
	ch := make(chan string)
	fmt.Println("Starting goroutine.")
	go do(ch)
	fmt.Println(<-ch)
	fmt.Println(<-ch)
	fmt.Println("Finished.")
}
```
このコードの`defer fmt.Println()`は実行されない。
```
Starting goroutine.
Hello from goroutine 1
Hello from goroutine 2
Finished.
```
２つめの`fmt.Println(<-ch)`が実行された時点でchannelのブロックが解除されるので、goroutineの終了を待たずにmain関数が終了している。

### buffered channel
```go
func do(ch chan string) {
	ch <- "Hello from goroutine 1"
	ch <- "Hello from goroutine 2"
}

func main() {
	ch := make(chan string, 3)
	fmt.Println("Starting goroutine.")
	go do(ch)
	fmt.Println(<-ch)
	fmt.Println(<-ch)
	fmt.Println("Finished.")
}
```
```
Starting goroutine.
Hello from goroutine 1
Hello from goroutine 2
Finished.
```
buffered channelはキャパシティありのFIFOキューとなる。  
この場合、キャパシティを1にしてもプログラムは正常終了する。

1. １つ書き込む
2. １つ読み出す
3. １つ書き込む
4. １つ読み出す

という流れになるので、キャパシティを超えた書き込みをしてはいけないわけではない。ただしこの場合、前述したように、空きが出るまで書き込みの段階で待機が発生する。

buffered channelから`for range`で値を読み出そうとすると、存在しない値を読み出そうとしてデッドロックになる。
```go
func do(ch chan string) {
	ch <- "Hello from goroutine 1"
	ch <- "Hello from goroutine 2"
}

func main() {
	ch := make(chan string, 2)
	fmt.Println("Starting goroutine.")
	go do(ch)
	for msg := range ch {
		fmt.Println(msg)
	}
	fmt.Println("Finished.")
}
```
```
Starting goroutine.
Hello from goroutine 1
Hello from goroutine 2
fatal error: all goroutines are asleep - deadlock!
```
これを回避するために、書き込みが終わったchannelはcloseしておく。
```go
func do(ch chan string) {
	defer close(ch)
	ch <- "Hello from goroutine 1"
	ch <- "Hello from goroutine 2"
}
```
```
Starting goroutine.
Hello from goroutine 1
Hello from goroutine 2
Finished.
```
`for range`はchannelがcloseされたときに自動的にループを終了してくれる。

### close(ch)の応用
「Go言語による並行処理」に面白い例が掲載されている。channelをcloseすることで複数のgoroutineにシグナルを送れるということ、そして閉じたchannelからは（データがなくても）無限に読み出しができるというということを利用したもの。

```go
func main() {
	var wg sync.WaitGroup
	ch := make(chan interface{})
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			<-ch // channelが読み出し可能になるまで待機する
			fmt.Println(fmt.Sprint(i) + " has begun.")
		}(i)
	}

	fmt.Println("Unblocking goroutines...")
	close(ch) // 閉じることで無限読み出しを可能にする
	wg.Wait()
}
```
```
Unblocking goroutines...
1 has begun.
0 has begun.
2 has begun.
3 has begun.
4 has begun.
```

たとえば１つだけgoroutineを動かしておいて、あとはchannelをcloseしてシグナルを送ってから動かしたいというような場合は、サイズ0の空の構造体を送ることで１つだけ解放できる。
```go
func main() {
	var wg sync.WaitGroup
	ch := make(chan interface{})
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			<-ch
			fmt.Println(fmt.Sprint(i) + " has begun.")
		}(i)
	}

	ch <- struct{}{} // １つだけgoroutineのブロックを解除する
	fmt.Println("Unblocking other goroutines...")
	close(ch)
	wg.Wait()
}
```
```
4 has begun.
Unblocking other goroutines...
1 has begun.
2 has begun.
3 has begun.
0 has begun.
```

## WaitGroupとchannelの併用時の注意点
上記のコードで、以下のように`close(ch)`と`wg.Wait()`を入れ替えるとデッドロックが発生する。
```go
func main() {
	var wg sync.WaitGroup
	ch := make(chan interface{})
...
	ch <- struct{}{}
	fmt.Println("Unblocking other goroutines...")
	wg.Wait()
	close(ch)
}
```

```
4 has begun.
Unblocking other goroutines...
fatal error: all goroutines are asleep - deadlock!

goroutine 1 [semacquire]:
sync.runtime_Semacquire(0xc0000781a0?)
	/usr/local/go-faketime/src/runtime/sema.go:62 +0x25
sync.(*WaitGroup).Wait(0x4b37f8?)
	/usr/local/go-faketime/src/sync/waitgroup.go:116 +0x48
main.main()
	/tmp/sandbox1058644992/prog.go:22 +0x171

goroutine 6 [chan receive]:
main.main.func1(0x0?)
	/tmp/sandbox1058644992/prog.go:15 +0x5b
created by main.main in goroutine 1
	/tmp/sandbox1058644992/prog.go:13 +0x4c

goroutine 7 [chan receive]:
main.main.func1(0x0?)
	/tmp/sandbox1058644992/prog.go:15 +0x5b
created by main.main in goroutine 1
	/tmp/sandbox1058644992/prog.go:13 +0x4c

goroutine 8 [chan receive]:
main.main.func1(0x0?)
	/tmp/sandbox1058644992/prog.go:15 +0x5b
created by main.main in goroutine 1
	/tmp/sandbox1058644992/prog.go:13 +0x4c
```
channelがcloseされないとWaitGroupのタスクカウントが減らないのに、closeするためにはWaitGroupのタスクが０にならないといけないから。ビルド時には検出してくれない。  
上記のコードはシンプルなのでさすがに気づきやすいが、入り組んだロジックを書く場合は気をつけないとふつうにハマりそうなので注意したい。