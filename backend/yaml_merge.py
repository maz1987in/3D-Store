#pip install HiYaPyCo --upgrade
import hiyapyco
import os

base_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'app'
    )
)
yaml_list = ['app/static/swagger_mini.yaml']
#print(base_path)
for candidate in os.listdir(base_path):
    # Must be a directory.
    if not os.path.isdir(os.path.join(base_path, candidate)):
        continue
    #print(candidate)
    #print(os.path.join(base_path+"/app", candidate,'swagger.yaml'))
    if os.path.exists(os.path.join(base_path, candidate,'swagger.yaml')):
        if candidate != 'static':
            mod_name = 'app/'+candidate + '/swagger.yaml'
            yaml_list.append(mod_name)
            print(mod_name)

merged_yaml = hiyapyco.load(yaml_list, method=hiyapyco.METHOD_MERGE, interpolate=True, failonmissingfiles=True)

f = open('app/static/swagger.yaml', "w")
f.write(hiyapyco.dump(merged_yaml))
f.close()
#print(hiyapyco.dump(merged_yaml))