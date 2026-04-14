const fs = require('fs');
const path = require('path');
const readline = require('readline');

// ------------------------------------------------
// Caminhos base (robustos)
// ------------------------------------------------

const pastaHeuristicas = path.join(__dirname, 'heuristicas');
const pastaCSV = path.join(__dirname, 'data');
const caminhoConfig = path.join(__dirname, 'heuristicas.config.json');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log("CONFIGURAÇÃO DE HEURÍSTICAS");


// ------------------------------------------------
// CARREGAR HEURÍSTICAS DINAMICAMENTE
// ------------------------------------------------

let heuristicas = {};
let listaHeuristicas = [];

try {

  listaHeuristicas = fs
    .readdirSync(pastaHeuristicas)
    .filter(f => f.endsWith('.py') && !f.startsWith('__'))
    .map(f => f.replace('.py', ''));

  if (listaHeuristicas.length === 0) {
    console.log("Nenhuma heurística encontrada na pasta 'heuristicas/'.");
    rl.close();
    process.exit(1);
  }

  listaHeuristicas.forEach((h, i) => {
    heuristicas[(i + 1).toString()] = h;
  });

} catch (err) {

  console.log(`Erro ao acessar pasta de heurísticas: ${err.message}`);
  rl.close();
  process.exit(1);

}


// ------------------------------------------------
// LISTAR CSVs
// ------------------------------------------------

let arquivosCSV = [];

try {

  arquivosCSV = fs
    .readdirSync(pastaCSV)
    .filter(f => f.endsWith('.csv'));

} catch (err) {

  console.log(`Erro ao acessar pasta 'data/': ${err.message}`);
  rl.close();
  process.exit(1);

}

if (arquivosCSV.length === 0) {

  console.log("Nenhum arquivo CSV encontrado na pasta 'data/'.");
  rl.close();
  process.exit(1);

}

console.log("\nARQUIVOS DISPONÍVEIS:");

arquivosCSV.forEach((f, i) => {
  console.log(`${i + 1}. ${f}`);
});


// ------------------------------------------------
// ESCOLHER CSV
// ------------------------------------------------

rl.question("\nDigite o número do arquivo CSV que deseja validar: ", (inputArquivo) => {

  const indexArquivo = parseInt(inputArquivo.trim(), 10) - 1;
  const arquivoSelecionado = arquivosCSV[indexArquivo];

  if (!arquivoSelecionado) {
    console.log("Seleção inválida.");
    rl.close();
    return;
  }

  console.log("\nSELECIONE AS HEURÍSTICAS:");

  for (const [num, nome] of Object.entries(heuristicas)) {
    console.log(`${num}. ${nome}`);
  }

  rl.question("\nDigite os números separados por vírgula (ex: 1,3,5): ", (inputHeuristicas) => {

    const selecionadas = inputHeuristicas
      .split(',')
      .map(i => heuristicas[i.trim()])
      .filter(Boolean);

    if (selecionadas.length === 0) {
      console.log("Nenhuma heurística válida selecionada.");
      rl.close();
      return;
    }

    // ------------------------------------------------
    // Criar configuração
    // ------------------------------------------------

    const configuracao = {
      arquivo_csv: path.join(pastaCSV, arquivoSelecionado),
      heuristicas: selecionadas
    };

    // ------------------------------------------------
    // Salvar JSON no local correto
    // ------------------------------------------------

    try {

      fs.writeFileSync(
        caminhoConfig,
        JSON.stringify(configuracao, null, 2)
      );

    } catch (err) {

      console.log(`Erro ao salvar configuração: ${err.message}`);
      rl.close();
      return;

    }

    console.log("\nPreferências salvas em 'heuristicas.config.json':");
    console.log(`Arquivo selecionado: ${arquivoSelecionado}`);
    console.log(`Heurísticas: ${selecionadas.join(', ')}`);

    rl.close();

  });

});