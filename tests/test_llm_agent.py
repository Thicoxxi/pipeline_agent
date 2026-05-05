import os
from src.llm_agent import extract_pipeline_params


def test_extract_dotnet_framework_with_nexus():
    os.environ['LLM_PROVIDER'] = 'local'
    p = extract_pipeline_params('Gerar pipeline para .NET framework versao 4.6 com upload no nexus')
    assert p['nexus_wanted'] is True
    assert p['language'] == 'dotnetframework' or 'dotnetframework' in str(p['language']).lower()


def test_extract_python_defaults():
    os.environ['LLM_PROVIDER'] = 'local'
    p = extract_pipeline_params('Gerar pipeline para Python com pyinstaller e upload no nexus')
    assert p['language'] == 'python'
    assert p['artifact_path'] == 'dist/'


def test_extract_node_detection():
    os.environ['LLM_PROVIDER'] = 'local'
    p = extract_pipeline_params('Pipeline para Node.js que faça build e upload')
    assert p['language'] == 'node'
    assert p['artifact_path'] == 'dist/'
