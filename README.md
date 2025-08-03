# Blackjack

Um jogo de **Blackjack** desenvolvido em **Python**.

## Como configurar e executar

### 1. Instalar Miniconda
Se ainda não tens o Miniconda instalado, faz o download em:  
[https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)  
Escolhe a versão para o teu sistema operativo (Windows/Linux/Mac).

---

### 2. Criar e ativar o ambiente virtual

Cria um novo ambiente chamado `blackjack` com **Python 3.9**:
```bash
conda create -n blackjack python=3.9
```

Depois ativa o ambiente:
```bash
conda activate blackjack
```

Garante que estás na pasta raiz do projeto, onde está o ficheiro requirements.txt, e instala as dependências:
```bash
pip install -r requirements.txt
```

Com o ambiente blackjack ativo, corre o jogo:
```bash
python main.py
```

Quando terminares, podes sair do ambiente virtual com:
```bash
conda deactivate
```