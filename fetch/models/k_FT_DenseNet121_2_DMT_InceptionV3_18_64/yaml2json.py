import yaml
import json

with open("ft_DenseNet121_2_dt_InceptionV3_18_64.yaml","r") as yaml_in, open("ft_DenseNet121_2_dt_InceptionV3_18_64.json","w") as json_out:
	yaml_object = yaml.safe_load(yaml_in)
	json.dump(yaml_object, json_out)
