# Django Panpub

**Warning: early-stage dev**

Panpub, from *pan* ("all, of everything") and *publishing*. A Django publishing app providing united streamlined outputs from centralised normalised inputs, with an embedded system of claims regarding each content and role (*creator*, *curator*, *mediator*).


## Directions

* **Medium openness**: widely-used media - writing, picture, audio and video - with outside link as a fall-back option
* **Access first**: various commonly-used formats for import and export
* **Living culture**: claims of participation (whether as creator, curator or mediator) available for each unique content
* **Batteries included**: delicious base of models, decorators and templatetags, with its standard topping of views, forms, urls and templates for reuse


## Achieved features
* Panpub ecosystem: claim system, corpus creation, system-wide exporting
* Text model: use of pandoc as the middleman, upload and download


## Requirements
* Python3
* Django
* pandoc

## Ecosystem

* models: Corpus, Content, Crafter, Claim
* decorators: has_any_claim, has_creator_claim, has_curator_claim, has_mediator_claim
* templatetags: crafterworks
* utils: panpub_export


## Writing

* main class: Text
* inputs: .md (*pandoc-standard* or *github-flavored*), .latex, .docx, .odt, .html, .rst, native Haskell
* in-house: markdown (*pandoc-standard*)
* ouputs: .md (*pandoc-standard* or *github-flavored*), .html, .docx, .epub, .odt
* templatetags: craftertexts


## Spoilers

* Text medium: fixing integration of xetex and adding .pdf to the outputs, extending .md and .latex plugins
* Picture medium: Pillow-fed input, with opt-in EXIF-cleaner and LSB-smoother (a.k.a. *anti-steganography**)
* Dataset medium: Tablib-fed input
* pandoc auto-installation
* and even more !

