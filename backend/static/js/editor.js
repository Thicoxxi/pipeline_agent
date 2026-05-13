export function highlightError(
  textarea,
  line
){

  const lines =
    textarea.value.split("\n");

  let start = 0;

  for(let i=0;i<line-1;i++){

    start += lines[i].length + 1;
  }

  const end =
    start +
    (lines[line-1]?.length || 0);

  textarea.focus();

  textarea.setSelectionRange(
    start,
    end
  );
}