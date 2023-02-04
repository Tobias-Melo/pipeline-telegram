import os
import json
import logging
from datetime import datetime, timedelta, timezone

import boto3
import pyarrow as pa
import pyarrow.parquet as pq


def lambda_handler(event: dict, context: dict) -> bool:

  '''
  Diariamente é executado para compactar as diversas mensagensm, no formato
  JSON, do dia anterior, armazenadas no bucket de dados cru, em um único 
  arquivo no formato PARQUET, armazenando-o no bucket de dados enriquecidos
  '''

  # vars de ambiente

  RAW_BUCKET = os.environ['AWS_S3_BUCKET']
  ENRICHED_BUCKET = os.environ['AWS_S3_ENRICHED']

  # vars lógicas

  tzinfo = timezone(offset=timedelta(hours=-3))
  date = (datetime.now(tzinfo) - timedelta(days=1)).strftime('%Y-%m-%d')
  timestamp = datetime.now(tzinfo).strftime('%Y%m%d%H%M%S%f')

  # código principal
  
  athena = boto3.client('athena')
  table = None
  client = boto3.client('s3')
  
  query = 'MSCK REPAIR TABLE telegram;'

  try:

      response = client.list_objects_v2(Bucket=RAW_BUCKET, Prefix=f'telegram/context_date={date}')

      for content in response['Contents']:

        key = content['Key']
        client.download_file(RAW_BUCKET, key, f"/tmp/{key.split('/')[-1]}")

        with open(f"/tmp/{key.split('/')[-1]}", mode='r', encoding='utf8') as fp:

          data = json.load(fp)
          data = data["message"]

        parsed_data = parse_data(data=data)
        iter_table = pa.Table.from_pydict(mapping=parsed_data)

        if table:

          table = pa.concat_tables([table, iter_table])

        else:

          table = iter_table
          iter_table = None
          
      pq.write_table(table=table, where=f'/tmp/{timestamp}.parquet')
      client.upload_file(f"/tmp/{timestamp}.parquet", ENRICHED_BUCKET, f"telegram/context_date={date}/{timestamp}.parquet")
      
      queryresult = athena.start_query_execution(QueryString=query,ResultConfiguration={'OutputLocation': 's3://ebac-bucket-results/'})

      return True
  
  except Exception as exc:
      logging.error(msg=exc)
      return False
      

def parse_data(data: dict) -> dict:

  date = datetime.now().strftime('%Y-%m-%d')
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  parsed_data = {'message_id': '',
                'user_id': '',
                'user_is_bot': '',
                'user_first_name': '',
                'chat_id': '',
                'chat_type': '',
                'date': '',
                'message_type': '',
                'message_content': '',
                'context_date': '',
                'context_timestamp': ''}

  for key, value in data.items():
    parsed_data['message_id'] = [data.get('message_id')]
    parsed_data['user_id'] = [data['from'].get('id')]
    parsed_data['user_is_bot'] = [data['from'].get('is_bot')]
    parsed_data['user_first_name'] = [data['from'].get('first_name')]
    parsed_data['chat_id'] = [data['chat'].get('id')]
    parsed_data['chat_type'] = [data['chat'].get('type')]
    parsed_data['date'] = [data.get('date')]
    name_message = list(data.keys())[-1]

    if name_message == 'photo':
      parsed_data['message_type'] = ['photo']
      parsed_data['message_content'] = ['photo']
      
    elif name_message == 'sticker':
      parsed_data['message_type'] = ['sticker']
      parsed_data['message_content'] = [data[name_message].get('emoji')]
      
    elif name_message == 'text':
      parsed_data['message_type'] = ['text']
      parsed_data['message_content'] = [data['text']]
      
    elif name_message == 'document':
      parsed_data['message_type'] = ['document']
      parsed_data['message_content'] = [data[name_message].get('file_name')]
      
    else:
      parsed_data['message_type'] = [name_message]
      parsed_data['message_content'] = [name_message]
            

  parsed_data['context_date'] = [date]
  parsed_data['context_timestamp'] = [timestamp]
  
  return parsed_data