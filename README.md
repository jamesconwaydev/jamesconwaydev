<!--
  Most of this file is hand-written, but not all of it. The project cards
  between the FEATURED and CARDS markers, and the posts between the BLOG
  markers, get rewritten by `python -m scripts.build refresh`, so any edit
  you make in there will vanish on the next run. Change projects.json to swap projects.
-->

<p align="center">
<a href="https://jamesconway.dev"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg"><img src="assets/header-light.svg" alt="James Conway's website. I build software that solves real problems. Self-hosted business software, high-performance developer tools, linux infrastructure."></picture></a>
</p>

<p align="center">
<a href="https://jamesconway.dev"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/icon-web-dark.svg"><img src="assets/icon-web-light.svg" alt="jamesconway.dev" width="48"></picture></a>
<a href="https://www.linkedin.com/in/jamesjconway/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/icon-linkedin-dark.svg"><img src="assets/icon-linkedin-light.svg" alt="James Conway on LinkedIn" width="48"></picture></a>
<a href="https://x.com/jamesconway"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/icon-x-dark.svg"><img src="assets/icon-x-light.svg" alt="James Conway on X" width="48"></picture></a>
<a href="https://mastodon.social/@jamesconway"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/icon-mastodon-dark.svg"><img src="assets/icon-mastodon-light.svg" alt="James Conway on Mastodon" width="48"></picture></a>
<a href="https://bsky.app/profile/jamesconway.dev"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/icon-bluesky-dark.svg"><img src="assets/icon-bluesky-light.svg" alt="James Conway on Bluesky" width="48"></picture></a>
</p>

<p align="center">
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/follow-dark.svg"><img src="assets/follow-light.svg" alt="Follow me: the button is in the sidebar to the left"></picture>
</p>

## Featured Project

<!-- FEATURED:START -->
<p>
<a href="https://github.com/conn3xorg/conn3x"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-conn3xorg-conn3x-featured-dark.svg"><img src="assets/card-conn3xorg-conn3x-featured-light.svg" alt="conn3xorg/conn3x: One binary to provision and configure your infrastructure." width="804"></picture></a>
</p>
<!-- FEATURED:END -->

## My Top Open Source Projects

<!-- CARDS:START -->
<p>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/label-high-performance-developer-tools-dark.svg"><img src="assets/label-high-performance-developer-tools-light.svg" alt="High-performance developer tools"></picture><br>
<a href="https://github.com/netweir/netweir"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-netweir-netweir-dark.svg"><img src="assets/card-netweir-netweir-light.svg" alt="netweir/netweir: An ultra-fast, self-healing, undetectable web scraper. Rust does the work; you write Python." width="400"></picture></a>
<a href="https://github.com/tachyon-cms/tachyoncms"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-tachyon-cms-tachyoncms-dark.svg"><img src="assets/card-tachyon-cms-tachyoncms-light.svg" alt="tachyon-cms/tachyoncms: Rust-powered, ultra-fast, highly secure headless CMS" width="400"></picture></a>
</p>

<p>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/label-linux-infrastructure-dark.svg"><img src="assets/label-linux-infrastructure-light.svg" alt="Linux infrastructure"></picture><br>
<a href="https://github.com/jamesconwaydev/aegis-v2"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-jamesconwaydev-aegis-v2-dark.svg"><img src="assets/card-jamesconwaydev-aegis-v2-light.svg" alt="jamesconwaydev/aegis-v2: Automated Ephemeral Honeypot &amp; Zero-Trust Runtime Quarantine Engine" width="400"></picture></a>
<a href="https://github.com/jamesconwaydev/sentry-v2"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-jamesconwaydev-sentry-v2-dark.svg"><img src="assets/card-jamesconwaydev-sentry-v2-light.svg" alt="jamesconwaydev/sentry-v2: Watches cgroup v2 pressure, systemd failures and SELinux denials on Rocky/RHEL 10, and applies reversible, time-boxed fixes before the OOM killer has to." width="400"></picture></a>
</p>

<p>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/label-self-hosted-business-software-dark.svg"><img src="assets/label-self-hosted-business-software-light.svg" alt="Self-hosted business software"></picture><br>
<a href="https://github.com/Sentrello/Sentrello"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-sentrello-sentrello-dark.svg"><img src="assets/card-sentrello-sentrello-light.svg" alt="Sentrello/Sentrello: Unified Business Management Platform (UBM)" width="400"></picture></a>
<a href="https://github.com/ticketslinger/ticketslinger"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-ticketslinger-ticketslinger-dark.svg"><img src="assets/card-ticketslinger-ticketslinger-light.svg" alt="ticketslinger/ticketslinger: The worlds greatest open-source ticket selling platform in the making." width="400"></picture></a>
</p>
<!-- CARDS:END -->

## Latest from Out of Memory

<!-- BLOG:START -->
`2026-10-25` · **[Two Tools, One Job: Why I Started Building Conn3x](https://jamesconway.dev/blog/why-i-started-conn3x/)**<br>I've started building Conn3x: one Go binary that creates your servers and configures them in the same plan. It's early, and I'm aiming for the CNCF.

`2026-10-23` · **[I Built the Smoke Detector Before the Fire](https://jamesconway.dev/blog/i-built-the-smoke-detector-before-the-fire/)**<br>Aegis v2 is an open-source eBPF tool that watches process behaviour on Rocky Linux 10, adds the warning signs into one score, and records one incident.

`2026-10-10` · **[Apparently, I Don't Know How to Build Small Projects](https://jamesconway.dev/blog/apparently-i-dont-know-how-to-build-small-projects/)**<br>Sentrello wasn't enough, so I built NetWeir: a Rust-core, Python-API web scraper, days old and public on GitHub. One more project still to come.

[Read the rest on jamesconway.dev →](https://jamesconway.dev/blog/)
<!-- BLOG:END -->

<p align="center">
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/footer-dark.svg"><img src="assets/footer-light.svg" alt="" width="900"></picture>
</p>
