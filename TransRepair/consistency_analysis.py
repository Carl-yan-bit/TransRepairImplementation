import difflib
import jieba
import numpy as np
import logging

jieba.setLogLevel(logging.INFO)


def getLevenshtein(sentence1, sentence2):
    size_x = len(sentence1) + 1
    size_y = len(sentence2) + 1
    matrix = np.zeros((size_x, size_y))
    for x in range(size_x):
        matrix[x, 0] = x
    for y in range(size_y):
        matrix[0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if sentence1[x - 1] == sentence2[y - 1]:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1
                )
            else:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1] + 1,
                    matrix[x, y - 1] + 1
                )
    return matrix[size_x - 1, size_y - 1]


def normalizedED(sentence1, sentence2):
    dist = getLevenshtein(sentence1, sentence2)
    normalized_dist = 1 - (dist / max(len(sentence1), len(sentence2)))
    return normalized_dist


def computeSimilarity(sentence1, sentence2):
    return normalizedED(sentence1, sentence2)


def wdiff_and_cut(sentence1, sentence2):
    """
    比较中文翻译结果，返回比较不同处后的切片子句集
    :return:
    """
    cut1 = list(jieba.cut(sentence1))
    cut2 = list(jieba.cut(sentence2))
    sub_sentences1 = []  # 去除切片后的子句集
    sub_sentences2 = []
    diff = list(difflib.Differ().compare(cut1, cut2))
    num_diff1 = 0
    num_diff2 = 0
    for d in diff:
        if d[0] == '-':
            num_diff1 = num_diff1 + 1
        if d[0] == '+':
            num_diff2 = num_diff2 + 1
    # 一次去除一个切片
    for i in range(1, num_diff1 + 1):
        count = 0
        sub_sentence1 = ""
        for d in diff:
            if d[0] == '-':
                count = count + 1
                if count == i:
                    continue

            if d[0] != '+':
                if d[0] == '-':
                    sub_sentence1 += d[2:].strip()
                else:
                    sub_sentence1 += d.strip()
        sub_sentences1.append(sub_sentence1)

    for i in range(1, num_diff2 + 1):
        count = 0
        sub_sentence2 = ""
        for d in diff:
            if d[0] == '+':
                count = count + 1
                if count == i:
                    continue
            if d[0] != '-':
                if d[0] == '+':
                    sub_sentence2 += d[2:].strip()
                else:
                    sub_sentence2 += d.strip()
        sub_sentences2.append(sub_sentence2)
    return sub_sentences1, sub_sentences2


def consistency_score(sentence1, sentence2):
    """
    一致性分数
    :param sentence1:语句一 (中文)
    :param sentence2: 语句二(中文)
    :return: 一致性分数
    """
    score = computeSimilarity(sentence1, sentence2)
    sub_sentences1, sub_sentences2 = wdiff_and_cut(sentence1, sentence2)
    for sub_sentence1 in sub_sentences1:
        for sub_sentence2 in sub_sentences2:
            t = computeSimilarity(sentence1, sentence2)
            if t > score:
                score = t

    return score


if __name__ == "__main__":
    print("test")
