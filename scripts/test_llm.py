from src.llm_agent import extract_pipeline_params

examples = [
    'Gerar pipeline para .NET Core 8 com upload no nexus my-repo e versão 8',
    'Gerar pipeline para .NET framework 4.8 e enviar para nexus releases',
    'Gerar pipeline para Python com pyinstaller e upload no nexus python-repo version 0.2.0',
]

for ex in examples:
    print('PROMPT:', ex)
    p = extract_pipeline_params(ex)
    print(p)
    print('-' * 60)
