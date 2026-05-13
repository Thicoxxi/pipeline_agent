export function convertToGitHub(yaml){

  try{

    const parsed = jsyaml.load(yaml);

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