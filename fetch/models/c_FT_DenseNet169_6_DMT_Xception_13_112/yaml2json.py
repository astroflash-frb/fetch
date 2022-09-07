import yaml
import json

with open("ft_DenseNet169_6_dt_Xception_13_112.yaml","r") as yaml_in, open("ft_DenseNet169_6_dt_Xception_13_112.json","w") as json_out:
	yaml_object = yaml.safe_load(yaml_in)
	json.dump(yaml_object, json_out)
