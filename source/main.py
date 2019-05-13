from matting.deep_matting import load_model, deep_matting
from matting.closed_form_matting import closed_form_matting_with_trimap

from mainWidget import initialWidget

def main():
    methods = []
    try:
        raise Exception("aa")
        model1 = None
        model2 = None
        try:
            model1 = load_model('/data2/human_matting/models/alpha_models_0305/alpha_net_100.pth', 0)
            model2 = load_model('/data2/human_matting/models/alpha_models_bg/alpha_net_100.pth', 0)
        except:
            model1 = load_model('/home/wuxian/human_matting/models/alpha_models_0305/alpha_net_100.pth', 0)
            model2 = load_model('/home/wuxian/human_matting/models/alpha_models_bg/alpha_net_100.pth', 0)

        a = lambda x, y : deep_matting(x, y, model1, 0)
        b = lambda x, y : deep_matting(x, y, model2, 0)
        c = lambda x, y : closed_form_matting_with_trimap(x / 255.0, y[:, :, 0] / 255.0) * 255.0
        loadList = '../final_list.txt'
        methods = [a, b, c]
        print("load model success!!!")
    except:
        print("load model failed...")
        a = lambda x, y: y
        b = lambda x, y: x
        c = lambda x, y: x / 2 + y / 2
        loadList = '../list.txt'
        methods = [a, b, c]
    initialWidget(loadList, *methods)

if __name__ == "__main__":
    main()
