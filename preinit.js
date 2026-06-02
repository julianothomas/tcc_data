const fs = require('fs');
const path = require('path');
const readline = require('readline');

const BASE_DIR = __dirname;

const pastaHeuristicas = path.join(BASE_DIR, 'heuristicas');
const pastaDataPadrao = path.join(BASE_DIR, 'data');

const CONFIG_PATH = path.join(BASE_DIR, 'heuristicas.config.json');

const FORMATOS_SUPORTADOS = ['.csv', '.parquet'];

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log("CONFIGURAÇÃO DE HEURÍSTICAS");

// ------------------------------------------------
// CARREGAR HEURÍSTICAS
// ------------------------------------------------

let heuristicas = {};
let listaHeuristicas = [];

try {

  listaHeuristicas = fs
    .readdirSync(pastaHeuristicas)
    .filter(f => f.endsWith('.py') && !f.startsWith('__') && !f.startsWith('utils_'))
    .map(f => f.replace('.py', ''));

  listaHeuristicas.forEach((h, i) => {
    heuristicas[(i + 1).toString()] = h;
  });

} catch {

  console.log(`Pasta '${pastaHeuristicas}' não encontrada.`);
  rl.close();
  process.exit(1);

}

// ------------------------------------------------
// ESCOLHER ORIGEM DOS DADOS
// ------------------------------------------------

console.log("\nORIGEM DOS DADOS:");
console.log("1. Apenas pasta padrão ./data");
console.log("2. Outra pasta");
console.log("3. Pasta ./data + outra pasta");

rl.question("\nEscolha uma opção: ", (opcao) => {

  let pastasDados = [];

  // ------------------------------------------------
  // OPÇÃO 1
  // ------------------------------------------------

  if (opcao.trim() === "1") {

    pastasDados.push(pastaDataPadrao);

    carregarArquivosDados(pastasDados);

  }

  // ------------------------------------------------
  // OPÇÃO 2
  // ------------------------------------------------

  else if (opcao.trim() === "2") {

    rl.question("\nDigite os caminhos das pastas contendo os dados, separados por vírgula: ", (entradaPastas) => {

      const pastasExtras = entradaPastas
        .split(',')
        .map(p => p.trim())
        .filter(p => p.length > 0);

      const pastasInvalidas = pastasExtras.filter(p => !fs.existsSync(p));
      
      if (pastasInvalidas.length > 0) {

        console.log("\nAs seguintes pastas não foram encontradas:");
        pastasInvalidas.forEach(p => console.log(`- ${p}`));
        rl.close();
        return;

      }

      pastasDados.push(...pastasExtras);

      carregarArquivosDados(pastasDados);

    });

  }

  // ------------------------------------------------
  // OPÇÃO 3
  // ------------------------------------------------

  else if (opcao.trim() === "3") {

    rl.question("\nDigite os caminhos das pastas extras, separados por vírgula: ", (entradaPastas) => {

      const pastasExtras = entradaPastas
        .split(',')
        .map(p => p.trim())
        .filter(p => p.length > 0);

      const pastasInvalidas = pastasExtras.filter(p => !fs.existsSync(p));
      
      if (pastasInvalidas.length > 0) {

        console.log("\nAs seguintes pastas não foram encontradas:");
        pastasInvalidas.forEach(p => console.log(`- ${p}`));
        rl.close();
        return;

      }

      pastasDados.push(pastaDataPadrao);
      pastasDados.push(...pastasExtras);

      carregarArquivosDados(pastasDados);

    });

  }

  else {

    console.log("Opção inválida.");
    rl.close();

  }

});

// ------------------------------------------------
// CARREGAR ARQUIVOS DE DADOS
// ------------------------------------------------

function carregarArquivosDados(pastasDados) {

  let arquivosDados = [];

  for (const pasta of pastasDados) {

    try {

      const encontrados = fs
        .readdirSync(pasta)
        .filter(f =>
          FORMATOS_SUPORTADOS.includes(path.extname(f).toLowerCase())
        )
        .map(f => ({
          nome: f,
          caminho: path.join(pasta, f)
        }));

      arquivosDados.push(...encontrados);

    } catch {

      console.log(`Erro ao acessar pasta: ${pasta}`);

    }

  }

  if (arquivosDados.length === 0) {

    console.log("Nenhum arquivo de dados encontrado.");
    rl.close();
    return;

  }

  // ------------------------------------------------
  // LISTAR ARQUIVOS
  // ------------------------------------------------

  console.log("\nARQUIVOS DE DADOS ENCONTRADOS:");

  arquivosDados.forEach((f, i) => {
    console.log(`${i + 1}. ${f.nome} (${path.dirname(f.caminho)})`);
  });

  // ------------------------------------------------
  // ESCOLHER ARQUIVOS
  // ------------------------------------------------

  rl.question(
    "\nDigite os números dos arquivos separados por vírgula (ex: 1,3,5): ",
    (inputArquivos) => {

      const selecionados = inputArquivos
        .split(',')
        .map(i => arquivosDados[parseInt(i.trim(), 10) - 1])
        .filter(Boolean);

      if (selecionados.length === 0) {

        console.log("Nenhum arquivo válido selecionado.");
        rl.close();
        return;

      }

      // ------------------------------------------------
      // LISTAR HEURÍSTICAS
      // ------------------------------------------------

      console.log("\nSELECIONE AS HEURÍSTICAS:");

      for (const [num, nome] of Object.entries(heuristicas)) {

        console.log(`${num}. ${nome}`);

      }

      rl.question(
        "\nDigite os números separados por vírgula (ex: 1,3,5): ",
        (inputHeuristicas) => {

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
          // SALVAR CONFIGURAÇÃO
          // ------------------------------------------------

          const configuracao = {

            arquivos_dados: selecionados.map(a => a.caminho),
            heuristicas: selecionadas

          };

          fs.writeFileSync(
            CONFIG_PATH,
            JSON.stringify(configuracao, null, 2)
          );

          console.log("\nPreferências salvas em 'heuristicas.config.json':");

          console.log("\nArquivos selecionados:");

          selecionados.forEach(a => {
            console.log(`- ${a.nome} (${path.dirname(a.caminho)})`);
          });

          console.log(`\nHeurísticas: ${selecionadas.join(', ')}`);

          rl.close();

        }

      );

    }

  );

}