# Royal Clash

Royal Clash é um jogo de cartas estratégico onde você constrói seu deck e batalha contra outros jogadores. O jogo combina elementos de estratégia, coleta de cartas e batalhas épicas.

## Características

- Sistema de cartas com diferentes raridades (Comum, Rara, Épica e Lendária)
- Batalhas estratégicas com sistema de mana e efeitos especiais
- Loja com ofertas diárias e especiais
- Sistema de baús e recompensas
- Interface gráfica moderna e responsiva
- Efeitos sonoros e visuais imersivos

## Requisitos

- Python 3.8 ou superior
- Pygame 2.5.2
- Pillow 10.2.0
- CustomTkinter 5.2.1
- Outras dependências listadas em requirements.txt

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/royal-clash.git
cd royal-clash
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o jogo:
```bash
python game/main.py
```

## Como Jogar

1. **Criar uma Conta**
   - Inicie o jogo e crie um nome de usuário
   - Você receberá um deck inicial de cartas

2. **Construir seu Deck**
   - Acesse o Deck Builder
   - Selecione até 8 cartas para seu deck
   - Estratégia é fundamental!

3. **Batalhar**
   - Enfrente outros jogadores em batalhas estratégicas
   - Use sua mana sabiamente
   - Aproveite os efeitos especiais das cartas

4. **Colecionar Cartas**
   - Ganhe baús após as batalhas
   - Compre cartas na loja
   - Atualize suas cartas favoritas

5. **Progressão**
   - Ganhe troféus nas batalhas
   - Suba de nível
   - Desbloqueie novas cartas e recursos

## Estrutura do Projeto

```
royal-clash/
├── assets/
│   ├── cards/      # Imagens das cartas
│   ├── avatars/    # Avatares dos jogadores
│   ├── sounds/     # Efeitos sonoros
│   └── shop/       # Imagens da loja
├── data/           # Dados do jogo
├── game/
│   ├── main.py     # Ponto de entrada do jogo
│   ├── battle.py   # Lógica de batalha
│   ├── cards.py    # Sistema de cartas
│   └── shop.py     # Sistema de loja
└── requirements.txt # Dependências
```

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
