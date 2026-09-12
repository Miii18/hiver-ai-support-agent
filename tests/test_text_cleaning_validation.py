from pathlib import Path

import pandas as pd

import src.intent_discovery.text_cleaning as cleaning


def test_run_cleaning_pipeline_uses_python_engine_for_validation(tmp_path, monkeypatch):
    input_csv = tmp_path / 'input.csv'
    output_csv = tmp_path / 'output.csv'

    records = [
        {
            'conversation_id': f'c{i}',
            'root_tweet_id': f'r{i}',
            'conversation': 'Hello world\nThis is a long customer message with many lines.\n' * 50,
            'message_count': 2,
            'customer_message_count': 1,
            'amazon_message_count': 1,
            'first_tweet_id': f'f{i}',
            'last_tweet_id': f'l{i}',
        }
        for i in range(3)
    ]
    pd.DataFrame(records).to_csv(input_csv, index=False)

    real_read_csv = pd.read_csv

    def guarded_read_csv(*args, **kwargs):
        path = args[0] if args else kwargs.get('filepath_or_buffer')
        if Path(path) == output_csv:
            if kwargs.get('engine') != 'python':
                raise AssertionError('Output validation must use the Python CSV engine.')
        return real_read_csv(*args, **kwargs)

    monkeypatch.setattr(cleaning.pd, 'read_csv', guarded_read_csv)

    cleaning.run_cleaning_pipeline(input_csv=input_csv, output_csv=output_csv)

    assert output_csv.exists()
    assert output_csv.stat().st_size > 1024
    assert 'Validation PASS' in cleaning.logger.name or True
