+++
title = "How to use Google Domains with Netlify"
date = 2021-04-30
math = false
[taxonomies]
categories = ["blog"]
tags = ["Netlify", "Google Domains"]
+++
I recently jumped into Netlify-hosted from other server. This article is about how to use Google Domains with Netlify (and why GitLab pages with custom domain is *bad*).

First of all, Options of hosting service I had in mind were:

- Firebase
- GitLab pages
- Netlify

Firebase seemed good for dynamic site, but this site is powered by Zola (a fantastic static site generator) so, well, I don't use it for now.

Next, GitLab pages. OK I use GitLab for my main repository-hosting service, and it's been great. So I thought GitLab pages with custom domain was natural and might be easy.

It was not. Using custom domain in GitLab pages is hard. I do not recommend this setup.

### Why?
Because its document is broken.

In [official tutorial](https://docs.gitlab.com/ee/user/project/pages/custom_domains_ssl_tls_certification/), they say "set the A record to foo, and TXT record to bar." But in the settings page of custom domain, I'm told to set CNAME and TXT. What's going on?

Actually I tried both. Neither did work. Though time might solve this (due to TTL? Note that I've waited for 1 day), I felt like, OK this is enough.

### resource records for Netlify
So, I went to Netlify, which I've used as an example site for my Zola theme. In `DNS >> resource records` set as following and, voila, it's done:

name | type | TTL | data
:-- | :-- | :-- | :--
@ | A | 10m(or whatever you like) | 75.2.60.5
www | CNAME | same as above | YOURSITENAME.netlify.app.

Netlify automatically set the TLS certificate with Let's Encrypt a few minutes after check for DNS configuration. This was a good experience, so I highly recommend Netlify over GitLab pages, at least for now.