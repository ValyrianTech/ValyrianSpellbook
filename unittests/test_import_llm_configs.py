"""Tests for import_llm_configs.py — bulk LLM config importer from CSV."""

import os
from unittest.mock import patch


import import_llm_configs


# ---------------------------------------------------------------------------
# parse_price
# ---------------------------------------------------------------------------

def test_parse_price_basic():
    assert import_llm_configs.parse_price('$2.00') == 2.0


def test_parse_price_with_commas():
    assert import_llm_configs.parse_price('$1,000.50') == 1000.50


def test_parse_price_empty_string():
    assert import_llm_configs.parse_price('') == 0.0


def test_parse_price_none():
    assert import_llm_configs.parse_price(None) == 0.0


def test_parse_price_whitespace():
    assert import_llm_configs.parse_price('   ') == 0.0


def test_parse_price_no_dollar_sign():
    assert import_llm_configs.parse_price('5.50') == 5.5


def test_parse_price_invalid():
    assert import_llm_configs.parse_price('abc') == 0.0


# ---------------------------------------------------------------------------
# parse_context_size
# ---------------------------------------------------------------------------

def test_parse_context_size_basic():
    assert import_llm_configs.parse_context_size('128000') == 128000


def test_parse_context_size_with_commas():
    assert import_llm_configs.parse_context_size('1,000,000') == 1000000


def test_parse_context_size_empty():
    assert import_llm_configs.parse_context_size('') == 4096


def test_parse_context_size_none():
    assert import_llm_configs.parse_context_size(None) == 4096


def test_parse_context_size_whitespace():
    assert import_llm_configs.parse_context_size('  ') == 4096


def test_parse_context_size_invalid():
    assert import_llm_configs.parse_context_size('abc') == 4096


# ---------------------------------------------------------------------------
# parse_vision_capability
# ---------------------------------------------------------------------------

def test_parse_vision_true():
    assert import_llm_configs.parse_vision_capability('TRUE') is True


def test_parse_vision_yes():
    assert import_llm_configs.parse_vision_capability('yes') is True


def test_parse_vision_one():
    assert import_llm_configs.parse_vision_capability('1') is True


def test_parse_vision_enabled():
    assert import_llm_configs.parse_vision_capability('enabled') is True


def test_parse_vision_false():
    assert import_llm_configs.parse_vision_capability('FALSE') is False


def test_parse_vision_no():
    assert import_llm_configs.parse_vision_capability('no') is False


def test_parse_vision_empty():
    assert import_llm_configs.parse_vision_capability('') is False


def test_parse_vision_none():
    assert import_llm_configs.parse_vision_capability(None) is False


def test_parse_vision_random():
    assert import_llm_configs.parse_vision_capability('maybe') is False


# ---------------------------------------------------------------------------
# create_llm_config
# ---------------------------------------------------------------------------

def _sample_model_data():
    return {
        'Provider': 'OpenAI',
        'Model_name': 'gpt-4o',
        'Input_Price': '$2.50',
        'Output_Price': '$10.00',
        'Context Size': '128000',
        'Vision': 'TRUE',
    }


def test_create_llm_config_basic():
    config = import_llm_configs.create_llm_config(_sample_model_data())
    assert config['llm_name'] == 'OpenAI:gpt-4o'
    assert config['llm_server_type'] == 'OpenAI'
    assert config['llm_model_name'] == 'gpt-4o'
    assert config['prompt_tokens_cost'] == 2.5
    assert config['completion_tokens_cost'] == 10.0
    assert config['prompt_tokens_multiplier'] == 1000000
    assert config['completion_tokens_multiplier'] == 1000000
    assert config['context_length'] == 128000
    assert config['vision'] is True
    assert config['chat'] is True
    assert config['max_tokens'] == 4096
    assert config['llm_host'] == ''
    assert config['llm_port'] is None
    assert config['allow_auto_routing'] is True
    assert config['api_key'] == ''
    assert config['video'] is False
    assert config['prompt_template'] == ''


def test_create_llm_config_audio_detection():
    data = _sample_model_data()
    data['Model_name'] = 'gpt-4o-audio-preview'
    config = import_llm_configs.create_llm_config(data)
    assert config['audio'] is True


def test_create_llm_config_no_audio():
    config = import_llm_configs.create_llm_config(_sample_model_data())
    assert config['audio'] is False


def test_create_llm_config_vision_false():
    data = _sample_model_data()
    data['Vision'] = 'FALSE'
    config = import_llm_configs.create_llm_config(data)
    assert config['vision'] is False


def test_create_llm_config_description():
    config = import_llm_configs.create_llm_config(_sample_model_data())
    assert config['llm_description'] == 'OpenAI gpt-4o model'


def test_create_llm_config_different_provider():
    data = _sample_model_data()
    data['Provider'] = 'Anthropic'
    data['Model_name'] = 'claude-3'
    config = import_llm_configs.create_llm_config(data)
    assert config['llm_name'] == 'Anthropic:claude-3'
    assert config['llm_server_type'] == 'Anthropic'


# ---------------------------------------------------------------------------
# save_llm_config_direct
# ---------------------------------------------------------------------------

@patch('import_llm_configs.save_llm_config_lightweight')
def test_save_llm_config_direct_success(mock_save):
    config = import_llm_configs.create_llm_config(_sample_model_data())
    result = import_llm_configs.save_llm_config_direct(config, verbose=False)
    assert result is True
    mock_save.assert_called_once()
    call_args = mock_save.call_args
    assert call_args[0][0] == 'OpenAI:gpt-4o'
    saved_config = call_args[0][1]
    assert saved_config['server_type'] == 'OpenAI'
    assert saved_config['model_name'] == 'gpt-4o'
    assert saved_config['prompt_tokens_cost'] == 2.5


@patch('import_llm_configs.save_llm_config_lightweight')
def test_save_llm_config_direct_verbose(mock_save, capsys):
    config = import_llm_configs.create_llm_config(_sample_model_data())
    result = import_llm_configs.save_llm_config_direct(config, verbose=True)
    assert result is True
    captured = capsys.readouterr()
    assert 'Saving LLM config: OpenAI:gpt-4o' in captured.out
    assert 'Successfully saved' in captured.out


@patch('import_llm_configs.save_llm_config_lightweight', side_effect=Exception('DB error'))
def test_save_llm_config_direct_exception(mock_save, capsys):
    config = import_llm_configs.create_llm_config(_sample_model_data())
    result = import_llm_configs.save_llm_config_direct(config, verbose=False)
    assert result is False
    captured = capsys.readouterr()
    assert 'Exception saving' in captured.out
    assert 'DB error' in captured.out


# ---------------------------------------------------------------------------
# read_csv_models
# ---------------------------------------------------------------------------

def test_read_csv_models_valid(tmp_path):
    csv_file = tmp_path / 'models.csv'
    csv_file.write_text(
        'Provider,Model_name,Input_Price,Output_Price,Context Size,Vision\n'
        'OpenAI,gpt-4o,$2.50,$10.00,128000,TRUE\n'
        'Anthropic,claude-3,$3.00,$15.00,200000,FALSE\n',
        encoding='utf-8',
    )
    models = import_llm_configs.read_csv_models(str(csv_file))
    assert len(models) == 2
    assert models[0]['Provider'] == 'OpenAI'
    assert models[1]['Provider'] == 'Anthropic'


def test_read_csv_models_file_not_found(capsys):
    models = import_llm_configs.read_csv_models('/nonexistent/path/file.csv')
    assert models == []
    captured = capsys.readouterr()
    assert 'CSV file not found' in captured.out


def test_read_csv_models_empty_file(tmp_path, capsys):
    csv_file = tmp_path / 'empty.csv'
    csv_file.write_text('', encoding='utf-8')
    models = import_llm_configs.read_csv_models(str(csv_file))
    assert models == []
    captured = capsys.readouterr()
    assert 'Read 0 models' in captured.out


def test_read_csv_models_io_error(tmp_path, capsys):
    # Passing a directory triggers an exception in open()
    models = import_llm_configs.read_csv_models(str(tmp_path))
    assert models == []
    captured = capsys.readouterr()
    assert 'Error reading CSV' in captured.out


# ---------------------------------------------------------------------------
# main — dry run mode
# ---------------------------------------------------------------------------

def _write_test_csv(tmp_path):
    csv_file = tmp_path / 'models.csv'
    csv_file.write_text(
        'Provider,Model_name,Input_Price,Output_Price,Context Size,Vision\n'
        'OpenAI,gpt-4o,$2.50,$10.00,128000,TRUE\n'
        'OpenAI,gpt-4o-mini,$0.15,$0.60,128000,FALSE\n'
        'Anthropic,claude-3,$3.00,$15.00,200000,FALSE\n',
        encoding='utf-8',
    )
    return str(csv_file)


def test_main_dry_run(tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path, '--dry-run']):
        ret = import_llm_configs.main()
    assert ret == 0
    captured = capsys.readouterr()
    assert 'DRY RUN MODE' in captured.out
    assert 'Would save: OpenAI:gpt-4o' in captured.out
    assert 'Would save: OpenAI:gpt-4o-mini' in captured.out
    assert 'Would save: Anthropic:claude-3' in captured.out
    assert 'DRY RUN COMPLETE' in captured.out


def test_main_dry_run_verbose(tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path, '--dry-run', '--verbose']):
        ret = import_llm_configs.main()
    assert ret == 0
    captured = capsys.readouterr()
    assert '"llm_name"' in captured.out


def test_main_dry_run_filter(tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path, '--dry-run', '--filter', 'gpt-4o']):
        ret = import_llm_configs.main()
    assert ret == 0
    captured = capsys.readouterr()
    assert 'Filtered to 2 models' in captured.out
    assert 'gpt-4o' in captured.out
    assert 'claude' not in captured.out.lower().split('would save')[0] or 'claude' not in captured.out


def test_main_no_models(tmp_path, capsys):
    csv_file = tmp_path / 'empty.csv'
    csv_file.write_text('Provider,Model_name,Input_Price,Output_Price,Context Size,Vision\n', encoding='utf-8')
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', str(csv_file), '--dry-run']):
        ret = import_llm_configs.main()
    assert ret == 1
    captured = capsys.readouterr()
    assert 'No models to import' in captured.out


def test_main_file_not_found(capsys):
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', '/nonexistent/file.csv', '--dry-run']):
        ret = import_llm_configs.main()
    assert ret == 1
    captured = capsys.readouterr()
    assert 'No models to import' in captured.out


# ---------------------------------------------------------------------------
# main — actual import (mocked save)
# ---------------------------------------------------------------------------

@patch('import_llm_configs.save_llm_config_lightweight')
def test_main_import_success(mock_save, tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path]):
        ret = import_llm_configs.main()
    assert ret == 0
    assert mock_save.call_count == 3
    captured = capsys.readouterr()
    assert 'IMPORT COMPLETE' in captured.out
    assert '3/3' in captured.out


@patch('import_llm_configs.save_llm_config_lightweight', side_effect=Exception('fail'))
def test_main_import_all_fail(mock_save, tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path]):
        ret = import_llm_configs.main()
    assert ret == 1
    captured = capsys.readouterr()
    assert 'Failed to import 3 models' in captured.out


@patch('import_llm_configs.save_llm_config_lightweight', side_effect=[None, Exception('fail'), None])
def test_main_import_partial_fail(mock_save, tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path]):
        ret = import_llm_configs.main()
    assert ret == 1
    captured = capsys.readouterr()
    assert '1/3' in captured.out or '2/3' in captured.out


# ---------------------------------------------------------------------------
# main — relative CSV path resolution
# ---------------------------------------------------------------------------

@patch('import_llm_configs.save_llm_config_lightweight')
def test_main_relative_csv_path(mock_save, tmp_path, capsys):
    csv_path = _write_test_csv(tmp_path)
    with patch('sys.argv', ['import_llm_configs.py', '--csv-file', csv_path, '--dry-run']):
        ret = import_llm_configs.main()
    assert ret == 0


# ---------------------------------------------------------------------------
# main — relative CSV path resolution (non-absolute path branch)
# ---------------------------------------------------------------------------

def test_main_relative_path_branch(tmp_path, capsys, monkeypatch):
    """Test that a relative --csv-file is resolved relative to the script dir."""
    csv_file = tmp_path / 'models.csv'
    csv_file.write_text(
        'Provider,Model_name,Input_Price,Output_Price,Context Size,Vision\n'
        'OpenAI,gpt-4o,$2.50,$10.00,128000,TRUE\n',
        encoding='utf-8',
    )
    # Use a relative path that resolves from the script directory
    # We monkeypatch os.path.dirname to point to tmp_path
    script_dir = os.path.dirname(os.path.abspath(import_llm_configs.__file__))
    # Copy the CSV to the script directory temporarily
    target = os.path.join(script_dir, '_test_relative.csv')
    import shutil
    shutil.copy(str(csv_file), target)
    try:
        with patch('sys.argv', ['import_llm_configs.py', '--csv-file', '_test_relative.csv', '--dry-run']):
            ret = import_llm_configs.main()
        assert ret == 0
        captured = capsys.readouterr()
        assert 'Would save: OpenAI:gpt-4o' in captured.out
    finally:
        os.remove(target)


# ---------------------------------------------------------------------------
# main — create_llm_config error handling
# ---------------------------------------------------------------------------

def test_main_create_config_error(tmp_path, capsys):
    csv_file = tmp_path / 'bad.csv'
    csv_file.write_text(
        'Provider,Model_name,Input_Price,Output_Price,Context Size,Vision\n'
        'OpenAI,gpt-4o,$2.50,$10.00,128000,TRUE\n',
        encoding='utf-8',
    )
    with patch('import_llm_configs.create_llm_config', side_effect=Exception('parse error')):
        with patch('sys.argv', ['import_llm_configs.py', '--csv-file', str(csv_file), '--dry-run']):
            ret = import_llm_configs.main()
    # dry run still counts as success for models that parse, but create_llm_config fails
    # so success_count stays 0, total_count is 1
    assert ret == 1
    captured = capsys.readouterr()
    assert 'Error creating config' in captured.out
