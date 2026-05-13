export function validateYAML(yamlText){

  try{

    jsyaml.load(yamlText);

    return {
      valid: true,
      message: "✅ YAML válido"
    };

  }catch(err){

    let line = 0;

    if(err.mark){

      line = err.mark.line + 1;
    }

    return {
      valid: false,
      line,
      message:
        `❌ YAML inválido na linha ${line}`
    };
  }
}

// =====================================================
// HIGHLIGHT ERROR
// =====================================================

export function highlightError(
  textarea,
  line
){

  const lines =
    textarea.value.split("\n");

  let start = 0;

  for(
    let i=0;
    i<line-1;
    i++
  ){

    start +=
      lines[i].length + 1;
  }

  const end =
    start +
    (
      lines[line-1]?.length || 0
    );

  textarea.focus();

  textarea.setSelectionRange(
    start,
    end
  );
}

// =====================================================
// GITLAB -> GITHUB
// =====================================================

export function convertToGitHub(yaml){

  try{

    const parsed =
      jsyaml.load(yaml);

    let jobs = "";

    for(const key in parsed){

      if(parsed[key]?.script){

        jobs += `
  ${key}:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - run: |
${parsed[key].script.map(
  s => "          " + s
).join("\n")}
`;
      }
    }

    return `name: CI

on:
  push:

jobs:
${jobs}`;

  }catch{

    return "# erro ao converter";
  }
}