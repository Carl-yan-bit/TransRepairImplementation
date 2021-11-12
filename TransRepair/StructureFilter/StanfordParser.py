from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP(r'E:\NLP\StanfordParser\stanford-corenlp-latest\stanford-corenlp-4.3.1')


def stanfordParser(s):
    # print('Tokenize:', nlp.word_tokenize(sentence))
    # print('Part of Speech:', nlp.pos_tag(s))
    # print('Named Entities:', nlp.ner(sentence))
    # print('Constituency Parsing:', nlp.parse(s))  # 语法树
    # print('Dependency Parsing:', nlp.dependency_parse(s))  # 依存句法
    return nlp.pos_tag(s)


def structureFilter(s1, s2):
    """
    判断两个句子结构是否相同
    """
    p1 = stanfordParser(s1)
    p2 = stanfordParser(s2)
    if len(p1) != len(p2):
        return False
    for i in range(0, len(p1)):
        if p1[i][1] != p2[i][1]:
            return False
    return True


def close():
    nlp.close()


if __name__ == "__main__":

    while True:
        s1 = input("input s1: ")
        s2 = input("input s2: ")
        if s1 == "end":
            break
        flag = structureFilter(s1, s2)
        if flag:
            print("same structure")
        else:
            print("wrong structure")
    close()
