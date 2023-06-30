import os

import faiss
import numpy as np
import openai
from dotenv import load_dotenv
from openai import Embedding
from openai.embeddings_utils import get_embedding

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

class Test:
    def __init__(self):
        self.target_texts = [
            "今日は雨森雅司に賽振られたねえ",
            "小泉今日子は雨後の筍喰えるかな",
            "マンゴー食べれてよかったねえ",
            "良い天気だね～～",
            "キウイはビタミンCが豊富だね",
            "カナダは北米に位置しているよ",
            "アイスランドは温泉が有名だね",
            "サッカーは楽しいスポーツだ",
            "日本は四季がはっきりしているね",
            "バナナは栄養価が高いよ",
            "オーストラリアはコアラがいるよ",
            "バスケットボールは高身長が有利だ",
            "インドはカレーがおいしいね",
            "フランスはワインが有名だよ",
            "ブラジルはサンバの国だね",
            "夏は海水浴が楽しいね",
            "ブルーベリーは目にいいよ",
            "エジプトはピラミッドがあるよ",
            "冬はスキーが楽しいね",
            "パリは芸術の盛んだった都市だよ",
            "春は桜がきれいだね",
            "中国は人口が多い国だよ",
            "フィジーはビーチが素晴らしいね",
            "イタリアはピザが有名だよ",
            "オレンジは甘酸っぱいね",
            "アフリカはサバンナが広がっているよ",
            "夏はバーベキューが楽しいね",
            "アイルランドはビールがおいしいよ",
            "ドイツはビールが有名だね",
            "秋は紅葉がきれいだよ",
            "ロンドンは雨が多いね",
            "日本は寿司が有名だよ",
            "春は新しい出会いがあるね",
            "ブドウはワインの原料だよ",
            "スペインは闘牛が有名だね",
            "冬は雪だるま作りが楽しいよ",
            "トマトは野菜の一種だよ",
            "ハワイはサーフィンが楽しいね",
            "ロシアは広大な国土を持っているよ",
            "森林浴は心地よいね",
            "デンマークは自転車が多いよ",
            "カボチャはハロウィンの象徴だね",
            "ベネズエラは美しいビーチがあるよ",
            "冬は雪合戦が楽しいね",
            "スイスはチーズが美味しいよ",
            "メキシコはタコスが有名だね",
            "南アフリカはサファリが人気だよ",
            "バドミントンは速いラリーがあるね",
            "ポーランドは美しい城があるよ",
            "ソウルはショッピングが楽しいね",
            "ペットは癒しをくれるよ",
            "スウェーデンはIKEAの本国だね",
            "プールは夏に涼しいね",
            "ジャガイモは料理の基本だよ",
            "オランダはチューリップが有名だね",
            "ベルギーはワッフルが美味しいよ",
            "釣りは静かな趣味だね",
            "マラソンは耐久力が試されるよ",
            "シンガポールは夜景がきれいだね",
            "アボカドは健康に良いよ",
            "ノルウェーはフィヨルドが有名だね",
            "チェスは頭の体操だよ",
            "イスラエルは歴史が深いね",
            "スペインはフラメンコが魅力的だよ",
            "ヨガはリラックスに良いね",
            "アメリカはバーガーが人気だよ",
            "イタリアはジェラートが美味しいね",
            "バレエは優雅なダンスだよ",
            "サッカーは国際的なスポーツだね",
            "ドバイは超高層ビルが立つよ",
            "カプサイシンは辛さの元だよ",
            "ニュージーランドは羊が多いね",
            "オリーブオイルは料理に欠かせないよ",
            "オーストラリアはコアラがいるよ",
            "バスケットは高速なゲームだね",
            "エクアドルは赤道が通るよ"] * 3

        response = Embedding.create(input=self.target_texts,
                                    model="text-embedding-ada-002")
        # 色んなプロパティを含んでいるresponseの中から、ベクトル表現のみを取り出したリストを作る
        self.embedding = [record["embedding"] for record in response["data"]]
        self.embedding_array = np.array(self.embedding).astype("float32")


    def init_voronoi_indexer(self):
        """
        クラスタリングによってデータ空間をボロノイ領域に分割することにより
        高速な近傍探索を可能にするためのindexerを初期化するメソッド
        ボロノイ領域の紹介はこちら --> https://ja.wikipedia.org/?curid=91418
        このアルゴリズムでは質問クエリに対して、その周辺領域のみで探索できるので
        総当たりせずに済むので探索にかかる時間を大幅に短縮できる
        """

        # 30ページを超える分量の多いPDFファイルに適用
        n_pages = len(self.embedding_array)
        if n_pages > 30:
            # ボロノイ領域の数
            # クラスタリング空間を定義する量子化器（Quantizer）つくる（L2ノルム）
            self.quantizer = faiss.IndexFlatL2(1536)
            # 下記引数の1536はembeddingの次元数、20はボロノイ領域の数（ボロノイの数は増やすと精度上がって処理時間増えるトレードオフ）
            # embeddingの次元数は`text-embedding-ada-002`以外を使う場合には変更が必要。BERT-baseなら768次元など。
            self.indexer = faiss.IndexIVFFlat(self.quantizer, 1536, 5)
            # ベクトルデータベースからボロノイ領域を生成
            self.indexer.train(self.embedding_array)
            # ボロノイ領域にデータを追加
            self.indexer.add(self.embedding_array)
        else:
            # 分量の少ないテキストデータに対しては総当たり探索でも問題ないので
            # 単体のL2ノルムアルゴリズムを使う。
            self.indexer = faiss.IndexFlatL2(1536)
            # データを追加
            self.indexer.add(self.embedding_array)

    def voronoi_diagram_search(self, query_embedding):
        """
        ボロノイ領域による近傍探索を実行するメソッド

        Args:
            query_embedding (np.ndarray): 質問クエリをembeddingしたやつ

        Returns:
            top_n_pages (pandas.DataFrame): 上位n件のテキスト情報を格納したデータフレーム
        """
        # 近傍探索の実行。
        query_embedding = np.array([query_embedding]).astype("float32")
        _, idx = self.indexer.search(query_embedding, 3)
        return self.target_texts[idx[0][0]]

    def answer_about_pdf(self, query):
        # query文字列とそのembedding
        query_embedding = get_embedding(query, engine="text-embedding-ada-002")

        # ボロノイ探索を実行。上位3件のテキストを取得
        self.init_voronoi_indexer()
        result = self.voronoi_diagram_search(query_embedding)
        return result


if __name__ == "__main__":
    query = "今日は雨振らんくてよかったねえ"
    test = Test()
    result = test.answer_about_pdf(query)
    print(result)