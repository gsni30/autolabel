# Autolabel
Labelling datasets using evadb's ChatGPT function.
This app can be used for:
1. Classification (Binary and multi-class classification)
2. Named-Entity Recognition.

## Steps:
1. Create an OpenAI key.
2. Create a config file which will be used to generate the prompt and label the dataset. 
3. Run the command given in the Usage section.

## Usage
```
python3 autolabel.py --config_file_path 'config.json' --dataset_path './seed2.csv' --result_path './result.csv' --key 'sk-.....'
```

config_file_path: Path where the config file is stored.
dataset_path: Path where the dataset is stored. (For now only CSV's are supported).
result_path: Path where the results will be stored.
