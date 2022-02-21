import typing
from google.cloud import secretmanager
from google.cloud import bigquery
import json
from typing import Any, Dict, Optional


class GcpUtils(object):
    storage_url: str = "https://storage.googleapis.com/archive-mint/v1/metadata/"


    @staticmethod
    def get_json_dict_from_secret_resource_id(
            secret_resource_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Assumes that the secret is stored as a dictionary
        """
        client_ = secretmanager.SecretManagerServiceClient()
        response = client_.access_secret_version(name=secret_resource_id)
        try:
            credentials = json.loads(response.payload.data.decode("UTF-8"))
        except json.decoder.JSONDecodeError as e:
            repr(e)
            print("Make sure to check if the secret format is good")
            raise e
        else:
            return credentials

    @staticmethod
    def insert_rows_bigquery(
        rows: typing.List[typing.Dict[str, typing.Any]], table_id: str
    ) -> typing.Sequence[dict]:
        bq_client = bigquery.Client()
        table = bq_client.get_table(table_id)
        return bq_client.insert_rows_json(table, rows)

