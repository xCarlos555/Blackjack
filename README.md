# Blackjack

A **Blackjack** game developed in **Python**.

## How to set up and run

### 1. Install Miniconda
If you don’t have Miniconda installed yet, download it from:  
[https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)  
Choose the version for your operating system (Windows/Linux/Mac).

---

### 2. Create and activate the virtual environment

Create a new environment named `blackjack` with **Python 3.9**:
```bash
conda create -n blackjack python=3.9
```

Then activate the environment:
```bash
conda activate blackjack
```

Make sure you are in the project’s root folder, where the requirements.txt file is located, and install the dependencies:
```bash
pip install -r requirements.txt
```

With the blackjack environment active, run the game:
```bash
python main.py
```

When you’re done, you can exit the virtual environment with:
```bash
conda deactivate
```

### 3. Delete the virtual environment

If you want to remove the blackjack environment completely:

```bash
conda env remove -n blackjack
```