# 仙台高齢化地域の可視化

## Usage

### Generate the files

1. Download original files from the internet. Specify their file paths in `constants.py`
1. Install Python3 and `pipenv`
1. `pipenv shell`
1. `pipenv install` at the directory of `Pipfile`
1. `python3 age_structure.py`: Generates `csv/ages.csv`
1. `python3 position.py`: Generates `csv/ages_positions.csv`
1. `python3 plot_on_map.py`

### Visualize Sendai towns with Matplotlib viwer

1. `python3 town_shapes.py`

## Purpose

- 仙台の高齢化地域を可視化してみたい
- Python や JavaScript での可視化ツール使用に慣れたい

## Files

- `age_structure.py`
  - 仙台市の年齢別町名別人口データのエクセルファイルを処理して、CSV に出力する
- `position.py`
  - 仙台市の町ごとの GPS 座標データのエクセルファイルを処理し、上記の年齢データと合算して CSV に出力する
- `town_shapes.py`
  - 仙台の全ての町の形状を以下のように可視化する
  - 仙台市の町ごとの形状データを処理し、町別年齢構成データと合わせて可視化...したかったのだが、この形状データと他の年齢構成データの地域区分の方法に齟齬があるため、その用途には使えなかった
- ![Sendai Town Shapes](./img/sendai_towns.png)
- `constants.py`
  - 複数の Python モジュールで共用するデータ
- `csv/`
  - 出力された CSV ファイルの置き場
- `raw/`
  - ダウンロードしてきた CSV ファイルの置き場
  - データサイズが大きいため元ファイルは`.gitignore` している

## To-do List

- Append population density field to age structure df
- Plot with D3.js & Vue.js
- Write unit test
- Compare the performance of list flatter functions

## Reference

- 仙台市の町別の年齢別人口データ（令和２年４月１日）
  - 町名別年齢（各歳）別住民基本台帳人口　http://www.city.sendai.jp/chosatoke/shise/toke/jinko/chomebetsu.html
  - 元データの宮城野区の地名「二（大字計）」は「二木（大字計）」の間違いだったので、該当する箇所を手動で置換した
- 宮城県各市町村の町の代表点の GPS 座標情報（平成 30 年分）
  - 位置参照情報ダウンロードサービス： http://nlftp.mlit.go.jp/cgi-bin/isj/dls/_choose_method.cgi
- 町別の形状データ
  - 独立行政法人統計センター　地図で見る統計(統計 GIS)　https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2015&serveyId=A002005212015
- 町名の読みがなデータ
  - 住所.jp http://jusyo.jp/csv/new.php
- 地図データ：以下のうちのどれかを使う予定
  - `matplotlib` + `basemap`
  - `pyshp`と国が提供している各町の shape file
  - Google Map
  - OpenStreetMap：　https://www.openstreetmap.org/search?query=%E4%BB%99%E5%8F%B0%E5%B8%82#map=11/38.2530/140.8646
