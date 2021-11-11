from gensim.test.utils import datapath, get_tmpfile
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models.word2vec import Word2Vec

model = KeyedVectors.load_word2vec_format("E:/大三上/自动化测试/工具复现/model/GloVe/glove_w2v.6B.50d.txt")


def train_glove_model():
    # 输入文件
    glove_file = datapath('E:/大三上/自动化测试/工具复现/model/GloVe/glove.6B.50d.txt')
    # 输出文件
    tmp_file = get_tmpfile("E:/大三上/自动化测试/工具复现/model/GloVe/glove_w2v.6B.50d.txt")
    # 开始转换
    glove2word2vec(glove_file, tmp_file)
    # 加载转化后的文件
    model = KeyedVectors.load_word2vec_format(tmp_file)


def glove_model():
    return model


if __name__ == "__main__":
    print(model.most_similar("dog"))
