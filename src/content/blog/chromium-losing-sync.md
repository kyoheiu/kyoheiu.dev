+++
title = "Chromium losing Sync support on March 15"
date = 2021-02-05
math = false
[taxonomies]
categories = ["blog"]
tags = ["Google", "Chromium", "security", "linux"]
+++
### 経緯

[Chromium Blog: Limiting Private API availability in Chromium](https://blog.chromium.org/2021/01/limiting-private-api-availability-in.html)

> During a recent audit, we discovered that some third-party Chromium based browsers were able to integrate Google features, such as Chrome sync and Click to Call, that are only intended for Google’s use. This meant that a small fraction of users could sign into their Google Account and store their personal Chrome sync data, such as bookmarks, not just with Google Chrome, but also with some third-party Chromium based browsers. We are limiting access to our private Chrome APIs starting on March 15, 2021.

Google提供のChromiumパッケージ以外のChromium、そしてChromiumベースのブラウザにおいて、ブックマークデータのsyncなど、「Googleによる利用のみが想定されていたAPI」の利用がみられることが「分かった」ので、このAPIの利用を21年3月15日より制限することにした、というのがGoogle側の話である。

[Arch Linux - News: Chromium losing Sync support in early March](https://archlinux.org/news/chromium-losing-sync-support-in-early-march/)

> Google has announced that they are going to block everything but Chrome from accessing certain Google features (like Chrome sync) starting on March 15. This decision by Google is going to affect Arch's chromium package a bit earlier, on March 2, when Chromium 89 gets released.

これを受けて、各ディストリビューションのメンテナも対応を迫られている。Arch Linux版はGoogleによる制限の前に先んじてAPI利用を停止する模様。

### Googleの方針転換

しかし、このGoogle側の言い分には事実でない情報が含まれているようだ。
以下のブログの記事を読んでみる。

[What’s The Deal With Chromium On Linux? Google At Odds With Package Maintainers | Hackaday](https://hackaday.com/2021/01/26/whats-the-deal-with-chromium-on-linux-google-at-odds-with-package-maintainers/)

> As developer Eric Hameleers explains in a lengthy blog post, he was supplied with a dedicated API key for his Slackware Chromium builds by the Google Chrome Team in 2013. He was granted “official permission to include Google API keys in your packages”, and was told that the usage quota for that particular key would be increased “in an effort to adequately support your users”, as normally the key he was assigned would only be for personal development use. Evangelos Foutras, the maintainer for the Arch Linux Chromium package, has indicated he received a similar email at around the same time.

[Re: \[Action Required\] Update on Google API usage in Chromium](https://groups.google.com/a/chromium.org/g/chromium-packagers/c/SG6jnsP4pWM/m/Kr0KlsL8CQAJ?pli=1)

Arch LinuxのChromiumパッケージのメンテナ・Evangelos Foutras氏の上記書き込みによると、このAPIは実は、2013年ごろにGoogleのChrome開発チームから「公式に再配布が認められていないものを、配布用に提供する」とのメッセージとともに送られたものだという。とすると、少なくともこのAPIの利用が各ディストリビューションのパッケージにおいて始まったタイミングでは、Google側はAPIがサードパーティーによって利用されていることは認識していたし、むしろそれを促進していたということになる。今回の方針転換が、API制限以上の何を示唆しているのかは、それぞれに感じるところがあるだろう。

### セキュリティ問題

これを受けてのコミュニティの主な反応としては当然、「各ディストリビューションのChromiumパッケージにおいてsyncが行えなくなること」、そして「Googleが提供しているプロプライエタリなChrome、そしてChromiumと比して価値が低落すること」を否定的に受け止め、他ブラウザへ移行するという声が多い。
しかしどうも話は単に「便利機能の制限」にとどまらないようだ。Foutras氏によると、このAPI制限によりセーフブラウンジング機能もdisabledにされる可能性があるとのこと。Safe Browsing Testing Linksでテストすると、[セーフブラウジング機能による警告が動かなかった](https://groups.google.com/a/chromium.org/g/chromium-packagers/c/SG6jnsP4pWM/m/OOxl9wKLAAAJ)という。これは利便性がどうこうという話以前の、深刻なトラブルにつながりかねない変更だ。

### メンテナの反応

この件については、上記のパッケージメンテナ諸氏による議論のほか、SlackwareのChromiumパッケージのメンテナ・Eric Hameleers氏のブログ記事も大変読み応えがある（[Google muzzles all Chromium browsers on 15 March 2021 | Alien Pastures](https://alien.slackbook.org/blog/google-muzzles-all-chromium-browsers-on-15-march-2021/)）。普段パッケージを好き勝手に使わせてもらっている身としては、これらの発言の奥にある感情を想像せずにはいられない。