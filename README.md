# yukkuri-reimu-marisa-videos

霊夢と魔理沙（[たぬき式ゆっくり](https://tanukiyukkuri.github.io/tanukitachie)の立ち絵）が掛け合いで解説する「ゆっくり解説風」の動画（MP4）を、Claude に作ってもらうための [Agent Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) です。

「〇〇でゆっくり解説動画を作って」と頼むだけで、Claude が次のところまで進めます。

- テーマの調査（Web検索で事実と出典を集める）
- 構成と台本づくり（台本は動画にする前に確認できる）
- 立ち絵の組み立て（表情5種、口パク、まばたき）
- 音声合成（Open JTalk）、字幕、解説パネル、図
- MP4・字幕（SRT）・サムネイル（1280×720）・YouTube 概要欄の書き出し

> [!NOTE]
> 本スキルは非公式のファンメイドです。東方Project・上海アリス幻樂団、たぬき式ゆっくりの配布元とは関係ありません。

## 必要なもの

- コードを実行できる Claude（claude.ai のコード実行・ファイル作成を有効にした状態、または Claude Code）
- 動画を作る環境に Python 3、ffmpeg、日本語フォント（Noto Sans CJK JP）
- Python パッケージ：Pillow、numpy、pyopenjtalk（足りなければ Claude が入れます）

## インストール

### claude.ai

1. [Releases](../../releases) から `yukkuri-reimu-marisa-videos.zip` をダウンロードします。
   - 緑の「Code」ボタンの「Download ZIP」は、フォルダ名が `…-main` になるためアップロードできません。
2. claude.ai で **Customize → Skills** を開き、「+」→「Create skill」→「Upload a skill」から ZIP をアップロードします。

### Claude Code

スキルのフォルダに clone します（このリポジトリの URL は「Code」ボタンからコピーできます）。

```bash
git clone <このリポジトリのURL> ~/.claude/skills/yukkuri-reimu-marisa-videos
```

## 使い方

Claude にこう頼みます。

- 「ブラックホールでゆっくり解説動画を作って」
- 「霊夢と魔理沙で、円安のしくみを3分で解説して」
- 「〇〇を解説する動画を一気に作って」（台本の確認を省略）

指定がなければ、長さは約3分、台本ができた時点で一度確認を求めます。

## フォルダ構成

```
SKILL.md                 Claude が読む手順書
scripts/
  build_sprites.py       立ち絵パーツを重ねて、表情ごとの立ち絵を作る
  chars.py               立ち絵の読み込み（素材がないとき用のオリジナルキャラも描ける）
  render.py              音声・字幕・画面を作り、MP4 とサムネイルを書き出す
assets/tanuki-yukkuri/   たぬき式ゆっくり素材（必要なパーツのみ）と配布元の README・TERMS
```

## ライセンスと素材について

| 対象 | 条件 |
|---|---|
| `SKILL.md`、`scripts/`、この README | [MIT License](LICENSE) |
| `assets/tanuki-yukkuri/` の立ち絵 PNG | たぬき式ゆっくりの規約（同梱の `tanuki-yukkuri_TERMS.txt`）に従います。MIT License の対象外です。 |
| 霊夢・魔理沙（キャラクター） | [東方Projectの二次創作ガイドライン](https://touhou-project.news/guideline/)に従います。 |

- 立ち絵素材は、たぬき式ゆっくり（制作：たぬき、イラスト：lilMonster 様）のうち、このスキルで使うパーツだけをファイル名を英字に変えて同梱しています。**素材そのものは公式サイトからの入手をおすすめします**：https://tanukiyukkuri.github.io/tanukitachie
- 新しい版の素材 ZIP を Claude に添付すれば、そちらを使って立ち絵を作ります。
- 素材についての問い合わせを、たぬき式ゆっくりの制作者・関係者にしないでください（配布元の規約で個別対応しないと定められています）。
- 音声は [Open JTalk](https://open-jtalk.sourceforge.net/) と HTS Voice "Mei"（© Nagoya Institute of Technology、CC BY 3.0）で合成します。音声モデルはこのリポジトリには含まれず、pyopenjtalk が取得します。

### 作った動画を公開するときは

スキルが概要欄用の文（`description.txt`）にまとめて出力しますが、次を入れてください。

- 東方Projectの二次創作であり、公式コンテンツではないこと
- クレジット：音声合成 Open JTalk ／ 音声モデル HTS Voice "Mei"（© Nagoya Institute of Technology, CC BY 3.0）／ 立ち絵 たぬき式ゆっくり: https://tanukiyukkuri.github.io/tanukitachie ／ 原作 東方Project（上海アリス幻樂団）
