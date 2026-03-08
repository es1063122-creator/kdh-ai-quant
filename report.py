def print_result(name, prob, acc):

    print("")
    print("종목:", name)

    print("상승확률:", round(prob * 100, 2), "%")

    print("백테스트 정확도:", round(acc * 100, 2), "%")