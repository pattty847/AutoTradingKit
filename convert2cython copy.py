import os

def convert_to_cython(py_file):
    cy_file = ""
    if "init" not in py_file:
        with open(py_file, 'r',encoding= "utf-8") as f:
            py_code = f.read()
            if "@njit(" in py_code:
                pyd_name = os.path.splitext(py_file)[0] + ".cp313-win_amd64.pyd"
                if os.path.exists(pyd_name):
                    print(pyd_name)
                    os.remove(pyd_name)
                    return
            cy_file = os.path.splitext(py_file)[0] + ".pyx"
            with open(cy_file, 'w',encoding="utf-8") as f:
                f.write(py_code)
    return cy_file

def convert_one(path_:str=r"atklip\graph_objects\chart_component\viewchart.py"):
    pyx_path = convert_to_cython(path_)
    # os.system(f'cythonize --build --inplace -3 --3str --cplus --force --keep-going --no-docstrings {path_}')

for root, _, files in os.walk("atklip"):
    for file in files:
        src_path = os.path.join(root, file)
        # Bỏ qua thư mục __pycache__
        if "__pycache__" in src_path:
            continue
        
        if "__init__" in src_path:
            continue
        
        if "resource" in src_path:
            continue
        
        # if src_path.endswith(".pyd"):
        #     print("delete old",src_path)
        #     os.remove(src_path)
        
        if src_path.endswith(".py"):
            print(src_path)
            convert_one(src_path)