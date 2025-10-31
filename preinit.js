const fs = require('fs');
const path = require('path');
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

const pastaCSV = path.join(__dirname, '../husky/data');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log("CONFIGURAÇÃO DE HEURÍSTICAS");

let arquivosCSV = [];
try {
  arquivosCSV = fs.readdirSync(pastaCSV).filter(f => f.endsWith('.csv'));
} catch {
  console.log(`Pasta '${pastaCSV}' não encontrada. Crie-a e adicione arquivos CSV.`);
  rl.close();
  process.exit(1);
}

if (arquivosCSV.length === 0) {
  console.log("Nenhum arquivo CSV encontrado na pasta 'data/'. Adicione e tente novamente.");
  rl.close();
  process.exit(1);
}

console.log("\nARQUIVOS DISPONÍVEIS:");
arquivosCSV.forEach((f, i) => console.log(`${i + 1}. ${f}`));

rl.question("\nDigite o número do arquivo CSV que deseja validar: ", (inputArquivo) => {
  const indexArquivo = parseInt(inputArquivo.trim(), 10) - 1;
  const arquivoSelecionado = arquivosCSV[indexArquivo];

  if (!arquivoSelecionado) {
    console.log("Seleção inválida. Encerrando.");
    rl.close();
    return;
  }

  console.log("\nSELECIONE AS HEURÍSTICAS QUE DESEJA APLICAR:");
  for (const [num, nome] of Object.entries(heuristicas)) {
    console.log(`${num}. ${nome}`);
  }

  rl.question("\nDigite os números separados por vírgula (ex: 1,3,5): ", (inputHeuristicas) => {
    const selecionadas = inputHeuristicas
      .split(',')
      .map(i => heuristicas[i.trim()])
      .filter(Boolean);

    if (selecionadas.length === 0) {
      console.log("Nenhuma heurística válida selecionada. Encerrando.");
      rl.close();
      return;
    }

    const configuracao = {
      arquivo_csv: path.join(pastaCSV, arquivoSelecionado),
      heuristicas: selecionadas
    };

    fs.writeFileSync(
      'heuristicas.config.json',
      JSON.stringify(configuracao, null, 2)
    );

    console.log("\nPreferências salvas em 'heuristicas.config.json':");
    console.log(`Arquivo selecionado: ${arquivoSelecionado}`);
    console.log(`Heurísticas: ${selecionadas.join(', ')}`);

    rl.close();
  });
});
