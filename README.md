# Mega Sena Number Generator

Este repositório contém um programa em Python que gera números para a Mega Sena com base na frequência de números sorteados em concursos anteriores.

## Pré-requisitos

Para executar o programa, você precisa ter Python instalado em seu sistema.

- Para instalar Python, siga as instruções na [página oficial de download do Python](https://www.python.org/downloads/).

### Instalando as bibliotecas

No diretório do programa Python, crie um ambiente virtual e instale as dependências com os seguintes comandos:

```bash
python3 -m venv env
source env/bin/activate
pip install requests tqdm sqlite3
```

### Usando um ambiente virtual

Para criar um ambiente virtual, use o seguinte comando:

```bash
python3 -m venv env
```

Para ativar o ambiente virtual, use o seguinte comando:

```bash
source env/bin/activate
```

Para desativar o ambiente virtual, use o seguinte comando:

```bash
deactivate
```

## Executando o programa

No diretório do programa Python, execute o seguinte comando:

```bash
python main.py
```

O programa irá gerar um número definido de jogos únicos e escrevê-los no banco de dados SQLite `lottery.db`. Cada jogo é um array de números, e os números são escolhidos com base em suas frequências nos resultados dos concursos da Mega Sena.

## Aviso

Este programa é apenas para fins educacionais. Jogos da Mega Sena são jogos de azar e este programa não deve ser usado para jogar, pois as chances de perder são maiores do que as chances de ganhar. O autor deste código não tem qualquer responsabilidade se alguém usar este programa para criar jogos reais da Mega Sena.