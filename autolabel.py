import evadb
import os
import json
import argparse
import time

READ_MODE = 'r'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file_path',
                        type=str,
                        help='Config file path')
    parser.add_argument(
        '--dataset_path',
        type=str,
        help=
        'dataset path'
    )
    parser.add_argument(
        '--result_path',
        type=str,
        default='./results.csv',
        help=
        'file path to save the results'
    )
    parser.add_argument('--key',
                        type=str,
                        help='OpenAI API key')
    args = parser.parse_args()
    return args

def set_openai_key(key):
    os.environ['OPENAI_API_KEY'] = key

def load_config(file_path):
    with open(file_path, READ_MODE) as file:
        config = json.load(file)
    return config

def init_database(config):
    cursor = evadb.connect().cursor()
    dataset = config['dataset']
    data_column = dataset['data_column']
    label_column = dataset['label_column']
    cursor.query("DROP TABLE IF EXISTS {}".format(config['task_name'])).df()
    print("Table {} dropped ".format(config['task_name']))
    cursor.query("CREATE TABLE IF NOT EXISTS {} ({} TEXT(10000), {} TEXT(20))".format(config['task_name'], data_column, label_column)).df()
    print("Table {} created".format(config['task_name']))
    return cursor

def load_data_into_db(cursor, config, file_path):
    cursor.query("LOAD CSV '{}' INTO {}".format(file_path, config['task_name'])).df()

def calculate_accuracy(result, actual_label_col, expected_label_col):
    num_accurate_labels = (result[actual_label_col] == result[expected_label_col]).sum()
    print(result.shape)
    total_data = result.shape[0]
    return num_accurate_labels / (total_data*1.0)

def label_data(cursor, config, output_file_path):
    metrics = { }
    start_time = time.time()
    prompt = config['prompt']
    dataset = config['dataset']
    labels = prompt['labels']
    data_column = dataset['data_column']
    label_column = dataset['label_column']
    label_str = ''
    for label in labels:
        label_str += (label + '\n')
    input_prompt = prompt['task_guidelines'] + " \n " + label_str + " \n " + prompt['output_guidelines']
    context = prompt['example_template'].format(prompt['example_input'], prompt['example_output'])
    query = 'SELECT {}, {}, ChatGPT({}, "{}", "{}") FROM {}'.format(data_column, label_column, data_column, context, input_prompt, config['task_name'])
    result_df = cursor.query(query).df()
    accuracy = calculate_accuracy(result_df, 'response', label_column)
    df_to_write = result_df[[data_column, 'response']]
    df_to_write.rename(columns={ 'response': label_column }, inplace=True)
    df_to_write.to_csv(output_file_path, index=False)
    end_time = time.time()
    metrics['total_time_in_sec'] = end_time- start_time
    metrics['accuracy'] = accuracy
    metrics['count'] = df_to_write.shape[0]
    print(metrics)

def main():
    args = parse_args()
    set_openai_key(args.key)
    config = load_config(args.config_file_path)
    cursor = init_database(config)
    load_data_into_db(cursor, config, args.dataset_path)
    label_data(cursor, config, args.result_path)

if __name__=="__main__": 
    main() 
