import evadb
import os
import json

READ_MODE = 'r'

def set_openai_key():
    os.environ['OPENAI_API_KEY'] = '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'

def load_config(file_path):
    with open(file_path, READ_MODE) as file:
        config = json.load(file)
    return config

def init_database(config):
    cursor = evadb.connect().cursor()
    dataset = config['dataset']
    data_column = dataset['data_column']
    label_column = dataset['label_column']

    cursor.query("DROP TABLE IF EXISTS craigslist").df()

    print("table craigslist dropped ")

    cursor.query("CREATE TABLE IF NOT EXISTS craigslist ({} TEXT(10000), {} TEXT(20))".format(data_column, label_column)).df()

    print("Table craigslist created")
    return cursor

def load_data_into_db(cursor, file_path):
    cursor.query("LOAD CSV '{}' INTO craigslist".format(file_path)).df()

def label_data(cursor, config, output_file_path):

    # classsification
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

    query = 'SELECT {}, ChatGPT({}, "{}", "{}") FROM craigslist LIMIT 5'.format(data_column, data_column, context, input_prompt)
    result_df = cursor.query(query).df()
    result_df.rename(columns={ 'response': label_column }, inplace=True)

    result_df.to_csv(output_file_path, index=False)



def main():
    set_openai_key()
    config = load_config('config.json')
    cursor = init_database(config)
    load_data_into_db(cursor, './seed2.csv')
    label_data(cursor, config, './result2.csv')


if __name__=="__main__": 
    main() 
