#!/usr/bin/env python3
"""Generate data/translations/*.yaml for flyer scans and link them in issue YAMLs."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS_DIR = ROOT / "data" / "translations"
ISSUES_DIR = ROOT / "data" / "issues" / "flyers"

LICENSE = (
    "Scan © malice-mizer.info / Malice Meezer (as credited per flyer). "
    "Translation for research/archival use; verify against physical copy where possible."
)

FLYERS: list[dict] = [
    {
        "id": "flyers-2000-02-01-shinwa-front",
        "article_id": "flyers-2000-02-01-shinwa-front",
        "issue_file": "2000-releases.yaml",
        "title_ja": "神話 release flyer (front)",
        "title_en": "Shinwa (Myth) — Kami memorial box flyer (front)",
        "publication_date": "2000-02-01",
        "scan": "images/flyers/flyers-2000-02-01-shinwa-front.webp",
        "section": "Front",
        "ja": """Kami's MEMORIAL BOX — Mini Album & Video —
『神話』 2000.2.1 RELEASE
Kamiが残した曲をメンバーが完成させた初めての作品集
& MALICE MIZERの未公開映像で綴ったメモリアルビデオ
MMCD-009 ¥4,410(tax in)
New Single & Video Single Now On Sale
再会の血と薔薇
<CD> 特製BOOK仕様 MMCD-006 ¥1,260(tax in)
<VT> 未公開写真20P豪華ブックレット付 MMVC-004 ¥1,890(tax in)""",
        "romaji": """Kami's MEMORIAL BOX — Mini Album & Video —
"Shinwa" 2000.2.1 RELEASE
Kami ga nokoshita kyoku o menbā ga kansei saseta hajimete no sakuhinshū
& MALICE MIZER no mikōkai eizō de tsuzutta memoriaru bideo
MMCD-009 ¥4,410 (tax in)
New Single & Video Single Now On Sale
Saikai no Chi to Bara
<CD> tokusei BOOK shiyō MMCD-006 ¥1,260 (tax in)
<VT> mikōkai shashin 20P gōka bukuretto tsuki MMVC-004 ¥1,890 (tax in)""",
        "en": """Kami's MEMORIAL BOX — mini album & video —
Shinwa (Myth) — release 1 Feb 2000.
The first collection of works where the members completed songs Kami left behind,
plus a memorial video compiled from unreleased MALICE MIZER footage (MMCD-009, ¥4,410 tax in).
Also on sale: new single & video single Blood and Roses of Reunion (Saikai no Chi to Bara).
CD special book edition MMCD-006 ¥1,260; VT with 20-page deluxe booklet of unreleased photos MMVC-004 ¥1,890.""",
    },
    {
        "id": "flyers-2000-02-01-shinwa-back",
        "article_id": "flyers-2000-02-01-shinwa-back",
        "issue_file": "2000-releases.yaml",
        "title_ja": "神話 release flyer (back)",
        "title_en": "Shinwa (Myth) — memorial message (back)",
        "publication_date": "2000-02-01",
        "scan": "images/flyers/flyers-2000-02-01-shinwa-back.webp",
        "section": "Back",
        "ja": """『神話』
1999年6月 Kamiは時間のない永遠の世界へと旅立ちました。
けれども彼の精神は私たちとともに歩み続けていると考えています。
そしてMALICE MIZERのメンバーであるKamiが初めて書いた曲を
私たちの想いをこめて完成させ、彼の誕生日に発表しようと決めました。
曲を完成させていくにつれて、彼のメロディーが表情をもち始め、
まるで私たちに話しかけてくるようでした。
Kamiの心の旋律が胸に響き、あなたの持つ言葉、
心が重なり合った時
そこから神話が生まれる･･･。""",
        "romaji": """"Shinwa"
1999-nen 6-gatsu, Kami wa jikan no nai eien no sekai e to tabidachi mashita.
Keredomo kare no seishin wa watashitachi to tomo ni ayumi tsuzukete iru to kangaete imasu.
Soshite MALICE MIZER no menbā de aru Kami ga hajimete kaita kyoku o
watashitachi no omoi o komete kansei sasete, kare no tanjōbi ni happyō shiyō to kimemashita.
Kyoku o kansei sasete iku ni tsurete, kare no merodī ga hyōjō o mochi hajime,
marude watashitachi ni hanashikakete kuru yō deshita.
Kami no kokoro no senritsu ga mune ni hibiki, anata no motsu kotoba,
kokoro ga kasanariau toki
soko kara shinwa ga umareru…""",
        "en": """Shinwa (Myth)
In June 1999, Kami departed for an eternal world without time.
Yet we believe his spirit continues to walk with us.
We decided to complete the first song Kami wrote as a member of MALICE MIZER,
filling it with our feelings, and release it on his birthday.
As we finished the song, his melody began to take on expression,
as if speaking to us.
When Kami's melody resonates in your heart and your words
and feelings overlap—
a myth is born from that moment…""",
    },
    {
        "id": "flyers-2000-05-31-kyomu",
        "article_id": "flyers-2000-05-31-kyomu",
        "issue_file": "2000-releases.yaml",
        "title_ja": "虚無の中での遊戯 release flyer",
        "title_en": "Kyomu no Naka de no Yūgi — single & video single flyer",
        "publication_date": "2000-05-31",
        "scan": "images/flyers/flyers-2000-05-31-kyomu.webp",
        "section": "Flyer",
        "ja": """NEW SINGLE
日本テレビ系全国30局ネット「号外!!爆笑大問題」エンディングテーマ
虚無の中での遊戯
MMCD-010 ¥1,260(tax in)
VIDEO SINGLE
虚無の中での遊戯 〜de l'image〜
MMVC-011 ¥1,680(tax in)
SINGLE & VIDEO 2000.5.31 DOUBLE RELEASE
SINGLE & VIDEO両方ご予約いただいた方に先着で特製ポストカードをプレゼント!
詳細はご予約の際、店頭でお問い合わせください。一部レコード店で取り扱わない場合がございます。ご了承ください。""",
        "romaji": """NEW SINGLE
Nippon Terebi-kei zenkoku 30-kyoku netto "Gougai!! Bakushou Daimondai" endingu tēma
Kyomu no Naka de no Yūgi
MMCD-010 ¥1,260 (tax in)
VIDEO SINGLE
Kyomu no Naka de no Yūgi ~de l'image~
MMVC-011 ¥1,680 (tax in)
SINGLE & VIDEO 2000.5.31 DOUBLE RELEASE
SINGLE & VIDEO ryōhō go-yoyaku itadaita kata ni senchaku de tokusei posutokādo o purezento!
Shōsai wa go-yoyaku no sai, tentō de o-toiawase kudasai. Ichibu rekōdo-ten de toriatsukawanai baai ga gozaimasu. Go-ryōshō kudasai.""",
        "en": """NEW SINGLE — ending theme for NTV's nationwide "Gougai!! Bakushou Daimondai."
Kyomu no Naka de no Yūgi (A Game in the Void) — MMCD-010 ¥1,260 tax in.
VIDEO SINGLE — Kyomu no Naka de no Yūgi ~de l'image~ — MMVC-011 ¥1,680 tax in.
Double release 31 May 2000.
First-come postcard gift for customers who pre-order both single and video; ask at the store for details.
Not available at all record shops.""",
    },
    {
        "id": "flyers-2000-08-03-bara-no-seidou-front",
        "article_id": "flyers-2000-08-03-bara-no-seidou-front",
        "issue_file": "2000-releases.yaml",
        "title_ja": "薔薇の聖堂 release flyer (front)",
        "title_en": "Bara no Seidō (Sanctuary of the Rose) — album flyer (front)",
        "publication_date": "2000-08-03",
        "scan": "images/flyers/flyers-2000-08-03-bara-no-seidou-front.webp",
        "section": "Front",
        "ja": """薔薇の聖堂
MMCD-017 ¥3,770(tax in) 初回限定: A5サイズ特殊BOOK仕様
第3章 SINGLE
白い肌に狂う愛と哀しみの輪舞 NOW ON SALE""",
        "romaji": """Bara no Seidō
MMCD-017 ¥3,770 (tax in) shokai gentei: A5 saizu tokushu BOOK shiyō
Dai 3-shō SINGLE
Shiroi hada ni kuruu ai to kanashimi no rinbu NOW ON SALE""",
        "en": """Bara no Seidō (Sanctuary of the Rose) — MMCD-017 ¥3,770 tax in.
First-press limited A5 special book edition.
Chapter 3 single: Shiroi Hada ni Kuruu Ai to Kanashimi no Rinbu
(A Rondo of Love and Sorrow Gone Mad on White Skin) — now on sale.""",
    },
    {
        "id": "flyers-2000-08-03-bara-no-seidou-back",
        "article_id": "flyers-2000-08-03-bara-no-seidou-back",
        "issue_file": "2000-releases.yaml",
        "title_ja": "薔薇の聖堂 release flyer (back)",
        "title_en": "Bara no Seidō — TV special & Budokan flyer (back)",
        "publication_date": "2000-08-03",
        "scan": "images/flyers/flyers-2000-08-03-bara-no-seidou-back.webp",
        "section": "Back",
        "ja": """薔薇に導かれた全ての存在が宿命のもとに巡り着く
薔薇の聖堂
今　最後の扉は開かれた
TV特番 MALICE MIZER 薔薇の肖像 ～新たなる悪意と悲劇の幕開け～
マリス ミゼルの辿ってきた激動の日々　その深淵から生まれた内なる想い
そして　その見つめる先にあるものは…
すべての封印を解き　マリス ミゼル 運命の物語が　今、明かされる…
「薔薇に彩られた悪意と悲劇の幕開け」
第一夜 再会の薔薇 / 第二夜 約束の薔薇
8/31 THU. 9/1 FRI. 日本武道館 OPEN-18:00 START-19:00
全席指定・S席 即日 SOLD OUT!
ステージプラン決定に伴い、8/12よりA席・立見券追加発売""",
        "romaji": """Bara ni michibikareta subete no sonzai ga shukumei no moto ni meguritsuku
Bara no Seidō
Ima saigo no tobira wa hirakareta
TV tokuban MALICE MIZER Bara no Shōzō ~Aratanaru akui to higeki no makuake~
Marisu Mizeru no tadoritte kita gekidō no hibi, sono shinen kara umareta uchinaru omoi
Soshite sono mitsumeru saki ni aru mono wa…
Subete no fūin o toki, Marisu Mizeru unmei no monogatari ga ima, akasareru…
"Bara ni irodorareta akui to higeki no makuake"
Dai ichiya Saikai no Bara / Dai niya Yakusoku no Bara
8/31 THU. 9/1 FRI. Nippon Budōkan OPEN 18:00 START 19:00
Zenseki shitei, S-seki sokujitsu SOLD OUT!
Sutēji puran kettei ni tomonai, 8/12 yori A-seki, tachimi-ken tsuika hatsubai""",
        "en": """All beings guided by the rose arrive at their destiny.
Sanctuary of the Rose — now the final door has opened.
TV special: MALICE MIZER — Portrait of the Rose ~The Beginning of New Malice and Tragedy~
The turbulent days Malice Mizer has walked; inner feelings born from that abyss…
Breaking every seal, the story of their fate is revealed.
Live: "The Beginning of Malice and Tragedy Colored by Roses"
Night 1: Rose of Reunion / Night 2: Rose of Promise
31 Aug & 1 Sep 2000, Nippon Budokan. Reserved seating; S seats sold out on day one.
Additional A seats and standing tickets from 12 Aug after stage plan finalized.""",
    },
    {
        "id": "flyers-2000-11-22-budokan-vhs",
        "article_id": "flyers-2000-11-22-budokan-vhs",
        "issue_file": "2000-releases.yaml",
        "title_ja": "薔薇に彩られた悪意と悲劇の幕開け VHS/DVD flyer",
        "title_en": "Budokan live VHS/DVD flyer",
        "publication_date": "2000-11-22",
        "scan": "images/flyers/flyers-2000-11-22-budokan-vhs.webp",
        "section": "Flyer",
        "ja": """薔薇に彩られた悪意と悲劇の幕開け
第一夜 再会の薔薇　第二夜 約束の薔薇
2000.11.22 RELEASE
2000.8.31 & 9.1 に日本武道館で行われた公演の模様を1本にまとめたビデオ＆DVD
アルバム「memoire」に収録されている「記憶と空」のリアレンジ・ヴァージョンや新曲2曲を含む全17曲
今回ボーナスショットとしてバックステージの模様を収録
[VHS] MMVC-014 ¥6,090(tax in) 84min
[DVD] MMBV-011 ¥6,510(tax in) 89min""",
        "romaji": """Bara ni irodorareta akui to higeki no makuake
Dai ichiya Saikai no Bara, Dai niya Yakusoku no Bara
2000.11.22 RELEASE
2000.8.31 & 9.1 ni Nippon Budōkan de okonawareta kōen no sugata o ippon ni matometa bideo & DVD
Arubamu "memoire" ni shūroku sarete iru "Kioku to Sora" no riarange vājon ya shinkyoku 2-kyoku o fukumu zen 17-kyoku
Konkai bōnasu shotto toshite bakkusutēji no sugata o shūroku
[VHS] MMVC-014 ¥6,090 (tax in) 84min
[DVD] MMBV-011 ¥6,510 (tax in) 89min""",
        "en": """The Beginning of Malice and Tragedy Colored by Roses
Night 1: Rose of Reunion / Night 2: Rose of Promise — release 22 Nov 2000.
Video & DVD compiling both 31 Aug and 1 Sep 2000 Nippon Budokan performances.
17 songs including rearranged "Kioku to Sora" from memoire and two new tracks;
bonus backstage footage included.
VHS MMVC-014 ¥6,090 (84 min); DVD MMBV-011 ¥6,510 (89 min).""",
    },
    # --- 1992–1994 live era (Malice Meezer scans) ---
    {
        "id": "flyers-1992-08-debut-era",
        "article_id": "flyers-1992-08-debut-era",
        "issue_file": "1992-1994-live.yaml",
        "title_ja": "Malice Mizer flyer (1992)",
        "title_en": "Malice Mizer debut-era flyer (1992)",
        "publication_date": "1992-08",
        "scan": "images/flyers/flyers-1992-08-debut-era.webp",
        "section": "Band profile",
        "ja": """92年8月に結成されたMalice Mizer。他に類を見ないTWIN GUITARの曲構成、不思議なコントラストで迫るBass、アグレッシブかつ狂気的なリズムを打ち出すDrum。その全てを包み込み、見る者の感情を逆なでるVocal、美しさと哀しみの旋律（戦慄）により、懐かしい記憶が今、甦る。
メンバー名: TETSU(Vo) MANA(G) Ko-Zi(GSyn) YUKI(B) Kami(Dr)
主な活動場所: 目黒鹿鳴館、市川クラブGIO、新宿LOFT
バンドの目標: 全世界をMalice Mizer Soundで包み込む!!
LIVE: 12/25 目黒ライヴステーション、29 心斎橋ミューズホール""",
        "romaji": """1992-nen 8-gatsu ni kessei sareta Malice Mizer…
Menbā: TETSU (Vo), MANA (G), Ko-Zi (GSyn), YUKI (B), Kami (Dr)
Shuyō katsudō basho: Meguro Rokumeikan, Ichikawa Club GIO, Shinjuku LOFT
Band no mokuhyō: zen sekai o Malice Mizer Sound de tsutsumikomu!!
LIVE: 12/25 Meguro Live Station, 29 Shinsaibashi Muse Hall""",
        "en": """Malice Mizer formed August 1992 — twin-guitar songs, contrasting bass, aggressive drums,
and vocals that stir the listener's emotions with beauty and sorrow.
Members: Tetsu (vo), Mana (g), Közi (g/synth), Yu~ki (b), Kami (dr).
Main venues: Meguro Rokumeikan, Ichikawa Club GIO, Shinjuku LOFT.
Goal: envelop the whole world in the Malice Mizer sound.
Dec 25 Meguro Live Station; Dec 29 Shinsaibashi Muse Hall.""",
    },
    {
        "id": "flyers-1993-06-live-1993",
        "article_id": "flyers-1993-06-live-1993",
        "issue_file": "1992-1994-live.yaml",
        "title_ja": "Se-duc-tive Tour '93 flyer",
        "title_en": "Se-duc-tive Tour '93 — live dates",
        "publication_date": "1993-06",
        "scan": "images/flyers/flyers-1993-06-live-1993.webp",
        "section": "Tour dates",
        "ja": """Se-duc-tive Tour '93
8/9 横浜MONSTER
8/11 大阪難波ROCKETS
8/13 名古屋MUSIC FARM
8/17 水戸LIGHT HOUSE
8/19 長野JUNK BOX
8/21 前橋J
8/27 川崎CLUB CITTA'""",
        "romaji": """Se-duc-tive Tour '93
8/9 Yokohama MONSTER
8/11 Osaka Namba ROCKETS
8/13 Nagoya MUSIC FARM
8/17 Mito LIGHT HOUSE
8/19 Nagano JUNK BOX
8/21 Maebashi J
8/27 Kawasaki CLUB CITTA'""",
        "en": """Se-duc-tive Tour '93 — Aug 9 Yokohama MONSTER; Aug 11 Osaka Namba ROCKETS;
Aug 13 Nagoya MUSIC FARM; Aug 17 Mito LIGHT HOUSE; Aug 19 Nagano JUNK BOX;
Aug 21 Maebashi J; Aug 27 Kawasaki CLUB CITTA'.""",
    },
    {
        "id": "flyers-1994-01-live-1994",
        "article_id": "flyers-1994-01-live-1994",
        "issue_file": "1992-1994-live.yaml",
        "title_ja": "memoire album & Cher de memoire tour flyer",
        "title_en": "memoire (1994) — album & tour flyer",
        "publication_date": "1994-01",
        "scan": "images/flyers/flyers-1994-01-live-1994.webp",
        "section": "Album & tour",
        "ja": """1st ALBUM memoire 〜メモワール〜 '94.7.24 ON SALE
(限定3,000枚・シリアルNo.入り) Midi:Netteレーベル／全6曲収録／¥2,300(税抜)
Cher de memoire Tour 1994 〜シェール ドゥ メモワール〜
7.30 新宿LOFT 〜CD発売記念GIG〜(ワンマン) … TOUR FINAL 9.23 目黒鹿鳴館
●チケットは、各会場、チケットぴあにて発売中
●ツアー会場にて、マリスミゼルメンバーデザインによるグッズ販売
CD取扱店 全国インディーズ各店""",
        "romaji": """1st ALBUM memoire — '94.7.24 ON SALE (gentei 3,000-mai, serial No. tsuki)
Cher de memoire Tour 1994 — July–Sept nationwide dates; final 9/23 Meguro Rokumeikan
Tickets at venues and Ticket Pia; member-designed goods at tour venues.""",
        "en": """First album memoire — 24 Jul 1994, limited 3,000 copies with serial numbers,
¥2,300 ex tax, 6 tracks on Midi:Nette.
Cher de memoire Tour 1994 with nationwide dates Jul–Sep; final 23 Sep Meguro Rokumeikan.
Tickets via Ticket Pia; member-designed merchandise at venues.""",
    },
    {
        "id": "flyers-1993-08-artistic-expression",
        "article_id": "flyers-1993-08-artistic-expression",
        "issue_file": "1992-1994-live.yaml",
        "title_ja": "芸術表現として音楽を昇華させていきたいんです",
        "title_en": "Artistic expression flyer (magazine clipping)",
        "publication_date": "1993-08",
        "scan": "images/flyers/flyers-1993-08-artistic-expression.webp",
        "section": "Article excerpt",
        "ja": """芸術表現として音楽を昇華させていきたいんです
今、関東の音楽シーンに新しい旋風を巻き起こしているマリス・ミゼル。結成1周年記念ライヴもソールド・アウトの大成功におさめ、現在は関東の若手バンドを集めて、イベント『悲劇の晩餐』を開催し、一緒に関東の音楽シーンを盛り上げていこうとしている。まさに今後、シーンの台風の目となる奴らだ。""",
        "romaji": """Geijutsu hyōgen to shite ongaku o shōka sasete ikitain desu.
Marisu Mizeru ga Kantō no ongaku shīn ni atarashii senpū o makiokoshite iru…
Ichinen kinen raivu mo sōrudo auto; ibento "Higeki no Bansan" o kaisai.""",
        "en": """"We want to elevate music as artistic expression."
Malice Mizer is stirring the Kanto scene; their first-anniversary live sold out.
They are hosting the event "Tragic Supper" with young Kanto bands to energize the scene—
described as the eye of the storm to come.""",
    },
    {
        "id": "flyers-1993-12-upcoming-lives",
        "article_id": "flyers-1993-12-upcoming-lives",
        "issue_file": "1992-1994-live.yaml",
        "title_ja": "Upcoming lives flyer (1993–1994)",
        "title_en": "Upcoming live dates flyer",
        "publication_date": "1993-12",
        "scan": "images/flyers/flyers-1993-12-upcoming-lives.webp",
        "section": "Live schedule",
        "ja": """2/5 下北沢Shelter
2/20 市川CLUBGIO (all night)
3/6 新宿LOFT
3/15 代々木Chocolate City
3/17 横浜MONSTER
3/27 日仏会館
3/29 目黒鹿鳴館
4/6 名古屋DIAMOND HALL
4/11 横浜MONSTER""",
        "romaji": """2/5 Shimokitazawa Shelter
2/20 Ichikawa CLUB GIO (all night)
3/6 Shinjuku LOFT
3/15 Yoyogi Chocolate City
3/17 Yokohama MONSTER
3/27 Nichifutsu Kaikan
3/29 Meguro Rokumeikan
4/6 Nagoya DIAMOND HALL
4/11 Yokohama MONSTER""",
        "en": """Early 1994 live schedule: Shimokitazawa Shelter (2/5), Ichikawa CLUB GIO all-night (2/20),
Shinjuku LOFT (3/6), Yoyogi Chocolate City (3/15), Yokohama MONSTER (3/17, 4/11),
Nichifutsu Kaikan (3/27), Meguro Rokumeikan (3/29), Nagoya DIAMOND HALL (4/6).""",
    },
    # --- 1994 releases ---
    {
        "id": "flyers-1994-07-24-memoire",
        "article_id": "flyers-1994-07-24-memoire",
        "issue_file": "1994-releases.yaml",
        "title_ja": "memoire release flyer",
        "title_en": "memoire — first album release flyer",
        "publication_date": "1994-07-24",
        "scan": "images/flyers/flyers-1994-07-24-memoire.webp",
        "section": "Album & tour",
        "ja": """1st ALBUM 〜メモアール〜 memoire '94.7.24 ON SALE
(限定3,000枚・シリアルNo.入り) Midi:Netteレーベル／全6曲収録／¥2,300(税抜)
Cher de memoire Tour 1994 — nationwide tour Jul–Sep, final 9.23 目黒鹿鳴館
チケット各会場・チケットぴあ。ツアー会場でメンバーデザイングッズ販売。""",
        "romaji": """1st ALBUM memoire '94.7.24 — gentei 3,000-mai, ¥2,300 zeinuki
Cher de memoire Tour 1994 — zenkoku, final Meguro Rokumeikan 9/23""",
        "en": """First album memoire — 24 Jul 1994, 3,000-copy limited press with serial numbers,
¥2,300 ex tax. Cher de memoire Tour 1994 nationwide; final 23 Sep Meguro Rokumeikan.""",
    },
    {
        "id": "flyers-1994-07-24-memoire-ii",
        "article_id": "flyers-1994-07-24-memoire-ii",
        "issue_file": "1994-releases.yaml",
        "title_ja": "memoire release flyer (variant II)",
        "title_en": "memoire — sold-out notice & one-man gigs",
        "publication_date": "1994-07-24",
        "scan": "images/flyers/flyers-1994-07-24-memoire-ii.webp",
        "section": "Release notice",
        "ja": """1st ALBUM memoire 〜メモアール〜 94.7.24 ON SALE
(限定3,000枚・通しNo.入り) Midi:Netteレーベル／全6曲収録／￥2,300(税抜)
●予約のみで完売致しました、ありがとうございます。尚、インディーズCD取扱店に多少の在庫がございますので、お問い合わせください。
〜CD発売記念ワンマンGIG〜『最後の晩餐』〈二部構成〉
7.30◆新宿LOFT／8.10◆大阪難波ロケッツ""",
        "romaji": """memoire sold out by reservation only; some stock at indie CD shops.
CD release commemorative one-man "Saigo no Bansan" (The Last Supper), two-part set:
7/30 Shinjuku LOFT, 8/10 Osaka Namba Rockets.""",
        "en": """memoire sold out on pre-orders; limited stock at indie retailers.
CD-release commemorative one-man gigs "The Last Supper" (two-part):
30 Jul Shinjuku LOFT; 10 Aug Osaka Namba Rockets.""",
    },
    {
        "id": "flyers-1994-12-24-memoire-dx",
        "article_id": "flyers-1994-12-24-memoire-dx",
        "issue_file": "1994-releases.yaml",
        "title_ja": "memoire DX release flyer",
        "title_en": "memoire Deluxe Edition flyer",
        "publication_date": "1994-12-24",
        "scan": "images/flyers/flyers-1994-12-24-memoire-dx.webp",
        "section": "Deluxe release",
        "ja": """記憶と空のワンシーン — 殺したいと思うだろうか？抱きたいと思うだろうか？……
物語の結末は、「memoire」デラックス盤、ヴィジュアル・ストーリーブックレットに記されています。
「memoire」デラックス盤発売！ 94.12.24 ON SALE ——世界同時発売—— ¥3,000(税別)
●豪華BOX入り ●ボーナス・トラック1曲追加 ●ヴィジュアル・ストーリーブックレット付(12ページ)
Cher de memoire II ONEMAN Tour 1994 — final 12/27 目黒鹿鳴館""",
        "romaji": """memoire DX hatsubai 94.12.24 — gōka BOX, bonus track, 12-page visual story booklet ¥3,000 zeibetsu
Cher de memoire II one-man tour — final 12/27 Meguro Rokumeikan""",
        "en": """memoire Deluxe Edition — 24 Dec 1994 worldwide, ¥3,000 ex tax.
Luxury box, one bonus track, 12-page visual story booklet concluding the album's narrative.
Cher de memoire II one-man tour; final 27 Dec Meguro Rokumeikan.""",
    },
    # --- 1995–2001 ---
    {
        "id": "flyers-1995-12-10-uruwashiki-kamen",
        "article_id": "flyers-1995-12-10-uruwashiki-kamen",
        "issue_file": "1995-releases.yaml",
        "title_ja": "麗しき仮面の招待状 release flyer",
        "title_en": "Uruwashiki Kamen no Shōtaijō — first single flyer",
        "publication_date": "1995-12-10",
        "scan": "images/flyers/flyers-1995-12-10-uruwashiki-kamen.webp",
        "section": "Single release",
        "ja": """95.12.10 1st. SINGLE RELEASE
〜麗しき仮面の招待状〜
C/W ▶ APRÈS MIDI 〜あるパリの午後で〜
CDS ▶ M:N-002 ¥1,500(税別)
通販方法 ▶ CD代金¥1,500 + 送料¥300を現金書留にてMidi:Netteまでお送りください。
1/6(Sat.) ON AIR WEST ●チケット代金 ¥3,500 チケットぴあ、会場にて11/5発売""",
        "romaji": """95.12.10 1st single Uruwashiki Kamen no Shōtaijō (Invitation of the Beautiful Mask)
C/W Après Midi ~Aru Pari no Gogo de~ (On a Certain Afternoon in Paris)
M:N-002 ¥1,500 zeibetsu; mail order +¥300 shipping
1/6 ON AIR WEST — tickets ¥3,500 on sale 11/5 via Ticket Pia""",
        "en": """First single release 10 Dec 1995: Uruwashiki Kamen no Shōtaijō
(Invitation of the Beautiful Mask); c/w Après Midi ~On a Certain Afternoon in Paris~.
M:N-002 ¥1,500 ex tax. Mail order available. 6 Jan ON AIR WEST — tickets ¥3,500.""",
    },
    {
        "id": "flyers-1996-06-09-voyage",
        "article_id": "flyers-1996-06-09-voyage",
        "issue_file": "1996-releases.yaml",
        "title_ja": "Voyage release flyer",
        "title_en": "Voyage — full album flyer",
        "publication_date": "1996-06-09",
        "scan": "images/flyers/flyers-1996-06-09-voyage.webp",
        "section": "Album release",
        "ja": """〜永遠の旅を貴方と共に〜
FULL ALBUM [Voyage ヴォヤージュ 〜sans retour〜] 1996.6.9 RELEASE
M:N-003 ¥3500(税別) 【初回限定5000枚】特殊BOX仕様 / VISUAL BOOKLET封入
※ローディー急募!! 詳しくは[Midi:Nette]へ""",
        "romaji": """~Eien no tabi o anata to tomo ni~
Voyage sans retour — 1996.6.9, M:N-003 ¥3500 zeibetsu
Shokai gentei 5000-mai tokushu BOX + visual booklet
Rōdī kyūbo (roadies wanted urgently)""",
        "en": """"An eternal journey together with you" — full album Voyage ~sans retour~,
9 Jun 1996, ¥3,500 ex tax. First-press 5,000 copies in special box with visual booklet.
Roadies urgently wanted — contact Midi:Nette.""",
    },
    {
        "id": "flyers-1996-10-10-ma-cherie",
        "article_id": "flyers-1996-10-10-ma-cherie",
        "issue_file": "1996-releases.yaml",
        "title_ja": "ma chérie single release flyer",
        "title_en": "ma chérie ~Itoshii Kimi e~ — single flyer",
        "publication_date": "1996-10-10",
        "scan": "images/flyers/flyers-1996-10-10-ma-cherie.webp",
        "section": "Single release",
        "ja": """新生マリス ミゼル 1周年 ファンクラブ マ・シェリ発足記念Single CD
写真集付きリリース決定 16ページ/B5変形判
完全限定予約生産 ma chérie 〜愛しい君へ〜 c/w regret
CDS◆M:N-004 ¥2500(税別) 1996.10.10 ON SALE""",
        "romaji": """Shinsei Marisu Mizeru 1-shūnen; fan club ma chérie launch commemorative single
Kanzen gentei yoyaku seisan — ma chérie ~Itoshii kimi e~, c/w regret
M:N-004 ¥2500 zeibetsu, 1996.10.10""",
        "en": """New Malice Mizer 1st anniversary; fan club ma chérie launch commemorative single
with 16-page B5 photo book. Completely limited pre-order production:
ma chérie ~To My Beloved You~, c/w regret — 10 Oct 1996, ¥2,500 ex tax.""",
    },
    {
        "id": "flyers-1997-02-11-gekka",
        "article_id": "flyers-1997-02-11-gekka",
        "issue_file": "1997-releases.yaml",
        "title_ja": "月下の夜想曲 release flyer",
        "title_en": "Gekka no Yasōkyoku — single & merveilles flyer",
        "publication_date": "1997-02-11",
        "scan": "images/flyers/flyers-1997-02-11-gekka.webp",
        "section": "Single & album",
        "ja": """NEW SINGLE 2.11 RELEASE 月下の夜想曲
TBS系TV「王様のブランチ」エンディング・テーマ 初回限定仕様 CODA-1415 ¥1,050(tax in)
Major 1st Album 3.18 Release merveilles (メルヴェイユ) COCA-14866 ¥3,059(tax in) 初回限定仕様
4.1 日本武道館公演決定 2.15 ticket on sale
[CBCラジオ] マリス・ミゼル「真夜中のシルヴプレ」(日) 24:00~24:30""",
        "romaji": """Gekka no Yasōkyoku — 2/11, TBS "Ōsama no Buranchi" ending theme
merveilles major 1st album 3/18; Nippon Budōkan 4/1 decided
Radio: Mayonaka no S'il vous plaît Sundays 24:00""",
        "en": """New single Gekka no Yasōkyoku (Nocturne Under the Moon) — 11 Feb 1997,
TBS "King's Brunch" ending theme. Major debut album merveilles 18 Mar.
Nippon Budokan 1 Apr; tickets 15 Feb. Radio program Mayonaka no S'il vous plaît Sun 24:00.""",
    },
    {
        "id": "flyers-1997-06-30-derniere-vhs",
        "article_id": "flyers-1997-06-30-derniere-vhs",
        "issue_file": "1997-releases.yaml",
        "title_ja": "sans retour Voyage 'derniere' VHS flyer",
        "title_en": "Shibuya Kokaido live video flyer",
        "publication_date": "1997-06-30",
        "scan": "images/flyers/flyers-1997-06-30-derniere-vhs.webp",
        "section": "Live video",
        "ja": """渋谷公会堂 LIVE VIDEO 6.30 RELEASE
カラー / Hi-Fi / 35分 / 特典:NEW POST CARD封入
M:N-005 ¥4,300(税別)
※4月1日におこなわれたインディーズ公演のダイジェスト版""",
        "romaji": """Shibuya Kōkaidō LIVE VIDEO 6.30 RELEASE
Karā / 35-fun / tokuten: NEW POST CARD fūnyū
M:N-005 ¥4,300 zeibetsu — 4/1 indies kōen digest""",
        "en": """Shibuya Public Hall live video — 30 Jun 1997, color, 35 min,
bonus postcard included, M:N-005 ¥4,300 ex tax.
Digest of the 1 Apr 1997 indies performance.""",
    },
    {
        "id": "flyers-1998-04-01-au-revoir",
        "article_id": "flyers-1998-04-01-au-revoir",
        "issue_file": "1998-releases.yaml",
        "title_ja": "au revoir release flyer",
        "title_en": "au revoir — single & Budokan flyer",
        "publication_date": "1998-04-01",
        "scan": "images/flyers/flyers-1998-04-01-au-revoir.webp",
        "section": "Single & tour",
        "ja": """New Single au revoir (オ・ルヴォワール) c/w au revoir ~BOSSA~ CODA-1376 ¥1,050(tax in)
東名阪公演 "Ville de merveilles 透明の螺旋" 即SOLD OUT
1998.4.1 日本武道館公演決定 2.15 ticket on sale
[CBCラジオ] マリス・ミゼル「真夜中のシルヴプレ」(火) 24:00〜24:30""",
        "romaji": """au revoir single now on sale
Tōmeihan kōen "Ville de merveilles Tōmei no Rasen" sold out immediately
Nippon Budōkan 1998.4.1 decided; tickets 2/15""",
        "en": """Single au revoir on sale (CODA-1376 ¥1,050).
Tokyo–Nagoya–Osaka tour "Ville de merveilles: Transparent Spiral" sold out instantly.
Nippon Budokan 1 Apr 1998; tickets from 15 Feb.""",
    },
    {
        "id": "flyers-1998-05-20-illuminati",
        "article_id": "flyers-1998-05-20-illuminati",
        "issue_file": "1998-releases.yaml",
        "title_ja": "ILLUMINATI release flyer",
        "title_en": "ILLUMINATI — single & merveilles tour flyer",
        "publication_date": "1998-05-20",
        "scan": "images/flyers/flyers-1998-05-20-illuminati.webp",
        "section": "Single & tour",
        "ja": """NEW SINGLE 5.20 RELEASE
読売TV・NTV系全国ネット「ダウンタウンDX」エンディング・テーマ ILLUMINATI
初回限定ミラー・ジャケット CODA-1528 ¥1,050(tax in)
MAJOR 1st ALBUM NOW ON SALE merveilles メルヴェイユ COCA-14866 ¥3,059(tax in)
"merveilles" TOUR '98 — 5.29札幌〜6.29愛媛 全国ツアー""",
        "romaji": """ILLUMINATI — 5/20, Yomiuri/NTV "Downtown DX" ending theme, mirror jacket first press
merveilles album on sale; Tour '98 May–Jun nationwide""",
        "en": """ILLUMINATI single — 20 May 1998, ending theme for "Downtown DX,"
first-press mirror jacket. Album merveilles on sale. merveilles Tour '98 May–Jun nationwide.""",
    },
    {
        "id": "flyers-1998-09-30-le-ciel",
        "article_id": "flyers-1998-09-30-le-ciel",
        "issue_file": "1998-releases.yaml",
        "title_ja": "Le ciel release flyer",
        "title_en": "Le ciel ~Kuuhaku no Kanata e~ — single & video flyer",
        "publication_date": "1998-09-30",
        "scan": "images/flyers/flyers-1998-09-30-le-ciel.webp",
        "section": "Single & video",
        "ja": """New Single 9.30 Release Le ciel ル・シエル 〜空白の彼方へ〜 CODA-1617 ¥840(tax in)
初回限定スペシャルワイド・ジャケット
Live Video 10.28 Release merveilles 〜終焉と帰趨〜 l'espace
「Tour '98 merveilles 〜終焉と帰趨〜」のライヴ映像 COVA-6191 ¥5,985(tax in)""",
        "romaji": """Le ciel ~Kūhaku no Kanata e~ — 9/30, shokai gentei wide jacket
merveilles ~Shūen to Kisū~ l'espace live video 10/28 COVA-6191""",
        "en": """Single Le ciel ~To the Other Side of the Void~ — 30 Sep 1998,
first-press special wide jacket. Live video merveilles ~End and Outcome~ l'espace — 28 Oct.""",
    },
    {
        "id": "flyers-1998-10-28-lespace",
        "article_id": "flyers-1998-10-28-lespace",
        "issue_file": "1998-releases.yaml",
        "title_ja": "merveilles l'espace video flyer",
        "title_en": "merveilles l'espace — live video flyer",
        "publication_date": "1998-10-28",
        "scan": "images/flyers/flyers-1998-10-28-lespace.webp",
        "section": "Live video",
        "ja": """merveilles 〜終焉と帰趨〜 l'espace (レスパス)
Live Video 10.28 Release
「Tour '98 merveilles 〜終焉と帰趨〜」のライヴ映像 COVA-6191 ¥5,985(tax in)
初回限定スペシャルクリアケース付
New Single Now On Sale Le ciel 〜空白の彼方へ〜 CODA-1617 ¥840(tax in)""",
        "romaji": """merveilles ~Shūen to Kisū~ l'espace — live video 10/28
Shokai gentei clear case; Le ciel single also on sale""",
        "en": """merveilles ~End and Outcome~ l'espace live video — 28 Oct 1998,
first-press special clear case, COVA-6191 ¥5,985 tax in.
Single Le ciel ~To the Other Side of the Void~ also on sale.""",
    },
    {
        "id": "flyers-1998-11-27-itan-shinmon",
        "article_id": "flyers-1998-11-27-itan-shinmon",
        "issue_file": "1998-releases.yaml",
        "title_ja": "異端審問 book release flyer",
        "title_en": "Itan Shinmon (Heretic Inquisition) — official book preorder flyer",
        "publication_date": "1998-11-27",
        "scan": "images/flyers/flyers-1998-11-27-itan-shinmon.webp",
        "section": "Book preorder",
        "ja": """MALICE初のオフィシャル・インタビュー本! 24時間 MALICE MIZER (仮)
撮影・篠山紀信 著者・MALICE MIZER (構成・金井覚) 98年11月末日発売予定
あなたの知らないMana、Gackt、Yu〜ki、Közi、Kamiがここにいる。
メンバー5人への個別インタビューとメンバー座談会、合計インタビュー時間は24時間。しかも、すべて語りおろし。
特別付録: 篠山紀信が撮り下ろした"ヴィジュアル・ストーリー口絵"、MALICE MIZERオリジナル・タトゥー・シール
A5判／200P (カラー口絵8P) ／ソフトカバー 予価1500円+税 ISBN4-87233-424-8""",
        "romaji": """Marisu hatsu official intabyū-bon — "24-jikan MALICE MIZER" (kari)
Kishin Shinoyama photography; 24 hours of all-new interviews + group talk
Tokubetsu furoku: visual story frontispiece, original tattoo stickers
A5, 200 pages, ¥1,500+tax — released end Nov 1998 (later titled Itan Shinmon)""",
        "en": """Malice Mizer's first official interview book (working title "24 Hours MALICE MIZER"),
photography by Kishin Shinoyama, planned late Nov 1998 (published as Itan Shinmon).
24 hours of brand-new individual and group interviews.
Bonus: Shinoyama visual-story frontispiece and original tattoo stickers.
A5 softcover, 200 pages, ¥1,500+tax.""",
    },
    {
        "id": "flyers-1999-11-03-saikai-single",
        "article_id": "flyers-1999-11-03-saikai-single",
        "issue_file": "1999-releases.yaml",
        "title_ja": "再会の血と薔薇 release flyer",
        "title_en": "Saikai no Chi to Bara — single & LP flyer",
        "publication_date": "1999-11-03",
        "scan": "images/flyers/flyers-1999-11-03-saikai-single.webp",
        "section": "Single & LP",
        "ja": """再会の血と薔薇
Single & Analog 1999.11.3 Double Release
<12cmCD> 特殊BOOK仕様 MMCD-006 ¥1,260(tax in)
<LP> 限定3万枚プレス / 特殊PICTURE仕様 MMAL-007 ¥1,575(tax in)""",
        "romaji": """Saikai no Chi to Bara — CD special book edition + limited 30,000-copy picture LP
Double release 1999.11.3""",
        "en": """Blood and Roses of Reunion (Saikai no Chi to Bara) —
double release 3 Nov 1999: CD special book edition MMCD-006 ¥1,260;
limited 30,000-copy picture LP MMAL-007 ¥1,575.""",
    },
    {
        "id": "flyers-1999-12-21-saikai-de-limage",
        "article_id": "flyers-1999-12-21-saikai-de-limage",
        "issue_file": "1999-releases.yaml",
        "title_ja": "再会の血と薔薇 de l'image flyer",
        "title_en": "Saikai no Chi to Bara ~de l'image~ — video single flyer",
        "publication_date": "1999-12-21",
        "scan": "images/flyers/flyers-1999-12-21-saikai-de-limage.webp",
        "section": "Video single",
        "ja": """VIDEO SINGLE 再会の血と薔薇 ~ de l'image ~ 1999.12.21 RELEASE
全20P豪華ブックレット付 AMV-001 ¥2,100(tax in) 期間限定ハードケース仕様
NEW SINGLE NOW ON SALE 再会の血と薔薇 12cmCD+特製BOOK仕様
発売当初品切れのため…2ndプレスから"ヴィデオ・ル・シェル"を店頭にてお渡し""",
        "romaji": """Video single Saikai no Chi to Bara ~de l'image~ — 20-page booklet, limited hard case
Apology gift "Video Le Ciel" from 2nd CD press after initial sellout""",
        "en": """Video single Blood and Roses of Reunion ~de l'image~ — 21 Dec 1999,
20-page deluxe booklet, limited hard case AMV-001 ¥2,100.
Apology for initial sellout: "Video Le Ciel" given at stores from 2nd CD pressing.""",
    },
    {
        "id": "flyers-2001-04-18-derniere-dvd-front",
        "article_id": "flyers-2001-04-18-derniere-dvd-front",
        "issue_file": "2001-releases.yaml",
        "title_ja": "sans retour Voyage 'derniere' DVD flyer",
        "title_en": "sans retour Voyage derniere — DVD flyer",
        "publication_date": "2001-04-18",
        "scan": "images/flyers/flyers-2001-04-18-derniere-dvd-front.webp",
        "section": "DVD release",
        "ja": """サン ルトゥール ヴォヤージュ "デルニエール" 〜アンコール ユヌ フォワ〜
DVD 2001.4.18 Release
1997年4月1日 渋谷公会堂で行われたライヴのダイジェスト
ボーナスショットとして、メンバーの撮りおろしインタビュー & [N.p.s N.g.s] を収録
MMBV-016 ¥5,000(tax out) 45min""",
        "romaji": """sans retour Voyage "derniere" ~encore une fois~ DVD 2001.4.18
1997/4/1 Shibuya Kōkaidō live digest + new member interviews & N.p.s N.g.s
MMBV-016 ¥5,000 zeinuki 45min""",
        "en": """sans retour Voyage "derniere" ~encore une fois~ DVD — 18 Apr 2001.
Digest of 1 Apr 1997 Shibuya Public Hall live; bonus new member interviews
and N.p.s N.g.s included. MMBV-016 ¥5,000 ex tax, 45 min.""",
    },
    {
        "id": "flyers-2001-05-30-gardenia",
        "article_id": "flyers-2001-05-30-gardenia",
        "issue_file": "2001-releases.yaml",
        "title_ja": "Gardenia release flyer",
        "title_en": "Gardenia — single & video flyer",
        "publication_date": "2001-05-30",
        "scan": "images/flyers/flyers-2001-05-30-gardenia.webp",
        "section": "Single & video",
        "ja": """Klaha 正式加入後、初のシングル第一段 2001.5.30 Release Gardenia ガーデニア
c/w: 崩壊序曲 / Gardenia (Instrumental) / 崩壊序曲 (Instrumental)
初回限定盤 BOX仕様＆ステッカー封入 MMCD-019 ¥1,260(tax in)
VIDEO & DVD同時発売 Gardenia ~de l'image~ MMVC-020 / MMBV-021 ¥1,575(tax in)""",
        "romaji": """First single after Klaha's official joining — Gardenia 2001.5.30
c/w Hōkai Jokyoku (Collapse Overture); shokai gentei BOX + sticker
Simultaneous video & DVD release Gardenia ~de l'image~""",
        "en": """First single after Klaha joined: Gardenia — 30 May 2001.
c/w Collapse Overture (Hōkai Jokyoku) and instrumentals.
First-press box with sticker MMCD-019 ¥1,260.
Simultaneous VHS/DVD Gardenia ~de l'image~.""",
    },
    {
        "id": "flyers-2001-10-30-bara-no-konrei",
        "article_id": "flyers-2001-10-30-bara-no-konrei",
        "issue_file": "2001-releases.yaml",
        "title_ja": "薔薇の婚礼 CD/DVD flyer",
        "title_en": "Bara no Konrei (Wedding of the Rose) — film tie-in flyer",
        "publication_date": "2001-10-30",
        "scan": "images/flyers/flyers-2001-10-30-bara-no-konrei.webp",
        "section": "Film & CD/DVD set",
        "ja": """急遽 発売決定 2001.10.30 Release
11月甘美にロードショー MALICE MIZER初主演映画「薔薇の婚礼」メインテーマ
「真夜中に交わした約束」〜薔薇の婚礼〜 CD & DVDセット MMCD-025 ¥2,835(tax in)
収録楽曲: CD 4曲 / DVD 1曲（PV特別編集・映画未公開映像含む）
公開記念写真集第1弾「薔薇の輪舞」10/15発売 ¥3,675(税込)
全国シネ・リーブル系で順次公開（池袋・梅田・神戸・博多駅ほか）""",
        "romaji": """Kyūkyo hatsubai — Bara no Konrei film roadshow Nov 2001
CD&DVD set "Mayonaka ni Kawashita Yakusoku ~Bara no Konrei~"
Commemorative photo book "Bara no Rinbu" (Rondo of the Rose) ¥3,675
Cine Libre theaters nationwide""",
        "en": """Urgent release 30 Oct 2001 — Malice Mizer's first starring film Wedding of the Rose
roadshow from November. CD & DVD set Promise Exchanged at Midnight ~Wedding of the Rose~
MMCD-025 ¥2,835; 4 CD tracks + special-edit PV DVD with unreleased film footage.
Commemorative photo book Rondo of the Rose (15 Oct, ¥3,675). Cine Libre nationwide.""",
    },
    {
        "id": "flyers-2001-11-30-garnet",
        "article_id": "flyers-2001-11-30-garnet",
        "issue_file": "2001-releases.yaml",
        "title_ja": "Garnet release flyer",
        "title_en": "Garnet ~Kindan no Sono e~ — single flyer",
        "publication_date": "2001-11-30",
        "scan": "images/flyers/flyers-2001-11-30-garnet.webp",
        "section": "Single",
        "ja": """Garnet 〜禁断の園へ〜 2001.11.30 ON SALE
I. Garnet 〜禁断の園へ〜
II. 幻想楽園
III. Garnet 〜禁断の園へ〜 (Instrumental)
IV. 幻想楽園 (Instrumental)""",
        "romaji": """Garnet ~Kindan no Sono e~ (To the Forbidden Garden) — 2001.11.30
Track II: Gensō Rakuen (Fantasy Paradise)""",
        "en": """Garnet ~To the Forbidden Garden~ — on sale 30 Nov 2001.
Tracks: Garnet ~To the Forbidden Garden~; Fantasy Paradise (Gensō Rakuen); instrumentals.""",
    },
]


def render_flyer_yaml(entry: dict) -> str:
    doc = {
        "id": entry["id"],
        "article_id": entry["article_id"],
        "publication": "flyers",
        "issue_number": None,
        "publication_date": entry["publication_date"],
        "pages": 1,
        "title_ja": entry["title_ja"],
        "title_en": entry["title_en"],
        "scan_paths": [entry["scan"]],
        "translator": "mizermaxxer",
        "translation_date": "2026-07-06",
        "review_status": "needs_review",
        "license_notes": LICENSE,
        "pages_content": [
            {
                "page": 1,
                "section": entry["section"],
                "ja": textwrap.dedent(entry["ja"]).strip(),
                "romaji": textwrap.dedent(entry["romaji"]).strip(),
                "en": textwrap.dedent(entry["en"]).strip(),
            }
        ],
    }
    # Use custom key pages_content then rename to pages in output
    lines = [
        f"id: {doc['id']}",
        f"article_id: {doc['article_id']}",
        f"publication: {doc['publication']}",
        "issue_number: null",
        f"publication_date: {doc['publication_date']}",
        "pages: 1",
        f"title_ja: {doc['title_ja']}",
        f"title_en: {doc['title_en']}",
        "scan_paths:",
        f"  - {doc['scan_paths'][0]}",
        "translator: mizermaxxer",
        "translation_date: 2026-07-06",
        "review_status: needs_review",
        "license_notes: >",
        f"  {LICENSE}",
        "",
        "pages:",
    ]
    for page in doc["pages_content"]:
        lines.append(f"  - page: {page['page']}")
        lines.append(f"    section: {page['section']}")
        for field in ("ja", "romaji", "en"):
            lines.append(f"    {field}: >")
            for line in page[field].splitlines():
                lines.append(f"      {line}")
    return "\n".join(lines) + "\n"


def link_issue_yaml(entry: dict) -> None:
    path = ISSUES_DIR / entry["issue_file"]
    text = path.read_text(encoding="utf-8")
    article_id = entry["article_id"]
    translation_url = f"data/translations/{entry['id']}.yaml"

    marker = f"- id: {article_id}\n"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"Article {article_id} not found in {path.name}")

    next_article = text.find("\n- id:", start + len(marker))
    block_end = next_article if next_article >= 0 else len(text)
    block = text[start:block_end]

    if "translation:\n" in block:
        block = re.sub(
            r"  translation:\n    available: (?:true|false)\n    url: [^\n]*",
            f"  translation:\n    available: true\n    url: {translation_url}",
            block,
            count=1,
        )
    else:
        raise ValueError(f"No translation block for {article_id}")

    text = text[:start] + block + text[block_end:]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
    for entry in FLYERS:
        out = TRANSLATIONS_DIR / f"{entry['id']}.yaml"
        out.write_text(render_flyer_yaml(entry), encoding="utf-8")
        link_issue_yaml(entry)
        print(f"Wrote {out.name} and linked {entry['article_id']}")


if __name__ == "__main__":
    main()
