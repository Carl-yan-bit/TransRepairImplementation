import spacy
import numpy as np
from collections import defaultdict
from nltk import FreqDist
from nltk.corpus import brown

GLOVE_LOCATION = "./"
SIM_DICT_FILE = "similarity_dict.txt"


def valid_eng_words(num):
    """
    符合的英文单词词库
    :param num: 单词数量
    :return:
    """
    frequency_list = FreqDist(i.lower() for i in brown.words())
    list = frequency_list.most_common()[:num]
    valid_words = []
    for w in list:
        valid_words.append(w[0])
    return valid_words


def load_glove():  # 加载glove
    glove_dict = {}
    with open(GLOVE_LOCATION + "glove.6B.50d.txt", 'r', encoding='mac_roman') as f:
        for line in f:
            try:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], "float32")
                glove_dict[word] = vector
            except:
                continue
    return glove_dict


def load_spacy():  # 加载spacy
    spacy_dict = spacy.load('en_core_web_md')
    return spacy_dict


def similarity(vec1, vec2):  # 计算向量余弦相似度
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def to_line(k, v):
    return "%s %s" % (k, ' '.join(map(str, v)))


def create_dictionary(threshold):
    """
    构建上下文相似语料库
    :param threshold: 相似阈值
    :return:
    """
    glove_dict = load_glove()
    spacy_dict = load_spacy()
    print("模型加载完毕")
    similarity_dict = defaultdict(list)  # 上下文相似语料库
    glove_filter_word = []
    valid_words = valid_eng_words(5000)

    # 过滤
    n = 0
    for word in sorted(glove_dict.keys()):
        n = n + 1
        print(n)
        if word not in valid_words or not spacy_dict.vocab.has_vector(word):
            glove_filter_word.append(word)
            continue
        # 过滤掉名词和形容词、数字以外的
        tokens = spacy_dict(word)
        pos = tokens[0].pos
        # 92名词 84形容词 93数字
        if pos not in [92, 84]:
            glove_filter_word.append(word)

    print("过滤glove_dict中单词数：", len(glove_filter_word))
    for word in glove_filter_word:
        del glove_dict[word]

    n = 0
    length = len(glove_dict)
    print("glove_dict剩余单词数：", length)
    length = length * length
    for word in sorted(glove_dict.keys()):
        for other_word in sorted(glove_dict.keys()):
            n = n + 1
            print(other_word, " ", n, " ", format(n/length, ".3f"))
            if other_word <= word:
                continue
            similarity_glove = similarity(glove_dict[word], glove_dict[other_word])
            similarity_spacy = similarity(spacy_dict(word).vector, spacy_dict(other_word).vector)
            if similarity_glove > threshold and similarity_spacy > threshold:
                similarity_dict[word].append(other_word)
                similarity_dict[other_word].append(word)

    with open(SIM_DICT_FILE, 'w') as f:  # 写入similarity_dict.txt
        print("similarity_dict")
        print(len(similarity_dict))
        for key, values in similarity_dict.items():
            current_line = to_line(key, values)
            print(current_line)
            f.write(current_line + '\n')
    return 0


def test():  # 测试glove, spacy
    glove_dict = load_glove()
    spacy_dict = load_spacy()
    print("finish loading")
    print(len(spacy_dict.vocab))
    while True:
        w1 = input("w1: ")
        w2 = input("w2: ")
        if w1 not in glove_dict:
            print(w1, "not int glove")
            continue
        if w2 not in glove_dict:
            print(w2, "not in glove")
            continue
        if not spacy_dict.vocab.has_vector(w1):
            print(w1, "not in spacy")
            continue
        if not spacy_dict.vocab.has_vector(w2):
            print(w2, "not in spacy")
            continue
        sim_glove = similarity(glove_dict[w1], glove_dict[w2])
        sim_spacy = similarity(spacy_dict(w1).vector, spacy_dict(w2).vector)

        print("glove_similarity: ", sim_glove)
        print("spacy_similarity: ", sim_spacy)


if __name__ == "__main__":
    create_dictionary(0.7)
