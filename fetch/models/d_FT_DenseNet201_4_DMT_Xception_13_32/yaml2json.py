import yaml
import json

with open("ft_DenseNet201_4_dt_Xception_13_32.yaml","r") as yaml_in, open("ft_DenseNet201_4_dt_Xception_13_32.json","w") as json_out:
	yaml_object = yaml.safe_load(yaml_in)
	json.dump(yaml_object, json_out)
