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