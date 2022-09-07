import yaml
import json

with open("ft_VGG19_3_dt_Xception_13_128.yaml","r") as yaml_in, open("ft_VGG19_3_dt_Xception_13_128.json","w") as json_out:
	yaml_object = yaml.safe_load(yaml_in)
	json.dump(yaml_object, json_out)
