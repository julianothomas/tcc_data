const fs = require('fs');
const readline = require('readline');

const heuristicas = {
  '1': 'colunas_sem_nome',
  '2': 'colunas_vazias',
  '3': 'linhas_duplicadas',
  '4': 'desequilibrio_categorias',
  '5': 'miscoding_numerico',
  '6': 'miscoding_caps',
  '7': 'outliers'
};

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log("SELECIONE AS HEURÍSTICAS QUE DESEJA APLICAR:");
for (const [num, nome] of Object.entries(heuristicas)) {
  console.log(`${num}. ${nome}`);
}

rl.question("Digite os números separados por vírgula (ex: 1,3,5): ", (input) => {
  const selecionadas = input.split(',').map(i => heuristicas[i.trim()]).filter(Boolean);
  if (selecionadas.length === 0) {
    console.log("Nenhuma heurística válida selecionada. Encerrando.");
    rl.close();
    return;
  }

  fs.writeFileSync(
    'heuristicas.config.json',
    JSON.stringify({ heuristicas: selecionadas }, null, 2)
  );

  console.log("Preferências salvas em 'heuristicas.config.json'.");
  rl.close();
});
