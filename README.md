# 仙台高齢化地域の可視化

## Usage

### Visualize Sendai ageing heat map

1. Open `index.html` with the browser

- Screenshot:
- ![Heatmap Screenshot](./img/ageing_heatmap_screenshot.jpg)


### Generate the files

1. Download original files from the internet. Specify their file paths in `constants.py`
1. Install Python3 and `pipenv`
1. `pipenv shell`
1. `pipenv install` from `Pipfile`
1. `mkdir csv`
1. `python3 age_structure.py`: Generates `csv/ages.csv`
1. `python3 position.py`: Generates `csv/ages_positions.csv`

### Visualize Sendai towns with Matplotlib viwer

1. `python3 town_shape.py`

- 形状頂点データを元にすべての町を描画した結果は以下の通り（色分けは境界を明示する以外の意味はありません）
- ![Sendai Town Shapes](./img/sendai_towns.png)

## Purpose

- 仙台の高齢化地域を可視化する（単なる興味）
- Python や JavaScript での可視化ツール使用に慣れる

## 使用したライブラリ

- `Pandas`
- `Numpy`
- `Matplotlib`
- `xlrd`: Excel ファイルの読み込み
- `myshp`: Shapefile の読み込み
- `Leaflet.js`: 地図へのプロット処理

## Files

- `index.html`と `vis-map.js`
  - OpenStreetMap への高齢化情報のプロット
  - `vis-map.js`内部で以下の Python での統計処理結果を使っている
- `age_structure.py`
  - 仙台市の年齢別町名別人口データのエクセルファイルを処理して、CSV に出力する
  - 元データのエクセルファイルは区と性別ごとに複数シートにわかれしてまっているので集約する
  - 「大字」と「小字」でダブルカウントされている行があるため、大字に集約する：
  - 例：「種次字中屋敷」「種次字番古」「種次字南番古」「種次（大字計）」という行が連続している場合には「種次」という大字名を記憶し、それを手がかりにして「種次字」で始まる地名の行を削除する
  - 列の見出しが日本語表記のままではデータ処理で扱いにくいので、英語に変換
- `position.py`
  - 仙台市の町ごとの GPS 座標データのエクセルファイルを処理し、上記の年齢データと合算して CSV に出力する
  - `age_structure.py`の出力結果をデータフレーム A として取り込む
  - データフレーム A から人口三区分（年少人口、生産年齢人口、老年人口）毎の人数・人口比を集計し、また高齢化率、従属人口比率、老年化指数、男女比も算出する
  - 別ファイルから各町丁大字の代表点の GPS 座標を取得し、データフレーム B とする
  - 年齢構成ファイルでは「４丁目」の書式のところが、このファイルでは漢数字の「四丁目」になってしまっているので統一する
  - データフレーム A とデータフレーム B を、町名と区名をキーにして JOIN する（町名だけだと失敗する。例えば青葉区と太白区両方に「茂庭」という地名があるため）
- `town_shapes.py`
  - 仙台の全ての町の形状を可視化する
  - 仙台市の町ごとの形状データを処理し、町別年齢構成データと合わせて可視化...したかったのだが、この形状データと他の年齢構成データの地域区分の方法に齟齬があるため、その用途には使えなかった
  - Shapefileは、仙台の全ての町の形の頂点情報を持っているが、このままだと扱いにくいのでPandasのDataframeに変換し、あとは頂点を描画していくだけ。
- `constants.py`
  - 複数の Python モジュールで共用するデータ
- `csv/`
  - Pythonで出力される CSV ファイルの置き場（`.gitignore`済）
- `raw/`
  - ダウンロードしてきた CSV ファイルの置き場
  - データサイズが大きいため元ファイルは`.gitignore` している

## 考察

- 高齢化率が低いのは、交通結節点と新興住宅地が多い。
  - 泉中央
  - 紫山
  - あすと長町
  - 富沢
  - 愛子盆地：　錦が丘は年少人口が４０％程度で仙台で一番こどもが多い。
  - 荒井
  - 仙台駅周辺
  - 新田
  - 将監殿
- 高齢化率が高いのは昭和 30 年代・40 年代から開発が進んだ住宅地と、僻地が多い。
  - 加茂
  - 長命ケ丘
  - 高森
  - 松陵
  - 鶴ケ谷
  - 八木山西部
  - 茂庭台
  - 袋原
  - 沿岸部
  - 山岳地帯
- 特殊な傾向が見られる地域もあるようだ。
  - 霞目と苦竹：　自衛隊駐屯地の所在地。大半が自衛隊員であるため。男女比も男性がかなり多い。
  - 古城二丁目：　仙台刑務所の所在地。男子刑務所であるため男女比も男性がかなり多い。
  - 三神峯：　大学職員宿舎しかないため、高齢化率が高い。
  - 川内亀岡町・川内元支倉：　国家公務員宿舎の所在地。国家公務員は男性が多いため、男女比も男が多く高齢化率も低い。
  - 大沢三丁目：　老人ホーム以外の住居がないためか、高齢化率が驚異の 98％。
- 町ごとに人口がまったく違うのでそこまで意味がない数字だが、一応以下のような分類ができる。（なお、仙台市の高齢化率は23.7％）
  | 地域種別 | 老年人口比率 | 町の数 |
  | :------------: | :---------------: | ------: |
  | 非高齢化地域 | 7%未満 | 37 |
  | 高齢化地域 | 7%以上 14%未満 | 91 |
  | 高齢地域 | 14%以上 21%未満 | 214 |
  | 超高齢地域 | 21%以上 | 607 |
  | 合計 | - | 949 |
- 人数が少なすぎて高齢化率の計算が統計的に意味のない地域もある。どの統計検定で除外できる？

## Reference

- 仙台市の町別の年齢別人口データ（令和２年４月１日）
  - 町名別年齢（各歳）別住民基本台帳人口　http://www.city.sendai.jp/chosatoke/shise/toke/jinko/chomebetsu.html
  - 元データの宮城野区の地名「二（大字計）」は「二木（大字計）」の間違いだったので、該当する箇所を手動で置換した
- 宮城県各市町村の町の代表点の GPS 座標情報（平成 30 年分）
  - 位置参照情報ダウンロードサービス： http://nlftp.mlit.go.jp/cgi-bin/isj/dls/_choose_method.cgi
- 町別の形状データ
  - 独立行政法人統計センター　地図で見る統計(統計 GIS)　https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2015&serveyId=A002005212015
- 地図データ：
  - OpenStreetMap：　https://www.openstreetmap.org/
  - `matplotlib` + `basemap`：　出力結果が見にくのでボツ
  - `matplotlib` + `pyshp`：　国交省の Shapefile における地域区分の単位が人口データの区分単位とズレているためボツ
  - Google Map：　 OpenStreetMap と同じことができるが、ライセンス的に面倒なのでボツ
