from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP(r'E:\NLP\StanfordParser\stanford-corenlp-latest\stanford-corenlp-4.3.1')


def stanfordParser(s):
    return nlp.pos_tag(s)


def structureFilter(s1, s2):
    """
    判断两个句子结构是否相同
    """
    try:
        p1 = list(stanfordParser(s1))
        p2 = list(stanfordParser(s2))
    except:
        return False
    if len(p1) != len(p2):
        return False
    for i in range(0, len(p1)):
        if p1[i][1][0] != p2[i][1][0]:
            return False
    return True


def stanford_nlp_close():
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
    stanford_nlp_close()
