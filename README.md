# Django Panpub

**Warning: still in really early-stage, no migration guaranteed**

Panpub, from *pan* ("all, of everything") and *publishing*. A Django publishing app providing united streamlined outputs from centralised normalised inputs.


## Targets

* **Medium openness**: widely-used media - writing, picture, audio and video - with outside link as a fall-back option
* **Living culture**: claims of participation (whether as creator, curator or mediator) available for each unique content
* **Batteries included**: delicious base of models, decorators and templatetags, with its standard topping of views, forms, urls and templates


## Ecosystem

Main classes: *Corpus*, *Content*, *Crafter*, *Claim*

Decorator: has_any_claim, has_creator_claim, has_curator_claim, has_mediator_claim

Templatetags: crafterworks


## Writing

Main class: *Text*

Available inputs: .md (pandoc-standard or github-flavored), .latex, .docx, .odt, .html, .rst, native Haskell

In-house format: Markdown (pandoc-flavored)

Available outputs: md, html, pdf, .ebook (none implemented yet)

Templatetags: craftertexts


## Spoilers

* Picture medium: Pillow-fed input, with opt-in EXIF-cleaner and LSB-smoother (a.k.a. *anti-steganography**)
* pandoc auto-installation
* and even more !

