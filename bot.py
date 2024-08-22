import discord
from discord.ext import commands
import re
import random
import json
import os

# Substitua pelo token do seu bot
TOKEN = 'MTI3NTUzMzczMjI1Nzg2MTY5Mg.GS-nxs.9Uua5gXusL11sb_a-4PocLk5D8M82vXEEZJR5A'
PASSWORD = '1234'

# Intents necessários para o bot funcionar
intents = discord.Intents.default()
intents.message_content = True  # Habilita leitura do conteúdo das mensagens
intents.presences = True  # Habilita acesso à presença dos membros (se necessário)

# Criação do bot com intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Nome do arquivo onde os dados serão armazenados
DATA_FILE = 'data.json'

# Função para carregar dados do arquivo JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Função para salvar dados no arquivo JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {'campanhas': {}}



@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')


@bot.command()
async def hello(ctx):
    await ctx.send(f'Olá, {ctx.author}!')

@bot.command()
async def roll(ctx, *, roll_string: str):
    """
    Rolagem de dados no formato NdM+X, onde N é o número de dados, M é o número de lados, e X é um modificador opcional.
    Exemplo: 2d6, 1d20+5
    """
    try:
        # Expressão regular para capturar os componentes do comando
        match = re.match(r'^(\d*)d(\d+)([+-]\d+)?$', roll_string)
        if not match:
            await ctx.send('Formato inválido. Use o formato NdM+X (por exemplo, 2d6 ou 1d20+5).')
            return

        num_dice = int(match.group(1)) if match.group(1) else 1
        num_sides = int(match.group(2))
        modifier = int(match.group(3) or 0)

        # Rolagem dos dados
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        # Formatação da resposta
        rolls_str = ', '.join(map(str, rolls))
        response = f'{total} <--- {rolls_str} = (modificador {modifier})'

        await ctx.send(response)

    except Exception as e:
        await ctx.send(f'Ocorreu um erro: {e}')


@bot.command()
async def add(ctx, password: str, *, input_text: str):
    """Adiciona uma pergunta e resposta se a senha estiver correta.
    O texto de entrada deve estar no formato: pergunta = resposta
    """
    if password == PASSWORD:
        try:
            # Divide a entrada em pergunta e resposta usando '=' como delimitador
            if '=' not in input_text:
                await ctx.send('Formato incorreto. Use o formato: pergunta = resposta.')
                return

            question, answer = input_text.split('=', 1)
            question = question.strip().lower()  # Converte a pergunta para minúsculas
            answer = answer.strip().lower()  # Converte a resposta para minúsculas

            data = load_data()
            data[question] = answer
            save_data(data)
            await ctx.send('Pergunta e resposta adicionadas com sucesso!')
        except ValueError:
            await ctx.send('Formato incorreto. Use o formato: pergunta = resposta.')
    else:
        await ctx.send('Senha incorreta. Não foi possível adicionar a pergunta e resposta.')


@bot.command()
async def get(ctx, *, question: str):
    """Obtém a resposta para uma pergunta. Não requer senha."""
    question = question.strip().lower()  # Converte a pergunta para minúsculas
    data = load_data()
    answer = data.get(question, 'Pergunta não encontrada.')
    await ctx.send(f'{answer}')

@bot.command()
async def ajuda(ctx):
    help_text = (

        "\n\n\n   - Cria uma nova campanha com as informações fornecidas.\n"
         "/criar_campanha <senha> = <nome_da_campanha> = <mestre> = <dia_da_semana> = <descricao> = <sistema> = <participantes_maximos>\n\n"
        "   - Entra em uma campanha existente com o personagem especificado.\n"
         "/entrar <nome_da_campanha> = <participante> = <raça> = <classe>\n\n"
        "   - Exibe todas as campanhas existentes e seus participantes.\n"
       "/campanhas\n\n"   
        "   - Exclui uma campanha existente, requer senha.\n"
         "/excluir <nome_da_campanha> = <senha>\n\n"
        "   - Edita uma campanha existente, requer senha.\n"
        "/editar <nome_da_campanha> = <senha> = <nova_descricao> = <novo_dia_da_semana> = <novo_participantes_maximos>\n"
    )
    await ctx.send(help_text)


    """Campanha"""


@bot.command()
async def criar_campanha(ctx, *, args):
    try:
        params = args.split('=')
        if len(params) != 7:
            await ctx.send(
                'Formato incorreto. Use: senha = nome_da_campanha = mestre = dia_da_semana = descricao = sistema = participantes_maximos')
            return

        senha = params[0].strip()
        nome_campanha = params[1].strip()
        mestre = params[2].strip()
        dia_da_semana = params[3].strip()
        descricao = params[4].strip()
        sistema = params[5].strip()

        try:
            participantes_maximos = int(params[6].strip())
        except ValueError:
            await ctx.send('O valor para participantes_maximos deve ser um número inteiro.')
            return

        data = load_data()

        if 'campanhas' not in data:
            data['campanhas'] = {}

        if nome_campanha in data['campanhas']:
            await ctx.send(f"Campanha '{nome_campanha}' já existe.")
            return

        data['campanhas'][nome_campanha] = {
            'senha': senha,
            'mestre': mestre,
            'dia_da_semana': dia_da_semana,
            'descricao': descricao,
            'sistema': sistema,
            'participantes_maximos': participantes_maximos,
            'participantes': {}
        }
        save_data(data)
        await ctx.send(f"Campanha '{nome_campanha}' criada com sucesso!")

    except Exception as e:
        await ctx.send(f"Ocorreu um erro ao tentar criar a campanha: {e}")



@bot.command()
async def entrar(ctx, *, entrada: str):
    try:
        # Dividir a entrada em componentes usando "=" como delimitador
        partes = entrada.split(" = ")
        if len(partes) != 4:
            await ctx.send("Por favor, use o formato: /entrar <nome_da_campanha> = <participante> = <raça> = <classe>")
            return

        nome_campanha, participante, raça, classe = partes

        data = load_data()

        if nome_campanha not in data['campanhas']:
            await ctx.send(f"Campanha '{nome_campanha}' não encontrada.")
            return

        campanha = data['campanhas'][nome_campanha]
        max_participantes = campanha['participantes_maximos']

        # Verifica se a campanha já atingiu o número máximo de participantes
        num_participantes_atual = sum(len(campanha['participantes'][p]) for p in campanha['participantes'])
        if num_participantes_atual >= max_participantes:
            await ctx.send(f"A campanha '{nome_campanha}' já atingiu o número máximo de {max_participantes} participantes.")
            return

        # Adicionando o personagem à campanha
        if participante not in campanha['participantes']:
            campanha['participantes'][participante] = []

        personagem = {'raça': raça, 'classe': classe}
        campanha['participantes'][participante].append(personagem)

        save_data(data)

        # Mensagem de confirmação
        await ctx.send(f"{participante} entrou na campanha '{nome_campanha}' como {raça} {classe}.")

    except Exception as e:
        await ctx.send(f"Ocorreu um erro ao tentar entrar na campanha: {e}")


@bot.command()
async def campanhas(ctx):
    try:
        data = load_data()

        if 'campanhas' not in data or not data['campanhas']:
            await ctx.send("Não há campanhas disponíveis no momento.")
            return

        resposta = "Campanhas Ativas:\n"
        for nome_campanha, detalhes in data['campanhas'].items():
            participantes = detalhes.get('participantes', {})
            max_participantes = detalhes.get('participantes_maximos', 0)
            descricao = detalhes.get('descricao', 'Descrição não disponível')
            dia_semana = detalhes.get('dia_semana', 'Dia da semana não definido')
            sistema = detalhes.get('sistema', 'Sistema não especificado')

            participantes_info = []
            for participante, personagens in participantes.items():
                for personagem in personagens:
                    participantes_info.append(f"{participante}: {personagem['raça']} {personagem['classe']}")

            num_participantes_atual = len(participantes_info)
            resposta += f"**{nome_campanha}**\nDescrição: {descricao}\nDia da Semana: {dia_semana}\nSistema: {sistema}\nParticipantes: {num_participantes_atual}/{max_participantes}\n"
            if participantes_info:
                resposta += "\n".join(participantes_info) + "\n"
            else:
                resposta += "Nenhum participante ainda.\n"

        await ctx.send(resposta.strip())

    except Exception as e:
        await ctx.send(f"Ocorreu um erro ao tentar listar as campanhas: {e}")


@bot.command()
async def excluir(ctx, *, args):
    try:
        # Divide os argumentos pelo símbolo '='
        params = args.split('=')

        if len(params) != 2:
            await ctx.send('Formato incorreto. Use: nome_da_campanha = senha')
            return

        nome_campanha = params[0].strip()
        senha = params[1].strip()

        # Carregando os dados existentes
        data = load_data()

        # Verifica se a campanha existe
        if nome_campanha not in data['campanhas']:
            await ctx.send(f"Campanha '{nome_campanha}' não encontrada.")
            return

        # Verifica se a senha está correta
        if data['campanhas'][nome_campanha]['senha'] != senha:
            await ctx.send('Senha incorreta.')
            return

        # Remove a campanha
        del data['campanhas'][nome_campanha]
        save_data(data)

        await ctx.send(f"Campanha '{nome_campanha}' excluída com sucesso!")

    except Exception as e:
        await ctx.send(f"Ocorreu um erro ao tentar excluir a campanha: {e}")


@bot.command()
async def editar(ctx, *, detalhes: str):
    """Edita os detalhes da campanha, se a senha estiver correta."""
    try:
        # Divide os detalhes fornecidos no comando
        detalhes_split = [d.strip() for d in detalhes.split('=')]

        if len(detalhes_split) != 5:
            await ctx.send("Formato incorreto. Use o formato: nome_da_campanha = senha = nova_descricao = novo_dia_da_semana = novo_participantes_maximos")
            return

        nome_campanha, senha, nova_descricao, novo_dia_da_semana, novo_participantes_maximos = detalhes_split

        data = load_data()

        # Verifica se a campanha existe
        if 'campanhas' not in data or nome_campanha not in data['campanhas']:
            await ctx.send("Campanha não encontrada.")
            return

        campanha = data['campanhas'][nome_campanha]

        # Verifica se a senha fornecida está correta
        if senha != campanha.get('senha', ''):
            await ctx.send("Senha incorreta!")
            return

        # Atualiza os detalhes da campanha
        campanha['descricao'] = nova_descricao
        campanha['dia_semana'] = novo_dia_da_semana
        campanha['participantes_maximos'] = int(novo_participantes_maximos)

        # Salva os dados atualizados
        save_data(data)
        await ctx.send(f"Campanha '{nome_campanha}' atualizada com sucesso!")

    except ValueError:
        await ctx.send("Número máximo de participantes deve ser um número inteiro.")
    except Exception as e:
        await ctx.send(f"Ocorreu um erro ao tentar editar a campanha: {e}")


bot.run(TOKEN)
